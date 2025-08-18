import json
import re
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from .base import BaseAgent, Tool
from ..models.base import AgentResult, AgentType, Document


class AuditLevel(Enum):
    """Audit level enumeration"""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    REGULATORY = "regulatory"


class AuditType(Enum):
    """Audit type enumeration"""
    COMPLIANCE = "compliance"
    RISK = "risk"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    SECURITY = "security"


class AuditTrailGeneratorTool(Tool):
    """Tool for generating comprehensive audit trails"""
    
    def __init__(self):
        super().__init__("generate_audit_trail", "Generate comprehensive audit trail")
    
    async def execute(self, document: Document, processing_history: List[Dict], **kwargs) -> Dict[str, Any]:
        """Generate audit trail for document processing"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            system_prompt = """You are an expert audit trail generator. Create a comprehensive audit trail for document processing.
            
            For each audit event, provide:
            - event_id: Unique event identifier
            - timestamp: ISO timestamp
            - event_type: Type of audit event
            - description: Detailed description
            - severity: LOW/MEDIUM/HIGH/CRITICAL
            - user: User who performed action
            - system_component: Component that generated event
            - metadata: Additional event metadata
            - compliance_relevance: Compliance implications
            
            Also provide:
            - audit_summary: Overall audit summary
            - compliance_status: Compliance status assessment
            - recommendations: Audit recommendations
            
            Respond with JSON:
            {
                "audit_events": [
                    {
                        "event_id": "evt_001",
                        "timestamp": "2024-01-01T10:00:00Z",
                        "event_type": "document_upload",
                        "description": "Document uploaded for processing",
                        "severity": "LOW",
                        "user": "user@example.com",
                        "system_component": "upload_service",
                        "metadata": {"file_size": 1024, "file_type": "pdf"},
                        "compliance_relevance": "Standard document processing"
                    }
                ],
                "audit_summary": "Comprehensive audit trail generated",
                "compliance_status": "COMPLIANT",
                "recommendations": ["Continue monitoring", "Review access logs"]
            }
            """
            
            # Prepare processing history context
            history_context = ""
            if processing_history:
                history_context = f"\n\nPROCESSING HISTORY:\n{json.dumps(processing_history, indent=2)}"
            
            # Get document metadata
            doc_metadata = document.metadata if hasattr(document, 'metadata') else {}
            doc_type = document.doc_type.value if hasattr(document, 'doc_type') and document.doc_type else "unknown"
            
            user_prompt = f"Generate audit trail for {doc_type} document:{history_context}\n\nDOCUMENT METADATA:\n{json.dumps(doc_metadata, indent=2)}\n\nDOCUMENT CONTENT (first 1000 chars):\n{document.content[:1000]}..."
            
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
                "audit_events": [],
                "audit_summary": f"Audit trail generation failed: {str(e)}",
                "compliance_status": "UNKNOWN",
                "recommendations": ["Manual audit review required"]
            }


class ComplianceReportGeneratorTool(Tool):
    """Tool for generating compliance reports"""
    
    def __init__(self):
        super().__init__("generate_compliance_report", "Generate compliance report")
    
    async def execute(self, document: Document, risk_assessment: Dict, audit_trail: Dict, **kwargs) -> Dict[str, Any]:
        """Generate compliance report"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            system_prompt = """You are an expert compliance analyst. Generate a comprehensive compliance report.
            
            For each compliance finding, provide:
            - finding_id: Unique finding identifier
            - regulation: Applicable regulation
            - requirement: Specific requirement
            - status: COMPLIANT/NON_COMPLIANT/PARTIAL
            - description: Detailed description
            - evidence: Supporting evidence
            - risk_level: LOW/MEDIUM/HIGH/CRITICAL
            - remediation: Required remediation actions
            - deadline: Remediation deadline
            
            Also provide:
            - overall_compliance_score: Overall compliance score (0.0-1.0)
            - compliance_summary: Overall compliance assessment
            - regulatory_implications: Regulatory implications
            - next_steps: Recommended next steps
            
            Respond with JSON:
            {
                "compliance_findings": [
                    {
                        "finding_id": "comp_001",
                        "regulation": "GDPR",
                        "requirement": "Data Protection",
                        "status": "COMPLIANT",
                        "description": "Document contains appropriate data protection measures",
                        "evidence": "Encryption and access controls implemented",
                        "risk_level": "LOW",
                        "remediation": "None required",
                        "deadline": "N/A"
                    }
                ],
                "overall_compliance_score": 0.85,
                "compliance_summary": "Document demonstrates good compliance posture",
                "regulatory_implications": "Minimal regulatory risk",
                "next_steps": ["Continue monitoring", "Annual review"]
            }
            """
            
            # Prepare context
            context = ""
            if risk_assessment:
                context += f"\n\nRISK ASSESSMENT:\n{json.dumps(risk_assessment, indent=2)}"
            if audit_trail:
                context += f"\n\nAUDIT TRAIL:\n{json.dumps(audit_trail, indent=2)}"
            
            doc_type = document.doc_type.value if hasattr(document, 'doc_type') and document.doc_type else "unknown"
            doc_metadata = document.metadata if hasattr(document, 'metadata') else {}
            
            user_prompt = f"Generate compliance report for {doc_type} document:{context}\n\nDOCUMENT METADATA:\n{json.dumps(doc_metadata, indent=2)}\n\nDOCUMENT CONTENT (first 1000 chars):\n{document.content[:1000]}..."
            
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
                "compliance_findings": [],
                "overall_compliance_score": 0.0,
                "compliance_summary": f"Compliance report generation failed: {str(e)}",
                "regulatory_implications": "Unable to assess",
                "next_steps": ["Manual compliance review required"]
            }


class AuditBundleGeneratorTool(Tool):
    """Tool for generating audit bundles"""
    
    def __init__(self):
        super().__init__("generate_audit_bundle", "Generate audit bundle")
    
    async def execute(self, document: Document, audit_trail: Dict, compliance_report: Dict, risk_assessment: Dict, **kwargs) -> Dict[str, Any]:
        """Generate comprehensive audit bundle"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            system_prompt = """You are an expert audit bundle generator. Create a comprehensive audit bundle for regulatory compliance.
            
            The audit bundle should include:
            - executive_summary: High-level summary
            - audit_scope: Scope of audit
            - methodology: Audit methodology
            - findings_summary: Summary of findings
            - risk_assessment: Risk assessment summary
            - compliance_assessment: Compliance assessment
            - recommendations: Detailed recommendations
            - appendices: Supporting documentation
            
            Also provide:
            - bundle_id: Unique bundle identifier
            - created_at: Creation timestamp
            - valid_until: Validity period
            - regulatory_frameworks: Applicable frameworks
            - audit_level: Audit level (BASIC/STANDARD/COMPREHENSIVE/REGULATORY)
            
            Respond with JSON:
            {
                "bundle_id": "audit_bundle_001",
                "created_at": "2024-01-01T10:00:00Z",
                "valid_until": "2024-12-31T23:59:59Z",
                "regulatory_frameworks": ["GDPR", "SOX", "ISO27001"],
                "audit_level": "COMPREHENSIVE",
                "executive_summary": "Comprehensive audit completed",
                "audit_scope": "Full document lifecycle audit",
                "methodology": "Risk-based audit approach",
                "findings_summary": "Summary of audit findings",
                "risk_assessment": "Overall risk assessment",
                "compliance_assessment": "Compliance status assessment",
                "recommendations": ["Recommendation 1", "Recommendation 2"],
                "appendices": ["Appendix A", "Appendix B"]
            }
            """
            
            # Prepare comprehensive context
            context = ""
            if audit_trail:
                context += f"\n\nAUDIT TRAIL:\n{json.dumps(audit_trail, indent=2)}"
            if compliance_report:
                context += f"\n\nCOMPLIANCE REPORT:\n{json.dumps(compliance_report, indent=2)}"
            if risk_assessment:
                context += f"\n\nRISK ASSESSMENT:\n{json.dumps(risk_assessment, indent=2)}"
            
            doc_type = document.doc_type.value if hasattr(document, 'doc_type') and document.doc_type else "unknown"
            doc_metadata = document.metadata if hasattr(document, 'metadata') else {}
            
            user_prompt = f"Generate audit bundle for {doc_type} document:{context}\n\nDOCUMENT METADATA:\n{json.dumps(doc_metadata, indent=2)}\n\nDOCUMENT CONTENT (first 1000 chars):\n{document.content[:1000]}..."
            
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
                "bundle_id": f"audit_bundle_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "created_at": datetime.utcnow().isoformat(),
                "valid_until": "2024-12-31T23:59:59Z",
                "regulatory_frameworks": [],
                "audit_level": "BASIC",
                "executive_summary": f"Audit bundle generation failed: {str(e)}",
                "audit_scope": "Limited scope due to generation failure",
                "methodology": "Manual review required",
                "findings_summary": "Unable to generate findings",
                "risk_assessment": "Risk assessment unavailable",
                "compliance_assessment": "Compliance assessment unavailable",
                "recommendations": ["Manual audit review required"],
                "appendices": []
            }


class ValidationReportGeneratorTool(Tool):
    """Tool for generating validation reports"""
    
    def __init__(self):
        super().__init__("generate_validation_report", "Generate validation report")
    
    async def execute(self, audit_bundle: Dict, **kwargs) -> Dict[str, Any]:
        """Generate validation report for audit bundle"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            system_prompt = """You are an expert audit validator. Generate a validation report for an audit bundle.
            
            For each validation check, provide:
            - check_id: Unique check identifier
            - check_type: Type of validation check
            - status: PASS/FAIL/WARNING
            - description: Description of check
            - criteria: Validation criteria
            - result: Validation result
            - confidence: Confidence in validation (0.0-1.0)
            - recommendations: Validation recommendations
            
            Also provide:
            - overall_validation_score: Overall validation score (0.0-1.0)
            - validation_summary: Overall validation assessment
            - bundle_quality: Assessment of bundle quality
            - regulatory_acceptance: Likelihood of regulatory acceptance
            
            Respond with JSON:
            {
                "validation_checks": [
                    {
                        "check_id": "val_001",
                        "check_type": "completeness",
                        "status": "PASS",
                        "description": "Audit bundle completeness check",
                        "criteria": "All required sections present",
                        "result": "All sections found",
                        "confidence": 0.95,
                        "recommendations": "Bundle is complete"
                    }
                ],
                "overall_validation_score": 0.9,
                "validation_summary": "Audit bundle passes validation",
                "bundle_quality": "HIGH",
                "regulatory_acceptance": "LIKELY"
            }
            """
            
            user_prompt = f"Validate this audit bundle:\n\nAUDIT BUNDLE:\n{json.dumps(audit_bundle, indent=2)}"
            
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
                "validation_checks": [],
                "overall_validation_score": 0.0,
                "validation_summary": f"Validation report generation failed: {str(e)}",
                "bundle_quality": "UNKNOWN",
                "regulatory_acceptance": "UNKNOWN"
            }


class AuditAgent(BaseAgent):
    """Agent responsible for audit trail generation and compliance reporting"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__("AuditAgent", AgentType.AUDIT)
        self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
        
        # Add tools
        self.add_tool(AuditTrailGeneratorTool())
        self.add_tool(ComplianceReportGeneratorTool())
        self.add_tool(AuditBundleGeneratorTool())
        self.add_tool(ValidationReportGeneratorTool())
    
    async def run(self, goal: str, context: Dict[str, Any]) -> AgentResult:
        """Main audit process"""
        document = context.get("document")
        if not document:
            return AgentResult(
                output=None,
                rationale="No document provided in context",
                confidence=0.0,
                next_suggested_action="Provide document in context"
            )
        
        try:
            # Get processing history and assessments
            processing_history = context.get("processing_history", [])
            risk_assessment = document.metadata.get("risk_assessment", {}) if hasattr(document, 'metadata') else {}
            
            # Generate audit trail
            audit_trail_tool = self.get_tool("generate_audit_trail")
            audit_trail = await audit_trail_tool.execute(
                document=document,
                processing_history=processing_history
            )
            
            # Generate compliance report
            compliance_tool = self.get_tool("generate_compliance_report")
            compliance_report = await compliance_tool.execute(
                document=document,
                risk_assessment=risk_assessment,
                audit_trail=audit_trail
            )
            
            # Generate audit bundle
            bundle_tool = self.get_tool("generate_audit_bundle")
            audit_bundle = await bundle_tool.execute(
                document=document,
                audit_trail=audit_trail,
                compliance_report=compliance_report,
                risk_assessment=risk_assessment
            )
            
            # Generate validation report
            validation_tool = self.get_tool("generate_validation_report")
            validation_report = await validation_tool.execute(
                audit_bundle=audit_bundle
            )
            
            # Create comprehensive audit result
            audit_result = {
                "audit_id": f"audit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "document_info": {
                    "id": getattr(document, 'id', 'unknown'),
                    "type": document.doc_type.value if hasattr(document, 'doc_type') and document.doc_type else "unknown",
                    "filename": getattr(document, 'filename', 'unknown')
                },
                "audit_components": {
                    "audit_trail": audit_trail,
                    "compliance_report": compliance_report,
                    "audit_bundle": audit_bundle,
                    "validation_report": validation_report
                },
                "audit_metadata": {
                    "audited_at": datetime.utcnow().isoformat(),
                    "audit_level": audit_bundle.get("audit_level", "STANDARD"),
                    "regulatory_frameworks": audit_bundle.get("regulatory_frameworks", []),
                    "compliance_score": compliance_report.get("overall_compliance_score", 0.0),
                    "validation_score": validation_report.get("overall_validation_score", 0.0)
                }
            }
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                audit_trail,
                compliance_report,
                audit_bundle,
                validation_report
            )
            
            # Generate rationale
            compliance_score = compliance_report.get("overall_compliance_score", 0.0)
            validation_score = validation_report.get("overall_validation_score", 0.0)
            audit_events = len(audit_trail.get("audit_events", []))
            compliance_findings = len(compliance_report.get("compliance_findings", []))
            
            rationale = f"Audit completed: {audit_events} audit events, {compliance_findings} compliance findings. Compliance score: {compliance_score:.2f}, Validation score: {validation_score:.2f}"
            
            return AgentResult(
                output=audit_result,
                rationale=rationale,
                confidence=confidence,
                next_suggested_action="Review audit results and address any compliance issues",
                metadata={
                    "audit_trail": audit_trail,
                    "compliance_report": compliance_report,
                    "audit_bundle": audit_bundle,
                    "validation_report": validation_report
                }
            )
            
        except Exception as e:
            return AgentResult(
                output=None,
                rationale=f"Audit process failed: {str(e)}",
                confidence=0.0,
                next_suggested_action="Manual audit required"
            )
    
    def _calculate_confidence(self, audit_trail: Dict, compliance_report: Dict, audit_bundle: Dict, validation_report: Dict) -> float:
        """Calculate confidence based on audit results"""
        confidence = 0.5  # Base confidence
        
        # Audit trail confidence
        audit_events = audit_trail.get("audit_events", [])
        if audit_events:
            avg_event_confidence = sum(event.get("confidence", 0.5) for event in audit_events if "confidence" in event) / len(audit_events)
            confidence += avg_event_confidence * 0.2
        
        # Compliance report confidence
        compliance_score = compliance_report.get("overall_compliance_score", 0.0)
        confidence += compliance_score * 0.2
        
        # Audit bundle confidence
        bundle_quality = audit_bundle.get("bundle_quality", "UNKNOWN")
        if bundle_quality == "HIGH":
            confidence += 0.1
        elif bundle_quality == "MEDIUM":
            confidence += 0.05
        
        # Validation report confidence
        validation_score = validation_report.get("overall_validation_score", 0.0)
        confidence += validation_score * 0.2
        
        # Overall completeness
        if audit_events and compliance_report.get("compliance_findings"):
            confidence += 0.1
        
        return min(1.0, max(0.0, confidence))
