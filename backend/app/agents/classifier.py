import json
from typing import Any, Dict, List, Optional
from datetime import datetime

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from .base import BaseAgent, Tool
from ..models.base import AgentResult, AgentType, Document, DocumentType


class DocumentClassificationTool(Tool):
    """Tool for classifying documents using LLM"""
    
    def __init__(self):
        super().__init__("classify", "Classify document type and domain using LLM")
    
    async def execute(self, content: str, **kwargs) -> Dict[str, Any]:
        """Classify document content"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            system_prompt = """You are an expert document classifier for regulatory and business documents. 
            Analyze the document content and classify it into one of the following types:
            
            - contract: Legal agreements, contracts, terms of service
            - invoice: Bills, invoices, payment requests
            - policy: Company policies, procedures, guidelines
            - regulation: Government regulations, compliance documents
            - compliance_report: Audit reports, compliance assessments
            - legal_document: Legal filings, court documents, legal correspondence
            - financial_statement: Financial reports, balance sheets, income statements
            - insurance_policy: Insurance documents, coverage details
            - medical_record: Medical documents, health records
            - unknown: Cannot determine type
            
            Also identify the domain (e.g., legal, financial, healthcare, technology, etc.)
            
            Respond with JSON:
            {
                "document_type": "type",
                "domain": "domain",
                "confidence": 0.95,
                "reasoning": "explanation",
                "key_indicators": ["indicator1", "indicator2"]
            }
            """
            
            user_prompt = f"Classify this document content:\n\n{content[:2000]}..."
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await llm.agenerate([messages])
            result_text = response.generations[0][0].text.strip()
            
            # Extract JSON from response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1]
            
            result = json.loads(result_text)
            return result
            
        except Exception as e:
            return {
                "document_type": "unknown",
                "domain": "unknown",
                "confidence": 0.0,
                "reasoning": f"Classification failed: {str(e)}",
                "key_indicators": []
            }


class ContentAnalysisTool(Tool):
    """Tool for analyzing document content structure"""
    
    def __init__(self):
        super().__init__("analyze_content", "Analyze document content structure and characteristics")
    
    async def execute(self, content: str, **kwargs) -> Dict[str, Any]:
        """Analyze content structure"""
        import re
        analysis = {
            "word_count": len(content.split()),
            "character_count": len(content),
            "paragraph_count": len([p for p in content.split('\n\n') if p.strip()]),
            "has_numbers": any(char.isdigit() for char in content),
            "has_dates": self._extract_dates(content),
            "has_legal_terms": self._check_legal_terms(content),
            "has_financial_terms": self._check_financial_terms(content),
            "structure_score": self._calculate_structure_score(content)
        }
        
        return analysis
    
    def _extract_dates(self, content: str) -> List[str]:
        """Extract dates from content"""
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',
            r'\d{4}-\d{2}-\d{2}',
            r'\w+ \d{1,2},? \d{4}'
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, content))
        
        return dates[:5]  # Limit to first 5 dates
    
    def _check_legal_terms(self, content: str) -> List[str]:
        """Check for legal terms"""
        legal_terms = [
            "contract", "agreement", "terms", "conditions", "liability",
            "jurisdiction", "governing law", "party", "breach", "termination",
            "amendment", "warranty", "indemnification", "force majeure"
        ]
        
        found_terms = []
        content_lower = content.lower()
        for term in legal_terms:
            if term in content_lower:
                found_terms.append(term)
        
        return found_terms
    
    def _check_financial_terms(self, content: str) -> List[str]:
        """Check for financial terms"""
        financial_terms = [
            "payment", "amount", "currency", "invoice", "balance",
            "total", "due", "account", "transaction", "fee",
            "price", "cost", "revenue", "expense", "budget"
        ]
        
        found_terms = []
        content_lower = content.lower()
        for term in financial_terms:
            if term in content_lower:
                found_terms.append(term)
        
        return found_terms
    
    def _calculate_structure_score(self, content: str) -> float:
        """Calculate document structure score"""
        score = 0.0
        
        # Check for headers
        lines = content.split('\n')
        header_count = sum(1 for line in lines if line.strip().isupper() and len(line.strip()) < 100)
        score += min(0.3, header_count * 0.1)
        
        # Check for numbered sections
        numbered_sections = sum(1 for line in lines if re.match(r'^\d+\.', line.strip()))
        score += min(0.2, numbered_sections * 0.05)
        
        # Check for paragraphs
        paragraphs = len([p for p in content.split('\n\n') if p.strip()])
        score += min(0.2, paragraphs * 0.01)
        
        # Check for consistent formatting
        if len(content) > 500:
            score += 0.3
        
        return min(1.0, score)


class ClassifierAgent(BaseAgent):
    """Agent responsible for document classification and type determination"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__("ClassifierAgent", AgentType.CLASSIFIER)
        self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
        
        # Add tools
        self.add_tool(DocumentClassificationTool())
        self.add_tool(ContentAnalysisTool())
    
    async def run(self, goal: str, context: Dict[str, Any]) -> AgentResult:
        """Main classification process"""
        document = context.get("document")
        if not document:
            return AgentResult(
                output=None,
                rationale="No document provided in context",
                confidence=0.0,
                next_suggested_action="Provide document in context"
            )
        
        try:
            # Analyze content structure
            content_analysis_tool = self.get_tool("analyze_content")
            content_analysis = await content_analysis_tool.execute(content=document.content)
            
            # Classify document
            classification_tool = self.get_tool("classify")
            classification = await classification_tool.execute(content=document.content)
            
            # Update document with classification results
            document.doc_type = DocumentType(classification["document_type"])
            document.metadata.update({
                "classification": classification,
                "content_analysis": content_analysis,
                "classified_at": datetime.utcnow().isoformat()
            })
            
            # Calculate overall confidence
            confidence = self._calculate_confidence(classification, content_analysis)
            
            return AgentResult(
                output=document,
                rationale=f"Classified as {classification['document_type']} in {classification['domain']} domain. {classification['reasoning']}",
                confidence=confidence,
                next_suggested_action="Proceed to entity extraction",
                metadata={
                    "classification": classification,
                    "content_analysis": content_analysis
                }
            )
            
        except Exception as e:
            return AgentResult(
                output=None,
                rationale=f"Classification failed: {str(e)}",
                confidence=0.0,
                next_suggested_action="Manual classification required"
            )
    
    def _calculate_confidence(self, classification: Dict[str, Any], content_analysis: Dict[str, Any]) -> float:
        """Calculate confidence based on classification and content analysis"""
        base_confidence = classification.get("confidence", 0.5)
        
        # Adjust based on content analysis
        adjustments = 0.0
        
        # Structure score adjustment
        structure_score = content_analysis.get("structure_score", 0.0)
        adjustments += structure_score * 0.2
        
        # Legal terms adjustment
        legal_terms = content_analysis.get("has_legal_terms", [])
        if classification["document_type"] == "contract" and legal_terms:
            adjustments += min(0.2, len(legal_terms) * 0.05)
        
        # Financial terms adjustment
        financial_terms = content_analysis.get("has_financial_terms", [])
        if classification["document_type"] == "invoice" and financial_terms:
            adjustments += min(0.2, len(financial_terms) * 0.05)
        
        # Word count adjustment
        word_count = content_analysis.get("word_count", 0)
        if word_count > 100:
            adjustments += 0.1
        
        # Date presence adjustment
        if content_analysis.get("has_dates"):
            adjustments += 0.1
        
        final_confidence = base_confidence + adjustments
        return min(1.0, max(0.0, final_confidence))
