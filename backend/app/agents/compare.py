import json
from typing import Any, Dict, List, Optional, Tuple

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.embeddings import OpenAIEmbeddings

from .base import BaseAgent, Tool
from ..models.base import AgentResult, AgentType, ComparisonResult


class SemanticDiffTool(Tool):
    """Semantic difference analysis tool"""
    
    def __init__(self):
        super().__init__("semantic_diff", "Analyze semantic differences between documents")
        self.embeddings = OpenAIEmbeddings()
    
    async def execute(self, doc_a: str, doc_b: str, **kwargs) -> List[Dict[str, Any]]:
        """Find semantic differences between documents"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            # Chunk documents for comparison
            chunks_a = self._chunk_text(doc_a, chunk_size=500)
            chunks_b = self._chunk_text(doc_b, chunk_size=500)
            
            # Find differences
            differences = []
            
            # Compare key sections
            sections_to_compare = [
                "parties", "dates", "amounts", "obligations", "liabilities", 
                "termination", "governing_law", "dispute_resolution"
            ]
            
            for section in sections_to_compare:
                diff = await self._compare_section(section, doc_a, doc_b, llm)
                if diff:
                    differences.append(diff)
            
            # Find clause-level differences
            clause_diffs = await self._find_clause_differences(chunks_a, chunks_b, llm)
            differences.extend(clause_diffs)
            
            return differences
            
        except Exception as e:
            return []
    
    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                if last_period > start + chunk_size // 2:
                    chunk = text[start:start + last_period + 1]
                    end = start + last_period + 1
            
            chunks.append(chunk)
            start = end
        
        return chunks
    
    async def _compare_section(self, section: str, doc_a: str, doc_b: str, llm) -> Optional[Dict[str, Any]]:
        """Compare a specific section between documents"""
        try:
            prompt = f"""
Compare the {section} section between two documents and identify differences.

DOCUMENT A (first 1000 chars):
{doc_a[:1000]}...

DOCUMENT B (first 1000 chars):
{doc_b[:1000]}...

TASK: Find differences in {section} information between the documents.

Respond with JSON:
{{
    "section": "{section}",
    "differences": [
        {{
            "type": "added/removed/modified",
            "description": "description of difference",
            "doc_a_value": "value in doc A",
            "doc_b_value": "value in doc B",
            "impact": "low/medium/high",
            "confidence": 0.85
        }}
    ],
    "has_differences": true
}}
"""
            
            response = await llm.agenerate([[HumanMessage(content=prompt)]])
            result_text = response.generations[0][0].text.strip()
            
            # Extract JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1]
            
            result = json.loads(result_text)
            
            if result.get("has_differences", False):
                return {
                    "section": section,
                    "differences": result.get("differences", []),
                    "type": "section_comparison"
                }
            
            return None
            
        except Exception:
            return None
    
    async def _find_clause_differences(self, chunks_a: List[str], chunks_b: List[str], llm) -> List[Dict[str, Any]]:
        """Find clause-level differences"""
        try:
            prompt = f"""
Compare these document chunks and identify clause-level differences.

CHUNKS FROM DOCUMENT A:
{chr(10).join([f"Chunk {i+1}: {chunk[:200]}..." for i, chunk in enumerate(chunks_a[:3])])}

CHUNKS FROM DOCUMENT B:
{chr(10).join([f"Chunk {i+1}: {chunk[:200]}..." for i, chunk in enumerate(chunks_b[:3])])}

TASK: Identify specific clause differences between the documents.

