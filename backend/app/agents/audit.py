import hashlib
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

from .base import BaseAgent, Tool
from ..models.base import AgentResult, AgentType, AuditBundle, RiskFinding, Entity


class AuditLogTool(Tool):
    """Create immutable audit logs"""
    
    def __init__(self):
        super().__init__("audit_log", "Create immutable audit log entries")
    
    async def execute(self, trace_id: UUID, steps: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Create audit log with hash chaining"""
        try:
            audit_entries = []
            previous_hash = None
            
            for i, step in enumerate(steps):
                # Create audit entry
                entry = {
                    "entry_id": i + 1,
                    "timestamp": step.get("timestamp", datetime.utcnow().isoformat()),
                    "agent": step.get("agent", "unknown"),
                    "action": step.get("tool", "execution"),
                    "input_ref": step.get("input_ref"),
                    "output_ref": step.get("output_ref"),
                    "rationale": step.get("rationale", ""),
                    "confidence": step.get("confidence", 0.0),
                    "duration_ms": step.get("duration_ms", 0),
                    "previous_hash": previous_hash,
                    "metadata": step.get("metadata", {})
                }
                
                # Calculate hash
                entry_data = json.dumps(entry, sort_keys=True, default=str)
                entry_hash = hashlib.sha256(entry_data.encode()).hexdigest()
                entry["hash"] = entry_hash
                
                audit_entries.append(entry)
                previous_hash = entry_hash
            
            # Create final audit log
            audit_log = {
                "trace_id": str(trace_id),
                "created_at": datetime.utcnow().isoformat(),
                "total_entries": len(audit_entries),
                "entries": audit_entries,
                "final_hash": previous_hash
            }
            
            return audit_log
            
        except Exception as e:
            return {
                "error": str(e),
                "trace_id": str(trace_id),
                "entries": []
            }


class ReportGenerationTool(Tool):
    """Generate audit reports"""
    
    def __init__(self):
        super().__init__("generate_report", "Generate comprehensive audit report")
    
    async def execute(self, audit_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate audit report"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            # Prepare report data
            report_data = {
                "trace_summary": audit_data.get("trace", {}),
                "findings": audit_data.get("findings", []),
                "entities": audit_data.get("entities", []),
                "audit_log": audit_data.get("audit_log", {})
            }
            
            prompt = f"""
Generate a comprehensive audit report based on this data. Respond with JSON only.

AUDIT DATA:
{json.dumps(report_data, indent=2, default=str)}

TASK:
1. Create executive summary
2. List key findings and risks
3. Provide compliance assessment
4. Suggest recommendations
5. Include technical details

Respond with JSON:
{{
    "executive_summary": "summary text",
    "key_findings": [
        {{
            "finding": "finding description",
            "severity": "high/medium/low",
            "impact": "impact description"
        }}
    ],
    "compliance_assessment": "assessment text",
    "recommendations": ["rec1", "rec2"],
    "technical_details": {{
        "total_agents": 5,
        "processing_time": "2.5 minutes",
        "confidence_score": 0.85
    }},
    "risk_score": 0.75
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
                "executive_summary": f"Report generation failed: {str(e)}",
                "key_findings": [],
                "compliance_assessment": "Unable to assess",
                "recommendations": ["Manual review required"],
                "technical_details": {},
                "risk_score": 0.0
            }


class ExportBundleTool(Tool):
    """Create exportable audit bundle"""
    
    def __init__(self):
        super().__init__("export_bundle", "Create exportable audit bundle")
    
    async def execute(self, audit_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Create export bundle with all data"""
        try:
            # Create bundle structure
            bundle = {
                "metadata": {
                    "created_at": datetime.utcnow().isoformat(),
                    "version": "1.0",
                    "format": "audit_bundle"
                },
                "document_info": audit_data.get("document", {}),
                "trace_info": audit_data.get("trace", {}),
                "findings": audit_data.get("findings", []),
                "entities": audit_data.get("entities", []),
                "audit_log": audit_data.get("audit_log", {}),
                "report": audit_data.get("report", {}),
                "export_info": {
                    "total_files": 4,  # JSON, CSV, PDF, ZIP
                    "bundle_size": "estimated_size",
                    "hash": "bundle_hash"
                }
            }
            
            # Calculate bundle hash
            bundle_data = json.dumps(bundle, sort_keys=True, default=str)
            bundle_hash = hashlib.sha256(bundle_data.encode()).hexdigest()
            bundle["export_info"]["hash"] = bundle_hash
            
            return bundle
            
        except Exception as e:
            return {
                "error": str(e),
                "metadata": {"created_at": datetime.utcnow().isoformat()}
            }


class ComplianceValidationTool(Tool):
    """Validate compliance with audit requirements"""
    
    def __init__(self):
        super().__init__("compliance_validation", "Validate audit compliance")
    
    async def execute(self, audit_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Validate compliance"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            prompt = f"""
Validate this audit for compliance with regulatory requirements. Respond with JSON only.

AUDIT DATA:
{json.dumps(audit_data, indent=2, default=str)}

COMPLIANCE REQUIREMENTS:
- Complete audit trail
- Tamper evidence
- Risk assessment
- Entity extraction
- Policy evaluation

TASK:
1. Check completeness
2. Validate tamper evidence
3. Assess compliance score
4. Identify gaps

Respond with JSON:
{{
    "compliance_score": 0.85,
    "completeness": "complete/partial/incomplete",
    "tamper_evidence": "valid/invalid",
    "gaps": ["gap1", "gap2"],
    "recommendations": ["rec1", "rec2"],
    "validation_status": "passed/failed"
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
                "compliance_score": 0.0,
                "completeness": "incomplete",
                "tamper_evidence": "invalid",
                "gaps": [f"Validation failed: {str(e)}"],
                "recommendations": ["Manual validation required"],
                "validation_status": "failed"
            }


class AuditAgent(BaseAgent):
    """Agent responsible for audit trail generation and compliance validation"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__("AuditAgent", AgentType.AUDIT)
        self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
        
        # Add tools
        self.add_tool(AuditLogTool())
        self.add_tool(ReportGenerationTool())
        self.add_tool(ExportBundleTool())
        self.add_tool(ComplianceValidationTool())
    
    async def run(self, goal: str, context: Dict[str, Any]) -> AgentResult:
        """Main audit process"""
        trace = context.get("trace")
        if not trace:
            return AgentResult(
                output=None,
                rationale="No trace data available for audit",
                confidence=0.0,
                next_suggested_action="Provide trace data in context"
            )
        
        try:
            # Extract data from context
            document = context.get("document")
            findings = context.get("findings", [])
            entities = context.get("entities", [])
            
            # Create audit log
            audit_tool = self.get_tool("audit_log")
            audit_log = await audit_tool.execute(
                trace_id=trace.trace_id,
                steps=[step.dict() for step in trace.steps]
            )
            
            # Generate report
            report_tool = self.get_tool("generate_report")
            audit_data = {
                "trace": trace.dict(),
                "document": document.dict() if document else {},
                "findings": [f.dict() for f in findings] if findings else [],
                "entities": [e.dict() for e in entities] if entities else [],
                "audit_log": audit_log
            }
            
            report = await report_tool.execute(audit_data=audit_data)
            
            # Validate compliance
            validation_tool = self.get_tool("compliance_validation")
            validation = await validation_tool.execute(audit_data=audit_data)
            
            # Create export bundle
            export_tool = self.get_tool("export_bundle")
            bundle_data = {
                **audit_data,
                "report": report,
                "validation": validation
            }
            
            export_bundle = await export_tool.execute(audit_data=bundle_data)
            
            # Create audit bundle object
            audit_bundle = AuditBundle(
                document_id=getattr(document, 'id', 'unknown') if document else 'unknown',
                trace_id=trace.trace_id,
                findings=findings,
                entities=entities,
                metadata={
                    "audit_log": audit_log,
                    "report": report,
                    "validation": validation,
                    "export_bundle": export_bundle
                },
                hash=export_bundle.get("export_info", {}).get("hash", "")
            )
            
            # Calculate overall confidence
            compliance_score = validation.get("compliance_score", 0.0)
            validation_status = validation.get("validation_status", "failed")
            
            if validation_status == "passed" and compliance_score > 0.8:
                overall_confidence = 0.9
            elif validation_status == "passed":
                overall_confidence = compliance_score
            else:
                overall_confidence = 0.5
            
            # Generate rationale
            rationale = f"Audit completed with {len(audit_log.get('entries', []))} entries. Compliance score: {compliance_score:.2f}. Status: {validation_status}"
            
            return AgentResult(
                output=audit_bundle,
                rationale=rationale,
                confidence=overall_confidence,
                next_suggested_action="Export audit bundle" if validation_status == "passed" else "Address compliance gaps"
            )
            
        except Exception as e:
            return AgentResult(
                output=AuditBundle(
                    document_id="unknown",
                    trace_id=trace.trace_id if trace else "unknown",
                    findings=[],
                    entities=[],
                    metadata={"error": str(e)},
                    hash=""
                ),
                rationale=f"Audit failed: {str(e)}",
                confidence=0.0,
                next_suggested_action="Manual audit required"
            )
    
    def get_audit_summary(self, audit_bundle: AuditBundle) -> Dict[str, Any]:
        """Get summary of audit bundle"""
        return {
            "document_id": audit_bundle.document_id,
            "trace_id": audit_bundle.trace_id,
            "findings_count": len(audit_bundle.findings),
            "entities_count": len(audit_bundle.entities),
            "compliance_score": audit_bundle.metadata.get("validation", {}).get("compliance_score", 0.0),
            "validation_status": audit_bundle.metadata.get("validation", {}).get("validation_status", "unknown"),
            "created_at": audit_bundle.created_at.isoformat(),
            "hash": audit_bundle.hash
        }
    
    def validate_audit_integrity(self, audit_bundle: AuditBundle) -> Dict[str, Any]:
        """Validate audit bundle integrity"""
        try:
            # Check hash consistency
            bundle_data = json.dumps(audit_bundle.dict(), sort_keys=True, default=str)
            calculated_hash = hashlib.sha256(bundle_data.encode()).hexdigest()
            
            is_valid = calculated_hash == audit_bundle.hash
            
            return {
                "integrity_valid": is_valid,
                "calculated_hash": calculated_hash,
                "stored_hash": audit_bundle.hash,
                "validation_timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "integrity_valid": False,
                "error": str(e),
                "validation_timestamp": datetime.utcnow().isoformat()
            }
