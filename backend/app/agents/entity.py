import json
import re
from typing import Any, Dict, List, Optional
from datetime import datetime

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from .base import BaseAgent, Tool
from ..models.base import AgentResult, AgentType, Document, Entity


class NamedEntityRecognitionTool(Tool):
    """Tool for extracting named entities using LLM"""
    
    def __init__(self):
        super().__init__("ner", "Extract named entities using LLM-based NER")
    
    async def execute(self, content: str, doc_type: str, **kwargs) -> List[Dict[str, Any]]:
        """Extract named entities from document content"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            # Define entity types based on document type
            entity_types = self._get_entity_types(doc_type)
            
            system_prompt = f"""You are an expert named entity recognition system for {doc_type} documents.
            Extract all named entities from the document content.
            
            ENTITY TYPES TO EXTRACT: {', '.join(entity_types)}
            
            For each entity found, provide:
            - text: The exact text of the entity
            - label: The entity type
            - start: Character position where entity starts
            - end: Character position where entity ends
            - confidence: Confidence score (0.0-1.0)
            
            Respond with JSON array:
            [
                {{
                    "text": "entity text",
                    "label": "entity_type",
                    "start": 123,
                    "end": 135,
                    "confidence": 0.95
                }}
            ]
            """
            
            user_prompt = f"Extract entities from this {doc_type} document:\n\n{content[:3000]}..."
            
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
            
            entities = json.loads(result_text)
            
            # Validate and clean entities
            cleaned_entities = []
            for entity in entities:
                if self._validate_entity(entity, content):
                    cleaned_entities.append(entity)
            
            return cleaned_entities
            
        except Exception as e:
            return []
    
    def _get_entity_types(self, doc_type: str) -> List[str]:
        """Get entity types based on document type"""
        base_types = ["PERSON", "ORGANIZATION", "DATE", "MONEY", "LOCATION"]
        
        type_mapping = {
            "contract": base_types + ["PARTY", "EFFECTIVE_DATE", "TERMINATION_DATE", "AMOUNT", "JURISDICTION"],
            "invoice": base_types + ["INVOICE_NUMBER", "VENDOR", "CUSTOMER", "DUE_DATE", "TAX_AMOUNT"],
            "policy": base_types + ["POLICY_NUMBER", "INSURED", "COVERAGE_TYPE", "PREMIUM", "EFFECTIVE_DATE"],
            "regulation": base_types + ["REGULATION_NUMBER", "JURISDICTION", "EFFECTIVE_DATE", "COMPLIANCE_DEADLINE"],
            "financial_statement": base_types + ["PERIOD", "REVENUE", "EXPENSE", "ASSET", "LIABILITY"],
            "medical_record": base_types + ["PATIENT_ID", "DIAGNOSIS", "TREATMENT", "MEDICATION", "PROVIDER"]
        }
        
        return type_mapping.get(doc_type, base_types)
    
    def _validate_entity(self, entity: Dict[str, Any], content: str) -> bool:
        """Validate extracted entity"""
        required_fields = ["text", "label", "start", "end", "confidence"]
        
        # Check required fields
        for field in required_fields:
            if field not in entity:
                return False
        
        # Validate text matches content
        start = entity.get("start", 0)
        end = entity.get("end", 0)
        if start >= len(content) or end > len(content) or start >= end:
            return False
        
        extracted_text = content[start:end]
        if extracted_text != entity["text"]:
            return False
        
        # Validate confidence
        confidence = entity.get("confidence", 0)
        if not (0.0 <= confidence <= 1.0):
            return False
        
        return True


class ClauseExtractionTool(Tool):
    """Tool for extracting legal clauses and key sections"""
    
    def __init__(self):
        super().__init__("extract_clauses", "Extract legal clauses and key sections from documents")
    
    async def execute(self, content: str, doc_type: str, **kwargs) -> List[Dict[str, Any]]:
        """Extract clauses and key sections"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            clause_types = self._get_clause_types(doc_type)
            
            system_prompt = f"""You are an expert legal document analyzer. Extract key clauses and sections from this {doc_type} document.
            
            CLAUSE TYPES TO EXTRACT: {', '.join(clause_types)}
            
            For each clause found, provide:
            - title: Clause title or section name
            - content: The full clause text
            - type: Type of clause
            - start: Character position where clause starts
            - end: Character position where clause ends
            - importance: High/Medium/Low importance
            
            Respond with JSON array:
            [
                {{
                    "title": "clause title",
                    "content": "full clause text",
                    "type": "clause_type",
                    "start": 123,
                    "end": 456,
                    "importance": "High"
                }}
            ]
            """
            
            user_prompt = f"Extract clauses from this {doc_type} document:\n\n{content[:4000]}..."
            
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
            
            clauses = json.loads(result_text)
            
            # Validate clauses
            valid_clauses = []
            for clause in clauses:
                if self._validate_clause(clause, content):
                    valid_clauses.append(clause)
            
            return valid_clauses
            
        except Exception as e:
            return []
    
    def _get_clause_types(self, doc_type: str) -> List[str]:
        """Get clause types based on document type"""
        base_types = ["GENERAL", "DEFINITIONS", "TERMINATION", "AMENDMENT"]
        
        type_mapping = {
            "contract": base_types + ["PAYMENT_TERMS", "LIABILITY", "INDEMNIFICATION", "FORCE_MAJEURE", "GOVERNING_LAW"],
            "policy": base_types + ["COVERAGE", "EXCLUSIONS", "CLAIMS_PROCEDURE", "PREMIUM_PAYMENT"],
            "regulation": base_types + ["COMPLIANCE_REQUIREMENTS", "PENALTIES", "ENFORCEMENT", "EXEMPTIONS"],
            "legal_document": base_types + ["RELIEF_SOUGHT", "JURISDICTION", "SERVICE_OF_PROCESS"]
        }
        
        return type_mapping.get(doc_type, base_types)
    
    def _validate_clause(self, clause: Dict[str, Any], content: str) -> bool:
        """Validate extracted clause"""
        required_fields = ["title", "content", "type", "start", "end", "importance"]
        
        # Check required fields
        for field in required_fields:
            if field not in clause:
                return False
        
        # Validate content matches
        start = clause.get("start", 0)
        end = clause.get("end", 0)
        if start >= len(content) or end > len(content) or start >= end:
            return False
        
        extracted_content = content[start:end]
        if not clause["content"].strip() in extracted_content:
            return False
        
        # Validate importance
        importance = clause.get("importance", "").upper()
        if importance not in ["HIGH", "MEDIUM", "LOW"]:
            return False
        
        return True