Respond with JSON:
{{
    "clause_differences": [
        {{
            "clause_type": "liability/termination/payment/etc",
            "difference": "description of difference",
            "doc_a_clause": "clause text from A",
            "doc_b_clause": "clause text from B",
            "risk_impact": "increased/decreased/unchanged",
            "confidence": 0.85
        }}
    ]
}}
"""
            
            response = await llm.agenerate([[HumanMessage(content=prompt)]])
            result_text = response.generations[0][0].text.strip()
            
            # Extract JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1]
            
            result = json.loads(result_text)
            
            differences = []
            for diff in result.get("clause_differences", []):
                differences.append({
                    "section": diff.get("clause_type", "unknown"),
                    "differences": [diff],
                    "type": "clause_comparison"
                })
            
            return differences
            
        except Exception:
            return []


class RiskDeltaTool(Tool):
    """Calculate risk delta between documents"""
    
    def __init__(self):
        super().__init__("risk_delta", "Calculate risk changes between documents")
    
    async def execute(self, differences: List[Dict[str, Any]], doc_a_risk: Dict[str, Any], doc_b_risk: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Calculate risk delta based on differences"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            prompt = f"""
Calculate the risk delta between two documents based on their differences and risk assessments.

DIFFERENCES:
{json.dumps(differences, indent=2)}

DOCUMENT A RISK ASSESSMENT:
{json.dumps(doc_a_risk, indent=2)}

DOCUMENT B RISK ASSESSMENT:
{json.dumps(doc_b_risk, indent=2)}

TASK:
1. Calculate overall risk delta (positive = increased risk, negative = decreased risk)
2. Identify specific risk changes by category
3. Assess impact of each difference on risk

Respond with JSON:
{{
    "overall_risk_delta": 0.15,
    "risk_changes": {{
        "liability": 0.2,
        "compliance": -0.1,
        "operational": 0.05
    }},
    "risk_factors": [
        {{
            "factor": "factor name",
            "change": 0.1,
            "reason": "explanation",
            "impact": "high/medium/low"
        }}
    ],
    "summary": "Overall risk increased by 15% due to..."
}}
"""
            
            response = await llm.agenerate([[HumanMessage(content=prompt)]])
            result_text = response.generations[0][0].text.strip()
            
            # Extract JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1]
            
            return json.loads(result_text)
            
        except Exception as e:
            return {
                "overall_risk_delta": 0.0,
                "risk_changes": {},
                "risk_factors": [],
                "summary": f"Risk delta calculation failed: {str(e)}"
            }


class ComplianceImpactTool(Tool):
    """Assess compliance impact of changes"""
    
    def __init__(self):
        super().__init__("compliance_impact", "Assess compliance impact of document changes")
    
    async def execute(self, differences: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Assess compliance impact"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            prompt = f"""
Assess the compliance impact of these document changes.

DIFFERENCES:
{json.dumps(differences, indent=2)}

TASK:
1. Identify compliance implications of each change
2. Assess regulatory impact
3. Suggest compliance actions needed

