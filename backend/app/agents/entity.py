import re
from typing import Any, Dict, List, Optional, Tuple

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

from .base import BaseAgent, Tool
from ..models.base import AgentResult, AgentType, Entity


class NERTool(Tool):
    """Named Entity Recognition tool"""
    
    def __init__(self):
        super().__init__("ner", "Extract named entities from text")
    
    async def execute(self, text: str, **kwargs) -> List[Dict[str, Any]]:
        """Extract named entities"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            prompt = f"""
Extract named entities from this text. Respond with JSON only.

TEXT (first 2000 characters):
{text[:2000]}...

ENTITY TYPES TO EXTRACT:
- PERSON: Names of people
- ORGANIZATION: Company names, institutions
- DATE: Dates, deadlines, time periods
- MONEY: Monetary amounts, currency
- PERCENT: Percentages
- LOCATION: Addresses, cities, countries
- POLICY_REF: Policy numbers, regulation references
- CLAUSE: Legal clauses, contract terms
- OBLIGATION: Requirements, duties, responsibilities
- RISK: Risk factors, liabilities, penalties

For each entity, provide:
- text: the actual text
- label: entity type
- start: character position (approximate)
- end: character position (approximate)
- confidence: 0.0-1.0
- page: page number (estimate)

Respond with JSON:
{{
    "entities": [
        {{
            "text": "entity text",
            "label": "ENTITY_TYPE",
            "start": 123,
            "end": 135,
            "confidence": 0.9,
            "page": 1
        }}
    ],
    "overall_confidence": 0.85
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
            result = json.loads(result_text)
            return result.get("entities", [])
            
        except Exception as e:
            return []


class ClauseExtractionTool(Tool):
    """Extract legal clauses and contract terms"""
    
    def __init__(self):
        super().__init__("clause_extract", "Extract legal clauses and contract terms")
    
    async def execute(self, text: str, doc_type: str, **kwargs) -> List[Dict[str, Any]]:
        """Extract clauses based on document type"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            clause_types = {
                "contract": ["termination", "liability", "confidentiality", "payment", "governing_law"],
                "policy": ["coverage", "exclusions", "deductibles", "claims", "cancellation"],
                "regulation": ["requirements", "prohibitions", "penalties", "compliance", "reporting"],
                "legal_document": ["relief", "jurisdiction", "venue", "damages", "injunction"]
            }
            
            types = clause_types.get(doc_type, ["general", "obligation", "rights"])
            
            prompt = f"""
Extract legal clauses from this {doc_type} document. Respond with JSON only.

TEXT (first 2500 characters):
{text[:2500]}...

CLAUSE TYPES TO EXTRACT: {types}

For each clause, provide:
- text: the clause text
- type: clause type
- start: character position
- end: character position
- confidence: 0.0-1.0
- page: page number
- importance: high/medium/low

Respond with JSON:
{{
    "clauses": [
        {{
            "text": "clause text",
            "type": "clause_type",
            "start": 123,
            "end": 456,
            "confidence": 0.9,
            "page": 1,
            "importance": "high"
        }}
    ],
    "overall_confidence": 0.85
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
            result = json.loads(result_text)
            return result.get("clauses", [])
            
        except Exception as e:
            return []


class UncertaintyDetectionTool(Tool):
    """Detect uncertain or ambiguous entities"""
    
    def __init__(self):
        super().__init__("uncertainty_detect", "Detect uncertain or ambiguous entities")
    
    async def execute(self, entities: List[Dict[str, Any]], text: str, **kwargs) -> List[Dict[str, Any]]:
        """Detect uncertain entities"""
        uncertain_entities = []
        
        uncertainty_patterns = [
            r'\b(approximately|about|around|roughly|estimated)\b',
            r'\b(may|might|could|should|would)\b',
            r'\b(subject to|pending|conditional|tentative)\b',
            r'\b(TBD|TBA|to be determined|to be announced)\b'
        ]
        
        for entity in entities:
            entity_text = entity.get("text", "")
            confidence = entity.get("confidence", 0.0)
            
            # Check for uncertainty patterns
            is_uncertain = False
            uncertainty_reasons = []
            
            # Low confidence
            if confidence < 0.7:
                is_uncertain = True
                uncertainty_reasons.append("low_confidence")
            
            # Uncertainty patterns in text
            for pattern in uncertainty_patterns:
                if re.search(pattern, entity_text, re.IGNORECASE):
                    is_uncertain = True
                    uncertainty_reasons.append("uncertainty_pattern")
                    break
            
            # Ambiguous text
            if len(entity_text.strip()) < 3 or entity_text.lower() in ["the", "and", "or", "of", "in", "on"]:
                is_uncertain = True
                uncertainty_reasons.append("ambiguous_text")
            
            if is_uncertain:
                entity["uncertainty"] = {
                    "is_uncertain": True,
                    "reasons": uncertainty_reasons,
                    "suggested_action": "manual_review" if confidence < 0.5 else "verify"
                }
                uncertain_entities.append(entity)
        
        return uncertain_entities


class EntityAgent(BaseAgent):
    """Agent responsible for entity extraction and clause identification"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__("EntityAgent", AgentType.ENTITY)
        self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
        
        # Add tools
        self.add_tool(NERTool())
        self.add_tool(ClauseExtractionTool())
        self.add_tool(UncertaintyDetectionTool())
    
    async def run(self, goal: str, context: Dict[str, Any]) -> AgentResult:
        """Main entity extraction process"""
        document = context.get("classifier_result")
        if not document or not hasattr(document, 'content'):
            return AgentResult(
                output=None,
                rationale="No document content available from classification",
                confidence=0.0,
                next_suggested_action="Ensure document is classified first"
            )
        
        try:
            # Extract named entities
            ner_tool = self.get_tool("ner")
            entities = await ner_tool.execute(text=document.content)
            
            # Extract clauses
            clause_tool = self.get_tool("clause_extract")
            doc_type = document.doc_type.value if document.doc_type else "unknown"
            clauses = await clause_tool.execute(text=document.content, doc_type=doc_type)
            
            # Detect uncertainty
            uncertainty_tool = self.get_tool("uncertainty_detect")
            uncertain_entities = await uncertainty_tool.execute(
                entities=entities + clauses,
                text=document.content
            )
            
            # Convert to Entity objects
            entity_objects = []
            for entity_data in entities:
                entity = Entity(
                    text=entity_data.get("text", ""),
                    label=entity_data.get("label", "UNKNOWN"),
                    start=entity_data.get("start", 0),
                    end=entity_data.get("end", 0),
                    confidence=entity_data.get("confidence", 0.0),
                    page=entity_data.get("page", 1),
                    metadata=entity_data
                )
                entity_objects.append(entity)
            
            # Add clauses as entities
            for clause_data in clauses:
                entity = Entity(
                    text=clause_data.get("text", ""),
                    label=f"CLAUSE_{clause_data.get('type', 'GENERAL').upper()}",
                    start=clause_data.get("start", 0),
                    end=clause_data.get("end", 0),
                    confidence=clause_data.get("confidence", 0.0),
                    page=clause_data.get("page", 1),
                    metadata=clause_data
                )
                entity_objects.append(entity)
            
            # Calculate overall confidence
            total_entities = len(entity_objects)
            if total_entities == 0:
                overall_confidence = 0.0
            else:
                avg_confidence = sum(e.confidence for e in entity_objects) / total_entities
                uncertainty_penalty = len(uncertain_entities) / total_entities * 0.2
                overall_confidence = max(0.0, avg_confidence - uncertainty_penalty)
            
            # Update document metadata
            document.metadata.update({
                "entities": [e.dict() for e in entity_objects],
                "entity_count": len(entities),
                "clause_count": len(clauses),
                "uncertain_entities": len(uncertain_entities),
                "entity_extraction_confidence": overall_confidence
            })
            
            # Generate rationale
            rationale = f"Extracted {len(entities)} entities and {len(clauses)} clauses. {len(uncertain_entities)} entities flagged for review."
            
            next_action = "Proceed to risk assessment"
            if len(uncertain_entities) > len(entity_objects) * 0.3:  # More than 30% uncertain
                next_action = "Manual review recommended due to high uncertainty"
            
            return AgentResult(
                output=entity_objects,
                rationale=rationale,
                confidence=overall_confidence,
                next_suggested_action=next_action
            )
            
        except Exception as e:
            return AgentResult(
                output=[],
                rationale=f"Entity extraction failed: {str(e)}",
                confidence=0.0,
                next_suggested_action="Manual entity extraction required"
            )
    
    def get_entity_statistics(self, entities: List[Entity]) -> Dict[str, Any]:
        """Get statistics about extracted entities"""
        if not entities:
            return {"total": 0, "by_type": {}, "avg_confidence": 0.0}
        
        by_type = {}
        for entity in entities:
            label = entity.label
            if label not in by_type:
                by_type[label] = {"count": 0, "avg_confidence": 0.0, "total_confidence": 0.0}
            by_type[label]["count"] += 1
            by_type[label]["total_confidence"] += entity.confidence
        
        # Calculate averages
        for label in by_type:
            by_type[label]["avg_confidence"] = by_type[label]["total_confidence"] / by_type[label]["count"]
        
        return {
            "total": len(entities),
            "by_type": by_type,
            "avg_confidence": sum(e.confidence for e in entities) / len(entities)
        }
