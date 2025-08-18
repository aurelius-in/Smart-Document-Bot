import json
import re
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from .base import BaseAgent, Tool
from ..models.base import AgentResult, AgentType, Document


class ComparisonType(Enum):
    """Comparison type enumeration"""
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"
    COMPLIANCE = "compliance"
    RISK = "risk"
    ENTITY = "entity"


class SemanticComparisonTool(Tool):
    """Tool for semantic document comparison"""
    
    def __init__(self):
        super().__init__("semantic_compare", "Compare documents semantically")
    
    async def execute(self, doc_a_content: str, doc_b_content: str, doc_a_type: str, doc_b_type: str, **kwargs) -> Dict[str, Any]:
        """Compare documents semantically"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            system_prompt = f"""You are an expert document comparison analyst. Compare these two documents semantically.
            
            DOCUMENT A TYPE: {doc_a_type}
            DOCUMENT B TYPE: {doc_b_type}
            
            For each semantic difference found, provide:
            - difference_type: Type of semantic difference (content, meaning, intent, etc.)
            - description: Detailed description of the difference
            - severity: LOW/MEDIUM/HIGH/CRITICAL
            - impact: Impact of this difference
            - location_a: Where in document A this appears
            - location_b: Where in document B this appears
            - confidence: Confidence in this analysis (0.0-1.0)
            
            Also provide:
            - overall_similarity: Overall similarity score (0.0-1.0)
            - key_differences: Summary of key differences
            - semantic_analysis: Overall semantic analysis
            
            Respond with JSON:
            {{
                "semantic_differences": [
                    {{
                        "difference_type": "content_change",
                        "description": "detailed description",
                        "severity": "MEDIUM",
                        "impact": "impact description",
                        "location_a": "section/page reference",
                        "location_b": "section/page reference",
                        "confidence": 0.9
                    }}
                ],
                "overall_similarity": 0.75,
                "key_differences": "summary of key differences",
                "semantic_analysis": "overall semantic analysis"
            }}
            """
            
            user_prompt = f"Compare these documents semantically:\n\nDOCUMENT A ({doc_a_type}):\n{doc_a_content[:2000]}...\n\nDOCUMENT B ({doc_b_type}):\n{doc_b_content[:2000]}..."
            
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
                "semantic_differences": [],
                "overall_similarity": 0.0,
                "key_differences": f"Semantic comparison failed: {str(e)}",
                "semantic_analysis": "Unable to perform semantic analysis"
            }


class StructuralComparisonTool(Tool):
    """Tool for structural document comparison"""
    
    def __init__(self):
        super().__init__("structural_compare", "Compare document structures")
    
    async def execute(self, doc_a_content: str, doc_b_content: str, doc_a_type: str, doc_b_type: str, **kwargs) -> Dict[str, Any]:
        """Compare document structures"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            system_prompt = f"""You are an expert document structure analyst. Compare the structure of these two documents.
            
            DOCUMENT A TYPE: {doc_a_type}
            DOCUMENT B TYPE: {doc_b_type}
            
            Analyze:
            - Section organization
            - Headers and formatting
            - Content flow
            - Document length and complexity
            - Structural patterns
            
            For each structural difference, provide:
            - difference_type: Type of structural difference
            - description: Detailed description
            - significance: LOW/MEDIUM/HIGH
            - impact: Impact on document effectiveness
            - confidence: Confidence in analysis (0.0-1.0)
            
            Also provide:
            - structure_similarity: Structural similarity score (0.0-1.0)
            - structural_analysis: Overall structural analysis
            
            Respond with JSON:
            {{
                "structural_differences": [
                    {{
                        "difference_type": "section_organization",
                        "description": "detailed description",
                        "significance": "MEDIUM",
                        "impact": "impact description",
                        "confidence": 0.9
                    }}
                ],
                "structure_similarity": 0.8,
                "structural_analysis": "overall structural analysis"
            }}
            """
            
            user_prompt = f"Compare the structure of these documents:\n\nDOCUMENT A ({doc_a_type}):\n{doc_a_content[:2000]}...\n\nDOCUMENT B ({doc_b_type}):\n{doc_b_content[:2000]}..."
            
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
                "structural_differences": [],
                "structure_similarity": 0.0,
                "structural_analysis": f"Structural comparison failed: {str(e)}"
            }


class ComplianceComparisonTool(Tool):
    """Tool for compliance comparison"""
    
    def __init__(self):
        super().__init__("compliance_compare", "Compare compliance aspects")
    
    async def execute(self, doc_a_content: str, doc_b_content: str, doc_a_risk: Dict, doc_b_risk: Dict, **kwargs) -> Dict[str, Any]:
        """Compare compliance aspects"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            system_prompt = """You are an expert compliance analyst. Compare the compliance aspects of these two documents.
            
            For each compliance difference, provide:
            - compliance_area: Specific compliance area
            - difference_type: Type of compliance difference
            - description: Detailed description
            - risk_impact: Impact on compliance risk
            - recommendation: Compliance recommendation
            - severity: LOW/MEDIUM/HIGH/CRITICAL
            - confidence: Confidence in analysis (0.0-1.0)
            
            Also provide:
            - compliance_impact: Overall compliance impact assessment
            - risk_delta: Change in compliance risk
            
            Respond with JSON:
            {
                "compliance_differences": [
                    {
                        "compliance_area": "data_privacy",
                        "difference_type": "regulation_change",
                        "description": "detailed description",
                        "risk_impact": "impact description",
                        "recommendation": "compliance recommendation",
                        "severity": "HIGH",
                        "confidence": 0.9
                    }
                ],
                "compliance_impact": "overall compliance impact",
                "risk_delta": "change in compliance risk"
            }
            """
            
            # Include risk assessment context
            risk_context = f"\n\nDOCUMENT A RISK ASSESSMENT:\n{json.dumps(doc_a_risk, indent=2)}\n\nDOCUMENT B RISK ASSESSMENT:\n{json.dumps(doc_b_risk, indent=2)}"
            
            user_prompt = f"Compare compliance aspects of these documents:{risk_context}\n\nDOCUMENT A:\n{doc_a_content[:1500]}...\n\nDOCUMENT B:\n{doc_b_content[:1500]}..."
            
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
                "compliance_differences": [],
                "compliance_impact": f"Compliance comparison failed: {str(e)}",
                "risk_delta": "Unable to assess risk delta"
            }


class EntityComparisonTool(Tool):
    """Tool for entity comparison"""
    
    def __init__(self):
        super().__init__("entity_compare", "Compare extracted entities")
    
    async def execute(self, doc_a_entities: List[Dict], doc_b_entities: List[Dict], **kwargs) -> Dict[str, Any]:
        """Compare extracted entities"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            system_prompt = """You are an expert entity comparison analyst. Compare the entities extracted from two documents.
            
            For each entity difference, provide:
            - entity_type: Type of entity (PERSON, ORGANIZATION, DATE, etc.)
            - difference_type: Type of difference (added, removed, changed)
            - entity_a: Entity from document A
            - entity_b: Entity from document B (if applicable)
            - significance: LOW/MEDIUM/HIGH
            - impact: Impact of this entity difference
            - confidence: Confidence in analysis (0.0-1.0)
            
            Also provide:
            - entity_similarity: Entity similarity score (0.0-1.0)
            - entity_analysis: Overall entity analysis
            
            Respond with JSON:
            {
                "entity_differences": [
                    {
                        "entity_type": "PERSON",
                        "difference_type": "added",
                        "entity_a": "John Doe",
                        "entity_b": null,
                        "significance": "MEDIUM",
                        "impact": "impact description",
                        "confidence": 0.9
                    }
                ],
                "entity_similarity": 0.7,
                "entity_analysis": "overall entity analysis"
            }
            """
            
            user_prompt = f"Compare these entities:\n\nDOCUMENT A ENTITIES:\n{json.dumps(doc_a_entities[:20], indent=2)}\n\nDOCUMENT B ENTITIES:\n{json.dumps(doc_b_entities[:20], indent=2)}"
            
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
                "entity_differences": [],
                "entity_similarity": 0.0,
                "entity_analysis": f"Entity comparison failed: {str(e)}"
            }


class ComparisonSummaryTool(Tool):
    """Tool for generating comparison summary"""
    
    def __init__(self):
        super().__init__("generate_summary", "Generate comparison summary")
    
    async def execute(self, semantic_result: Dict, structural_result: Dict, compliance_result: Dict, entity_result: Dict, **kwargs) -> Dict[str, Any]:
        """Generate comprehensive comparison summary"""
        try:
            # Calculate overall similarity
            similarities = [
                semantic_result.get("overall_similarity", 0.0),
                structural_result.get("structure_similarity", 0.0),
                entity_result.get("entity_similarity", 0.0)
            ]
            
            # Weighted average (semantic gets higher weight)
            weights = [0.5, 0.3, 0.2]
            overall_similarity = sum(s * w for s, w in zip(similarities, weights))
            
            # Count differences by severity
            all_differences = []
            
            semantic_diffs = semantic_result.get("semantic_differences", [])
            for diff in semantic_diffs:
                diff["category"] = "semantic"
                all_differences.append(diff)
            
            structural_diffs = structural_result.get("structural_differences", [])
            for diff in structural_diffs:
                diff["category"] = "structural"
                all_differences.append(diff)
            
            compliance_diffs = compliance_result.get("compliance_differences", [])
            for diff in compliance_diffs:
                diff["category"] = "compliance"
                all_differences.append(diff)
            
            entity_diffs = entity_result.get("entity_differences", [])
            for diff in entity_diffs:
                diff["category"] = "entity"
                all_differences.append(diff)
            
            # Severity distribution
            severity_dist = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
            for diff in all_differences:
                severity = diff.get("severity", "LOW")
                severity_dist[severity] += 1
            
            # Category distribution
            category_dist = {}
            for diff in all_differences:
                category = diff.get("category", "unknown")
                category_dist[category] = category_dist.get(category, 0) + 1
            
            # Generate insights
            insights = []
            
            if overall_similarity > 0.8:
                insights.append("Documents are highly similar with minimal differences")
            elif overall_similarity > 0.6:
                insights.append("Documents show moderate similarity with some key differences")
            else:
                insights.append("Documents show significant differences requiring careful review")
            
            critical_diffs = [d for d in all_differences if d.get("severity") == "CRITICAL"]
            if critical_diffs:
                insights.append(f"Found {len(critical_diffs)} critical differences requiring immediate attention")
            
            compliance_impact = compliance_result.get("compliance_impact", "")
            if "risk" in compliance_impact.lower() or "compliance" in compliance_impact.lower():
                insights.append("Significant compliance implications detected")
            
            # Generate recommendations
            recommendations = []
            
            if critical_diffs:
                recommendations.append("Immediate review required for critical differences")
            
            high_diffs = [d for d in all_differences if d.get("severity") == "HIGH"]
            if high_diffs:
                recommendations.append("High-priority review recommended for high-severity differences")
            
            if compliance_diffs:
                recommendations.append("Legal/compliance review recommended")
            
            if not recommendations:
                recommendations.append("Documents appear compatible with standard review process")
            
            return {
                "overall_similarity": overall_similarity,
                "total_differences": len(all_differences),
                "severity_distribution": severity_dist,
                "category_distribution": category_dist,
                "insights": insights,
                "recommendations": recommendations,
                "comparison_summary": {
                    "semantic_analysis": semantic_result.get("semantic_analysis", ""),
                    "structural_analysis": structural_result.get("structural_analysis", ""),
                    "compliance_impact": compliance_result.get("compliance_impact", ""),
                    "entity_analysis": entity_result.get("entity_analysis", "")
                }
            }
            
        except Exception as e:
            return {
                "overall_similarity": 0.0,
                "total_differences": 0,
                "severity_distribution": {},
                "category_distribution": {},
                "insights": [f"Summary generation failed: {str(e)}"],
                "recommendations": ["Manual review required"],
                "comparison_summary": {}
            }


class CompareAgent(BaseAgent):
    """Agent responsible for document comparison and analysis"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__("CompareAgent", AgentType.COMPARE)
        self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
        
        # Add tools
        self.add_tool(SemanticComparisonTool())
        self.add_tool(StructuralComparisonTool())
        self.add_tool(ComplianceComparisonTool())
        self.add_tool(EntityComparisonTool())
        self.add_tool(ComparisonSummaryTool())
    
    async def run(self, goal: str, context: Dict[str, Any]) -> AgentResult:
        """Main document comparison process"""
        document_a = context.get("document_a")
        document_b = context.get("document_b")
        
        if not document_a or not document_b:
            return AgentResult(
                output=None,
                rationale="Two documents required for comparison",
                confidence=0.0,
                next_suggested_action="Provide both documents in context"
            )
        
        try:
            # Get document information
            doc_a_type = document_a.doc_type.value if document_a.doc_type else "unknown"
            doc_b_type = document_b.doc_type.value if document_b.doc_type else "unknown"
            
            doc_a_entities = document_a.metadata.get("entities", [])
            doc_b_entities = document_b.metadata.get("entities", [])
            
            doc_a_risk = document_a.metadata.get("risk_assessment", {})
            doc_b_risk = document_b.metadata.get("risk_assessment", {})
            
            # Perform semantic comparison
            semantic_tool = self.get_tool("semantic_compare")
            semantic_result = await semantic_tool.execute(
                doc_a_content=document_a.content,
                doc_b_content=document_b.content,
                doc_a_type=doc_a_type,
                doc_b_type=doc_b_type
            )
            
            # Perform structural comparison
            structural_tool = self.get_tool("structural_compare")
            structural_result = await structural_tool.execute(
                doc_a_content=document_a.content,
                doc_b_content=document_b.content,
                doc_a_type=doc_a_type,
                doc_b_type=doc_b_type
            )
            
            # Perform compliance comparison
            compliance_tool = self.get_tool("compliance_compare")
            compliance_result = await compliance_tool.execute(
                doc_a_content=document_a.content,
                doc_b_content=document_b.content,
                doc_a_risk=doc_a_risk,
                doc_b_risk=doc_b_risk
            )
            
            # Perform entity comparison
            entity_tool = self.get_tool("entity_compare")
            entity_result = await entity_tool.execute(
                doc_a_entities=doc_a_entities,
                doc_b_entities=doc_b_entities
            )
            
            # Generate comparison summary
            summary_tool = self.get_tool("generate_summary")
            comparison_summary = await summary_tool.execute(
                semantic_result=semantic_result,
                structural_result=structural_result,
                compliance_result=compliance_result,
                entity_result=entity_result
            )
            
            # Create comparison result
            comparison_result = {
                "comparison_id": f"comp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "document_a": {
                    "id": getattr(document_a, 'id', 'unknown'),
                    "type": doc_a_type,
                    "filename": getattr(document_a, 'filename', 'unknown')
                },
                "document_b": {
                    "id": getattr(document_b, 'id', 'unknown'),
                    "type": doc_b_type,
                    "filename": getattr(document_b, 'filename', 'unknown')
                },
                "comparison_results": {
                    "semantic": semantic_result,
                    "structural": structural_result,
                    "compliance": compliance_result,
                    "entity": entity_result,
                    "summary": comparison_summary
                },
                "comparison_metadata": {
                    "compared_at": datetime.utcnow().isoformat(),
                    "comparison_type": "comprehensive"
                }
            }
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                semantic_result,
                structural_result,
                compliance_result,
                entity_result,
                comparison_summary
            )
            
            # Generate rationale
            overall_similarity = comparison_summary.get("overall_similarity", 0.0)
            total_differences = comparison_summary.get("total_differences", 0)
            
            rationale = f"Comparison completed: {overall_similarity:.2f} similarity, {total_differences} differences identified across semantic, structural, compliance, and entity dimensions"
            
            return AgentResult(
                output=comparison_result,
                rationale=rationale,
                confidence=confidence,
                next_suggested_action="Review comparison results and address critical differences",
                metadata={
                    "semantic_result": semantic_result,
                    "structural_result": structural_result,
                    "compliance_result": compliance_result,
                    "entity_result": entity_result,
                    "comparison_summary": comparison_summary
                }
            )
            
        except Exception as e:
            return AgentResult(
                output=None,
                rationale=f"Document comparison failed: {str(e)}",
                confidence=0.0,
                next_suggested_action="Manual comparison required"
            )
    
    def _calculate_confidence(self, semantic_result: Dict, structural_result: Dict, compliance_result: Dict, entity_result: Dict, summary: Dict) -> float:
        """Calculate confidence based on comparison results"""
        confidence = 0.5  # Base confidence
        
        # Semantic analysis confidence
        semantic_diffs = semantic_result.get("semantic_differences", [])
        if semantic_diffs:
            avg_semantic_confidence = sum(d.get("confidence", 0) for d in semantic_diffs) / len(semantic_diffs)
            confidence += avg_semantic_confidence * 0.2
        
        # Structural analysis confidence
        structural_diffs = structural_result.get("structural_differences", [])
        if structural_diffs:
            avg_structural_confidence = sum(d.get("confidence", 0) for d in structural_diffs) / len(structural_diffs)
            confidence += avg_structural_confidence * 0.15
        
        # Compliance analysis confidence
        compliance_diffs = compliance_result.get("compliance_differences", [])
        if compliance_diffs:
            avg_compliance_confidence = sum(d.get("confidence", 0) for d in compliance_diffs) / len(compliance_diffs)
            confidence += avg_compliance_confidence * 0.15
        
        # Entity analysis confidence
        entity_diffs = entity_result.get("entity_differences", [])
        if entity_diffs:
            avg_entity_confidence = sum(d.get("confidence", 0) for d in entity_diffs) / len(entity_diffs)
            confidence += avg_entity_confidence * 0.1
        
        # Overall analysis completeness
        total_differences = summary.get("total_differences", 0)
        if total_differences > 0:
            confidence += 0.1
        
        return min(1.0, max(0.0, confidence))