class KeyInformationExtractionTool(Tool):
    """Tool for extracting key information and metadata"""
    
    def __init__(self):
        super().__init__("extract_key_info", "Extract key information and metadata from documents")
    
    async def execute(self, content: str, doc_type: str, **kwargs) -> Dict[str, Any]:
        """Extract key information"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            info_types = self._get_info_types(doc_type)
            
            system_prompt = f"""You are an expert document analyzer. Extract key information from this {doc_type} document.
            
            INFORMATION TYPES TO EXTRACT: {', '.join(info_types)}
            
            For each piece of information, provide:
            - type: Information type
            - value: Extracted value
            - confidence: Confidence score (0.0-1.0)
            - location: Where in document (page/section)
            
            Respond with JSON:
            {{
                "key_information": [
                    {{
                        "type": "info_type",
                        "value": "extracted_value",
                        "confidence": 0.95,
                        "location": "page 1, section 2"
                    }}
                ],
                "summary": "Brief summary of key findings",
                "total_items": 5
            }}
            """
            
            user_prompt = f"Extract key information from this {doc_type} document:\n\n{content[:3000]}..."
            
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
            
            return json.loads(result_text)
            
        except Exception as e:
            return {
                "key_information": [],
                "summary": f"Extraction failed: {str(e)}",
                "total_items": 0
            }
    
    def _get_info_types(self, doc_type: str) -> List[str]:
        """Get information types based on document type"""
        base_types = ["TITLE", "DATE", "AUTHOR", "VERSION"]
        
        type_mapping = {
            "contract": base_types + ["PARTIES", "EFFECTIVE_DATE", "TERM", "VALUE", "JURISDICTION"],
            "invoice": base_types + ["INVOICE_NUMBER", "DUE_DATE", "TOTAL_AMOUNT", "VENDOR", "CUSTOMER"],
            "policy": base_types + ["POLICY_NUMBER", "INSURED", "COVERAGE_AMOUNT", "PREMIUM", "TERM"],
            "regulation": base_types + ["REGULATION_NUMBER", "JURISDICTION", "EFFECTIVE_DATE", "COMPLIANCE_DEADLINE"],
            "financial_statement": base_types + ["PERIOD", "REVENUE", "NET_INCOME", "TOTAL_ASSETS", "TOTAL_LIABILITIES"]
        }
        
        return type_mapping.get(doc_type, base_types)


class EntityAgent(BaseAgent):
    """Agent responsible for entity extraction and information extraction"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__("EntityAgent", AgentType.ENTITY)
        self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
        
        # Add tools
        self.add_tool(NamedEntityRecognitionTool())
        self.add_tool(ClauseExtractionTool())
        self.add_tool(KeyInformationExtractionTool())
    
    async def run(self, goal: str, context: Dict[str, Any]) -> AgentResult:
        """Main entity extraction process"""
        document = context.get("document")
        if not document:
            return AgentResult(
                output=None,
                rationale="No document provided in context",
                confidence=0.0,
                next_suggested_action="Provide document in context"
            )
        
        try:
            doc_type = document.doc_type.value if document.doc_type else "unknown"
            
            # Extract named entities
            ner_tool = self.get_tool("ner")
            entities = await ner_tool.execute(content=document.content, doc_type=doc_type)
            
            # Extract clauses
            clause_tool = self.get_tool("extract_clauses")
            clauses = await clause_tool.execute(content=document.content, doc_type=doc_type)
            
            # Extract key information
            key_info_tool = self.get_tool("extract_key_info")
            key_info = await key_info_tool.execute(content=document.content, doc_type=doc_type)
            
            # Convert entities to Entity objects
            entity_objects = []
            for entity in entities:
                entity_obj = Entity(
                    text=entity["text"],
                    label=entity["label"],
                    start=entity["start"],
                    end=entity["end"],
                    confidence=entity["confidence"],
                    page=1,  # Default to page 1 for now
                    metadata={
                        "extraction_method": "llm_ner",
                        "extracted_at": datetime.utcnow().isoformat()
                    }
                )
                entity_objects.append(entity_obj)
            
            # Update document metadata
            document.metadata.update({
                "entities": [entity.dict() for entity in entity_objects],
                "clauses": clauses,
                "key_information": key_info,
                "entity_extraction": {
                    "total_entities": len(entity_objects),
                    "total_clauses": len(clauses),
                    "key_info_items": key_info.get("total_items", 0),
                    "extracted_at": datetime.utcnow().isoformat()
                }
            })
            
            # Calculate confidence
            confidence = self._calculate_confidence(entities, clauses, key_info)
            
            return AgentResult(
                output=document,
                rationale=f"Extracted {len(entity_objects)} entities, {len(clauses)} clauses, and {key_info.get('total_items', 0)} key information items from {doc_type} document.",
                confidence=confidence,
                next_suggested_action="Proceed to risk assessment",
                metadata={
                    "entities": entities,
                    "clauses": clauses,
                    "key_information": key_info
                }
            )
            
        except Exception as e:
            return AgentResult(
                output=None,
                rationale=f"Entity extraction failed: {str(e)}",
                confidence=0.0,
                next_suggested_action="Manual entity extraction required"
            )
    
    def _calculate_confidence(self, entities: List[Dict], clauses: List[Dict], key_info: Dict) -> float:
        """Calculate confidence based on extraction results"""
        confidence = 0.5  # Base confidence
        
        # Entity confidence
        if entities:
            avg_entity_confidence = sum(e.get("confidence", 0) for e in entities) / len(entities)
            confidence += avg_entity_confidence * 0.3
        
        # Clause confidence
        if clauses:
            clause_confidence = min(1.0, len(clauses) * 0.1)  # More clauses = higher confidence
            confidence += clause_confidence * 0.2
        
        # Key information confidence
        key_info_items = key_info.get("total_items", 0)
        if key_info_items > 0:
            key_info_confidence = min(1.0, key_info_items * 0.05)
            confidence += key_info_confidence * 0.2
        
        # Content length adjustment
        if len(entities) > 10:
            confidence += 0.1
        
        return min(1.0, max(0.0, confidence))
