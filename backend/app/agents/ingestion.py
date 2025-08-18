import re
from typing import Any, Dict, List, Optional

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

from .base import BaseAgent, Tool
from ..models.base import AgentResult, AgentType, Document


class OCRTool(Tool):
    """OCR tool for extracting text from images/PDFs"""
    
    def __init__(self):
        super().__init__("ocr", "Extract text from images using OCR")
    
    async def execute(self, file_path: str, **kwargs) -> str:
        """Execute OCR on file"""
        try:
            import pytesseract
            from PIL import Image
            from pdf2image import convert_from_path
            
            if file_path.lower().endswith('.pdf'):
                # Convert PDF to images
                pages = convert_from_path(file_path)
                text = ""
                for page in pages:
                    text += pytesseract.image_to_string(page) + "\n"
                return text
            else:
                # Direct image OCR
                image = Image.open(file_path)
                return pytesseract.image_to_string(image)
        except Exception as e:
            return f"OCR Error: {str(e)}"


class PDFExtractTool(Tool):
    """Native PDF text extraction tool"""
    
    def __init__(self):
        super().__init__("pdf_extract", "Extract text from PDF using native methods")
    
    async def execute(self, file_path: str, **kwargs) -> str:
        """Extract text from PDF"""
        try:
            import PyPDF2
            
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            return f"PDF Extraction Error: {str(e)}"


class TextNormalizationTool(Tool):
    """Text normalization and cleaning tool"""
    
    def __init__(self):
        super().__init__("normalize", "Normalize and clean extracted text")
    
    async def execute(self, text: str, **kwargs) -> str:
        """Normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR issues
        text = re.sub(r'[|]', 'I', text)  # Common OCR mistake
        text = re.sub(r'[0]', 'O', text)  # Another common mistake
        
        # Remove page numbers and headers/footers
        text = re.sub(r'Page \d+', '', text)
        text = re.sub(r'\d+ of \d+', '', text)
        
        return text.strip()


class IngestionAgent(BaseAgent):
    """Agent responsible for document ingestion and text extraction"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__("IngestionAgent", AgentType.INGESTION)
        self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
        
        # Add tools
        self.add_tool(OCRTool())
        self.add_tool(PDFExtractTool())
        self.add_tool(TextNormalizationTool())
    
    async def choose_extraction_strategy(self, file_path: str, file_info: Dict[str, Any]) -> str:
        """Use LLM to choose the best extraction strategy"""
        prompt = f"""
You are an expert document processing agent. Choose the best text extraction strategy for this file.

FILE INFO:
- Path: {file_path}
- Size: {file_info.get('size', 'unknown')} bytes
- Type: {file_info.get('type', 'unknown')}

EXTRACTION OPTIONS:
1. pdf_extract: Native PDF text extraction (fast, good for text-based PDFs)
2. ocr: Optical Character Recognition (slower, good for scanned documents)

Choose the strategy based on:
- File type (PDF vs image)
- Whether it's likely scanned or text-based
- File size (larger files might be scanned)

Respond with just the tool name: "pdf_extract" or "ocr"
"""
        
        try:
            response = await self.llm.agenerate([[HumanMessage(content=prompt)]])
            strategy = response.generations[0][0].text.strip().lower()
            
            if strategy in ["pdf_extract", "ocr"]:
                return strategy
            else:
                # Default to PDF extract for PDFs, OCR for others
                return "pdf_extract" if file_path.lower().endswith('.pdf') else "ocr"
        except Exception:
            # Fallback strategy
            return "pdf_extract" if file_path.lower().endswith('.pdf') else "ocr"
    
    async def run(self, goal: str, context: Dict[str, Any]) -> AgentResult:
        """Main ingestion process"""
        file_path = context.get("file_path")
        if not file_path:
            return AgentResult(
                output=None,
                rationale="No file path provided in context",
                confidence=0.0,
                next_suggested_action="Provide file_path in context"
            )
        
        try:
            # Get file info
            import os
            file_info = {
                "size": os.path.getsize(file_path),
                "type": os.path.splitext(file_path)[1].lower()
            }
            
            # Choose extraction strategy
            strategy = await self.choose_extraction_strategy(file_path, file_info)
            
            # Extract text
            if strategy == "pdf_extract":
                tool = self.get_tool("pdf_extract")
                raw_text = await tool.execute(file_path=file_path)
            else:
                tool = self.get_tool("ocr")
                raw_text = await tool.execute(file_path=file_path)
            
            # Check if extraction was successful
            if raw_text.startswith("OCR Error") or raw_text.startswith("PDF Extraction Error"):
                # Try fallback strategy
                fallback_strategy = "ocr" if strategy == "pdf_extract" else "pdf_extract"
                fallback_tool = self.get_tool(fallback_strategy)
                raw_text = await fallback_tool.execute(file_path=file_path)
                
                if raw_text.startswith("OCR Error") or raw_text.startswith("PDF Extraction Error"):
                    return AgentResult(
                        output=None,
                        rationale=f"Both {strategy} and {fallback_strategy} failed",
                        confidence=0.0,
                        next_suggested_action="Manual review required"
                    )
            
            # Normalize text
            normalize_tool = self.get_tool("normalize")
            normalized_text = await normalize_tool.execute(text=raw_text)
            
            # Create document object
            document = Document(
                filename=os.path.basename(file_path),
                content=normalized_text,
                metadata={
                    "extraction_strategy": strategy,
                    "file_size": file_info["size"],
                    "original_length": len(raw_text),
                    "normalized_length": len(normalized_text)
                }
            )
            
            # Calculate confidence based on text quality
            confidence = self._calculate_confidence(normalized_text, strategy)
            
            return AgentResult(
                output=document,
                rationale=f"Successfully extracted text using {strategy} strategy. Extracted {len(normalized_text)} characters.",
                confidence=confidence,
                next_suggested_action="Proceed to classification"
            )
            
        except Exception as e:
            return AgentResult(
                output=None,
                rationale=f"Ingestion failed: {str(e)}",
                confidence=0.0,
                next_suggested_action="Check file accessibility and format"
            )
    
    def _calculate_confidence(self, text: str, strategy: str) -> float:
        """Calculate confidence based on text quality"""
        if not text or len(text.strip()) < 10:
            return 0.0
        
        # Base confidence
        confidence = 0.7 if strategy == "pdf_extract" else 0.6
        
        # Adjust based on text quality
        word_count = len(text.split())
        if word_count > 100:
            confidence += 0.2
        elif word_count > 50:
            confidence += 0.1
        
        # Check for common OCR artifacts
        ocr_artifacts = len(re.findall(r'[|]', text))  # Common OCR mistake
        if ocr_artifacts > 0:
            confidence -= min(0.1, ocr_artifacts / 100)
        
        return min(1.0, max(0.0, confidence))
