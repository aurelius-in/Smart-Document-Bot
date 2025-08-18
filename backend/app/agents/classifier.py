import re
from typing import Any, Dict, List, Optional

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

from .base import BaseAgent, Tool
from ..models.base import AgentResult, AgentType, DocumentType


class DocumentClassificationTool(Tool):
    """LLM-based document classification tool"""
    
    def __init__(self):
        super().__init__("classify", "Classify document type and domain using LLM")
    
    async def execute(self, text: str, **kwargs) -> Dict[str, Any]:
        """Classify document"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            prompt = f"""
Analyze this document text and classify it. Respond with JSON only.

DOCUMENT TEXT (first 1000 characters):
{text[:1000]}...

CLASSIFICATION TASK:
1. Determine document type from: contract, invoice, policy, regulation, compliance_report, legal_document, financial_statement, insurance_policy, medical_record, unknown
2. Identify domain: healthcare, finance, legal, insurance, government, technology, manufacturing, retail, other
3. Identify missing critical fields (list as array)
4. Provide confidence score (0.0-1.0)

Respond with JSON:
{{
    "document_type": "type",
    "domain": "domain", 
    "missing_fields": ["field1", "field2"],
    "confidence": 0.85,
    "reasoning": "brief explanation"
}}
"""
            
            response = await llm.agenerate([[HumanMessage(content=prompt)]])
            result_text = response.generations[0][0].text.strip()
            
            # Extract JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1]
            
            import json
            return json.loads(result_text)
            
        except Exception as e:
            return {
                "document_type": "unknown",
                "domain": "other",
                "missing_fields": [],
                "confidence": 0.0,
                "reasoning": f"Classification failed: {str(e)}"
            }


class FieldExtractionTool(Tool):
    """Extract key fields from document"""
    
    def __init__(self):
        super().__init__("extract_fields", "Extract key fields from document text")
    
    async def execute(self, text: str, doc_type: str, **kwargs) -> Dict[str, Any]:
        """Extract fields based on document type"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            field_mapping = {
                "contract": ["parties", "effective_date", "termination_date", "value", "obligations"],
                "invoice": ["invoice_number", "date", "amount", "vendor", "customer", "items"],
                "policy": ["policy_number", "effective_date", "coverage", "exclusions", "premium"],
                "regulation": ["regulation_number", "effective_date", "jurisdiction", "requirements"],
                "compliance_report": ["report_date", "compliance_status", "findings", "recommendations"],
                "legal_document": ["case_number", "filing_date", "parties", "relief_sought"],
                "financial_statement": ["period", "revenue", "expenses", "net_income", "assets"],
                "insurance_policy": ["policy_number", "insured", "coverage_amount", "premium", "term"],
                "medical_record": ["patient_id", "date", "diagnosis", "treatment", "provider"]
            }
            
            fields = field_mapping.get(doc_type, ["title", "date", "author"])
            
            prompt = f"""
Extract key fields from this {doc_type} document. Respond with JSON only.

DOCUMENT TEXT (first 1500 characters):
{text[:1500]}...

FIELDS TO EXTRACT: {fields}

For each field, provide:
- value: extracted value or null if not found
- confidence: 0.0-1.0 based on clarity
- location: approximate location in text

Respond with JSON:
{{
    "fields": {{
        "field_name": {{
            "value": "extracted_value",
            "confidence": 0.85,
            "location": "description"
        }}
    }},
    "overall_confidence": 0.8
}}
"""
            
            response = await llm.agenerate([[HumanMessage(content=prompt)]])
            result_text = response.generations[0][0].text.strip()
            
            # Extract JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1]
            
            import json
            return json.loads(result_text)
            
        except Exception as e:
            return {
                "fields": {},
                "overall_confidence": 0.0,
                "error": str(e)
            }


class ClassifierAgent(BaseAgent):
    """Agent responsible for document classification and field identification"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__("ClassifierAgent", AgentType.CLASSIFIER)
        self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
        
        # Add tools
        self.add_tool(DocumentClassificationTool())
        self.add_tool(FieldExtractionTool())
    
    async def run(self, goal: str, context: Dict[str, Any]) -> AgentResult:
        """Main classification process"""
        document = context.get("ingestion_result")
        if not document or not hasattr(document, 'content'):
            return AgentResult(
                output=None,
                rationale="No document content available from ingestion",
                confidence=0.0,
                next_suggested_action="Ensure document is ingested first"
            )
        
        try:
            # Classify document
            classify_tool = self.get_tool("classify")
            classification = await classify_tool.execute(text=document.content)
            
            # Extract fields
            extract_tool = self.get_tool("extract_fields")
            field_extraction = await extract_tool.execute(
                text=document.content,
                doc_type=classification.get("document_type", "unknown")
            )
            
            # Update document with classification
            document.doc_type = DocumentType(classification.get("document_type", "unknown"))
            document.metadata.update({
                "classification": classification,
                "field_extraction": field_extraction,
                "domain": classification.get("domain", "other"),
                "missing_fields": classification.get("missing_fields", [])
            })
            
            # Calculate overall confidence
            classification_confidence = classification.get("confidence", 0.0)
            field_confidence = field_extraction.get("overall_confidence", 0.0)
            overall_confidence = (classification_confidence + field_confidence) / 2
            
            # Generate rationale
            rationale = f"Classified as {classification.get('document_type', 'unknown')} ({classification.get('domain', 'other')} domain) with {len(field_extraction.get('fields', {}))} fields extracted. Missing: {', '.join(classification.get('missing_fields', []))}"
            
            return AgentResult(
                output=document,
                rationale=rationale,
                confidence=overall_confidence,
                next_suggested_action="Proceed to entity extraction" if overall_confidence > 0.6 else "Manual review recommended"
            )
            
        except Exception as e:
            return AgentResult(
                output=document,
                rationale=f"Classification failed: {str(e)}",
                confidence=0.0,
                next_suggested_action="Manual classification required"
            )
    
    def get_expected_fields(self, doc_type: str) -> List[str]:
        """Get expected fields for document type"""
        field_mapping = {
            "contract": ["parties", "effective_date", "termination_date", "value", "obligations"],
            "invoice": ["invoice_number", "date", "amount", "vendor", "customer", "items"],
            "policy": ["policy_number", "effective_date", "coverage", "exclusions", "premium"],
            "regulation": ["regulation_number", "effective_date", "jurisdiction", "requirements"],
            "compliance_report": ["report_date", "compliance_status", "findings", "recommendations"],
            "legal_document": ["case_number", "filing_date", "parties", "relief_sought"],
            "financial_statement": ["period", "revenue", "expenses", "net_income", "assets"],
            "insurance_policy": ["policy_number", "insured", "coverage_amount", "premium", "term"],
            "medical_record": ["patient_id", "date", "diagnosis", "treatment", "provider"]
        }
        return field_mapping.get(doc_type, ["title", "date", "author"])