Respond with JSON:
{{
    "compliance_impact": "low/medium/high",
    "regulatory_implications": [
        {{
            "regulation": "regulation name",
            "impact": "description",
            "action_required": "action needed"
        }}
    ],
    "compliance_actions": ["action1", "action2"],
    "risk_level": "low/medium/high"
}}
"""
            
            response = await llm.agenerate([[HumanMessage(content=prompt)]])
            result_text = response.generations[0][0].text.strip()
            
            # Extract JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1]
            
            return json.loads(result_text)
            
        except Exception as e:
            return {
                "compliance_impact": "unknown",
                "regulatory_implications": [],
                "compliance_actions": ["Manual review required"],
                "risk_level": "unknown"
            }


class CompareAgent(BaseAgent):
    """Agent responsible for document comparison and risk delta analysis"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__("CompareAgent", AgentType.COMPARE)
        self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
        
        # Add tools
        self.add_tool(SemanticDiffTool())
        self.add_tool(RiskDeltaTool())
        self.add_tool(ComplianceImpactTool())
    
    async def run(self, goal: str, context: Dict[str, Any]) -> AgentResult:
        """Main comparison process"""
        doc_a = context.get("document_a")
        doc_b = context.get("document_b")
        
        if not doc_a or not doc_b:
            return AgentResult(
                output=None,
                rationale="Two documents required for comparison",
                confidence=0.0,
                next_suggested_action="Provide document_a and document_b in context"
            )
        
        try:
            # Extract document content
            content_a = doc_a.content if hasattr(doc_a, 'content') else str(doc_a)
            content_b = doc_b.content if hasattr(doc_b, 'content') else str(doc_b)
            
            # Get risk assessments if available
            risk_a = context.get("risk_assessment_a", {})
            risk_b = context.get("risk_assessment_b", {})
            
            # Perform semantic diff
            diff_tool = self.get_tool("semantic_diff")
            differences = await diff_tool.execute(doc_a=content_a, doc_b=content_b)
            
            # Calculate risk delta
            risk_tool = self.get_tool("risk_delta")
            risk_delta = await risk_tool.execute(
                differences=differences,
                doc_a_risk=risk_a,
                doc_b_risk=risk_b
            )
            
            # Assess compliance impact
            compliance_tool = self.get_tool("compliance_impact")
            compliance_impact = await compliance_tool.execute(differences=differences)
            
            # Create comparison result
            comparison_result = ComparisonResult(
                doc_a_id=getattr(doc_a, 'id', 'unknown'),
                doc_b_id=getattr(doc_b, 'id', 'unknown'),
                semantic_diffs=differences,
                risk_delta=risk_delta.get("risk_changes", {}),
                confidence=0.8,  # Based on analysis quality
                summary=risk_delta.get("summary", "Comparison completed")
            )
            
            # Calculate overall confidence
            total_differences = len(differences)
            if total_differences == 0:
                overall_confidence = 0.9  # High confidence in no differences
            else:
                # Average confidence across differences
                avg_confidence = sum(
                    diff.get("confidence", 0.8) 
                    for section in differences 
                    for diff in section.get("differences", [])
                ) / max(1, sum(len(section.get("differences", [])) for section in differences))
                overall_confidence = avg_confidence
            
            # Generate rationale
            rationale = f"Found {total_differences} difference categories. Risk delta: {risk_delta.get('overall_risk_delta', 0):.2f}. Compliance impact: {compliance_impact.get('compliance_impact', 'unknown')}"
            
            return AgentResult(
                output={
                    "comparison": comparison_result,
                    "risk_delta": risk_delta,
                    "compliance_impact": compliance_impact,
                    "differences": differences
                },
                rationale=rationale,
                confidence=overall_confidence,
                next_suggested_action="Review high-impact differences" if risk_delta.get("overall_risk_delta", 0) > 0.1 else "Proceed with confidence"
            )
            
        except Exception as e:
            return AgentResult(
                output={
                    "comparison": ComparisonResult(
                        doc_a_id="unknown",
                        doc_b_id="unknown",
                        semantic_diffs=[],
                        risk_delta={},
                        confidence=0.0,
                        summary=f"Comparison failed: {str(e)}"
                    ),
                    "risk_delta": {},
                    "compliance_impact": {},
                    "differences": []
                },
                rationale=f"Comparison failed: {str(e)}",
                confidence=0.0,
                next_suggested_action="Manual comparison required"
            )
    
    def get_comparison_summary(self, differences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary of comparison differences"""
        if not differences:
            return {"total_differences": 0, "by_type": {}, "by_impact": {}}
        
        by_type = {}
        by_impact = {}
        
        for section in differences:
            section_type = section.get("type", "unknown")
            if section_type not in by_type:
                by_type[section_type] = 0
            by_type[section_type] += 1
            
            for diff in section.get("differences", []):
                impact = diff.get("impact", "unknown")
                if impact not in by_impact:
                    by_impact[impact] = 0
                by_impact[impact] += 1
        
        return {
            "total_differences": sum(len(section.get("differences", [])) for section in differences),
            "by_type": by_type,
            "by_impact": by_impact,
            "high_impact_count": by_impact.get("high", 0)
        }
