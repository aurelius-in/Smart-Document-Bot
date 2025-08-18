import json
import re
from typing import Any, Dict, List, Optional

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

from .base import BaseAgent, Tool
from ..models.base import AgentResult, AgentType, RiskFinding, SeverityLevel


class OPAPolicyTool(Tool):
    """Open Policy Agent (OPA) integration tool"""
    
    def __init__(self):
        super().__init__("opa_evaluate", "Evaluate policies using OPA")
    
    async def execute(self, policy_name: str, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Evaluate OPA policy"""
        try:
            # In a real implementation, this would call OPA server
            # For demo purposes, we'll simulate OPA evaluation
            
            # Load policy rules
            policy_rules = self._load_policy_rules(policy_name)
            
            # Apply rules to input data
            violations = []
            for rule in policy_rules:
                if self._evaluate_rule(rule, input_data):
                    violations.append({
                        "rule_id": rule["id"],
                        "description": rule["description"],
                        "severity": rule["severity"],
                        "policy_reference": rule["policy_ref"]
                    })
            
            return {
                "violations": violations,
                "total_rules_evaluated": len(policy_rules),
                "violation_count": len(violations)
            }
            
        except Exception as e:
            return {
                "violations": [],
                "error": str(e),
                "total_rules_evaluated": 0,
                "violation_count": 0
            }
    
    def _load_policy_rules(self, policy_name: str) -> List[Dict[str, Any]]:
        """Load policy rules based on policy name"""
        # Demo policy rules - in production, these would be loaded from .rego files
        policies = {
            "hipaa": [
                {
                    "id": "hipaa_001",
                    "description": "PHI disclosure without authorization",
                    "severity": "critical",
                    "policy_ref": "HIPAA §164.502(a)",
                    "pattern": r"\b(patient|medical|health|diagnosis|treatment)\b.*\b(share|disclose|release|publish)\b"
                },
                {
                    "id": "hipaa_002", 
                    "description": "Missing privacy notice",
                    "severity": "high",
                    "policy_ref": "HIPAA §164.520",
                    "pattern": r"\bprivacy\s+notice\b"
                }
            ],
            "sec": [
                {
                    "id": "sec_001",
                    "description": "Material information omission",
                    "severity": "critical", 
                    "policy_ref": "SEC Rule 10b-5",
                    "pattern": r"\b(material|significant|important)\b.*\b(omitted|withheld|concealed)\b"
                },
                {
                    "id": "sec_002",
                    "description": "Insider trading indicators",
                    "severity": "high",
                    "policy_ref": "SEC Rule 10b5-1",
                    "pattern": r"\b(insider|non-public|confidential)\b.*\b(trade|sell|buy)\b"
                }
            ],
            "generic": [
                {
                    "id": "gen_001",
                    "description": "Unclear liability terms",
                    "severity": "medium",
                    "policy_ref": "Contract Law §2-314",
                    "pattern": r"\b(liability|responsibility)\b.*\b(unlimited|unclear|vague)\b"
                },
                {
                    "id": "gen_002",
                    "description": "Missing termination clause",
                    "severity": "medium",
                    "policy_ref": "Contract Law §2-309",
                    "pattern": r"\b(terminate|end|cancel)\b"
                }
            ]
        }
        
        return policies.get(policy_name, policies["generic"])
    
    def _evaluate_rule(self, rule: Dict[str, Any], input_data: Dict[str, Any]) -> bool:
        """Evaluate if a rule is violated"""
        text = input_data.get("text", "").lower()
        pattern = rule.get("pattern", "")
        
        if pattern:
            return bool(re.search(pattern, text, re.IGNORECASE))
        
        return False


class RiskScoringTool(Tool):
    """Risk scoring and severity assessment tool"""
    
    def __init__(self):
        super().__init__("risk_score", "Score risks and assess severity")
    
    async def execute(self, violations: List[Dict[str, Any]], context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Score risks based on violations and context"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            prompt = f"""
Analyze these policy violations and assess overall risk. Respond with JSON only.

VIOLATIONS:
{json.dumps(violations, indent=2)}

CONTEXT:
- Document type: {context.get('doc_type', 'unknown')}
- Domain: {context.get('domain', 'unknown')}
- Entity count: {context.get('entity_count', 0)}

TASK:
1. Assess overall risk level (low/medium/high/critical)
2. Calculate risk score (0.0-1.0)
3. Identify top 3 risk factors
4. Suggest mitigations

Respond with JSON:
{{
    "overall_risk": "risk_level",
    "risk_score": 0.75,
    "top_risk_factors": ["factor1", "factor2", "factor3"],
    "suggested_mitigations": ["mitigation1", "mitigation2"],
    "confidence": 0.85
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
                "overall_risk": "medium",
                "risk_score": 0.5,
                "top_risk_factors": ["Unknown"],
                "suggested_mitigations": ["Manual review required"],
                "confidence": 0.0,
                "error": str(e)
            }


class MitigationSuggestionTool(Tool):
    """Generate risk mitigation suggestions"""
    
    def __init__(self):
        super().__init__("suggest_mitigation", "Suggest risk mitigation strategies")
    
    async def execute(self, violation: Dict[str, Any], context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate mitigation suggestions for a violation"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            prompt = f"""
Generate specific mitigation suggestions for this policy violation. Respond with JSON only.

VIOLATION:
- Rule: {violation.get('description', 'Unknown')}
- Severity: {violation.get('severity', 'medium')}
- Policy Reference: {violation.get('policy_reference', 'Unknown')}

CONTEXT:
- Document type: {context.get('doc_type', 'unknown')}
- Domain: {context.get('domain', 'unknown')}

TASK:
Provide specific, actionable mitigation strategies.

Respond with JSON:
{{
    "mitigation_strategies": [
        {{
            "strategy": "strategy description",
            "priority": "high/medium/low",
            "effort": "low/medium/high",
            "effectiveness": 0.85
        }}
    ],
    "compliance_actions": ["action1", "action2"],
    "timeline": "immediate/short-term/long-term"
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
                "mitigation_strategies": [],
                "compliance_actions": ["Manual review required"],
                "timeline": "immediate",
                "error": str(e)
            }


class RiskAgent(BaseAgent):
    """Agent responsible for risk assessment and compliance evaluation"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__("RiskAgent", AgentType.RISK)
        self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
        
        # Add tools
        self.add_tool(OPAPolicyTool())
        self.add_tool(RiskScoringTool())
        self.add_tool(MitigationSuggestionTool())
    
    async def run(self, goal: str, context: Dict[str, Any]) -> AgentResult:
        """Main risk assessment process"""
        document = context.get("entity_result")
        if not document or not hasattr(document, 'content'):
            return AgentResult(
                output=None,
                rationale="No document content available from entity extraction",
                confidence=0.0,
                next_suggested_action="Ensure entities are extracted first"
            )
        
        try:
            # Determine applicable policies
            doc_type = context.get("doc_type", "unknown")
            domain = context.get("domain", "other")
            
            policies = self._get_applicable_policies(doc_type, domain)
            
            # Evaluate each policy
            all_violations = []
            policy_results = {}
            
            for policy in policies:
                opa_tool = self.get_tool("opa_evaluate")
                input_data = {
                    "text": document.content,
                    "doc_type": doc_type,
                    "domain": domain,
                    "entities": context.get("entities", [])
                }
                
                result = await opa_tool.execute(policy_name=policy, input_data=input_data)
                policy_results[policy] = result
                
                # Add policy name to violations
                for violation in result.get("violations", []):
                    violation["policy_name"] = policy
                    all_violations.append(violation)
            
            # Score overall risk
            risk_tool = self.get_tool("risk_score")
            risk_assessment = await risk_tool.execute(
                violations=all_violations,
                context={
                    "doc_type": doc_type,
                    "domain": domain,
                    "entity_count": len(context.get("entities", []))
                }
            )
            
            # Generate risk findings
            findings = []
            for violation in all_violations:
                # Generate mitigation suggestions
                mitigation_tool = self.get_tool("suggest_mitigation")
                mitigation = await mitigation_tool.execute(
                    violation=violation,
                    context={"doc_type": doc_type, "domain": domain}
                )
                
                finding = RiskFinding(
                    severity=SeverityLevel(violation.get("severity", "medium")),
                    category=violation.get("policy_name", "unknown"),
                    description=violation.get("description", "Unknown violation"),
                    policy_reference=violation.get("policy_reference", "Unknown"),
                    location={"policy": violation.get("policy_name")},
                    confidence=0.8,  # Based on OPA evaluation
                    suggested_mitigation="; ".join(mitigation.get("compliance_actions", []))
                )
                findings.append(finding)
            
            # Calculate overall confidence
            total_violations = len(all_violations)
            if total_violations == 0:
                overall_confidence = 0.9  # High confidence in no violations
            else:
                # Average confidence across findings
                overall_confidence = sum(f.confidence for f in findings) / len(findings)
            
            # Generate rationale
            rationale = f"Evaluated {len(policies)} policies. Found {total_violations} violations. Overall risk: {risk_assessment.get('overall_risk', 'unknown')}"
            
            return AgentResult(
                output={
                    "findings": findings,
                    "risk_assessment": risk_assessment,
                    "policy_results": policy_results,
                    "total_violations": total_violations
                },
                rationale=rationale,
                confidence=overall_confidence,
                next_suggested_action="Proceed to audit trail generation" if total_violations == 0 else "Review violations and implement mitigations"
            )
            
        except Exception as e:
            return AgentResult(
                output={"findings": [], "risk_assessment": {}, "policy_results": {}, "total_violations": 0},
                rationale=f"Risk assessment failed: {str(e)}",
                confidence=0.0,
                next_suggested_action="Manual risk assessment required"
            )
    
    def _get_applicable_policies(self, doc_type: str, domain: str) -> List[str]:
        """Get list of applicable policies based on document type and domain"""
        policies = ["generic"]  # Always include generic policies
        
        # Add domain-specific policies
        if domain == "healthcare":
            policies.append("hipaa")
        elif domain == "finance":
            policies.append("sec")
        
        # Add document-type specific policies
        if doc_type in ["contract", "legal_document"]:
            policies.append("contract_law")
        
        return policies
    
    def get_risk_summary(self, findings: List[RiskFinding]) -> Dict[str, Any]:
        """Get summary of risk findings"""
        if not findings:
            return {"total": 0, "by_severity": {}, "by_category": {}}
        
        by_severity = {}
        by_category = {}
        
        for finding in findings:
            # Count by severity
            severity = finding.severity.value
            if severity not in by_severity:
                by_severity[severity] = 0
            by_severity[severity] += 1
            
            # Count by category
            category = finding.category
            if category not in by_category:
                by_category[category] = 0
            by_category[category] += 1
        
        return {
            "total": len(findings),
            "by_severity": by_severity,
            "by_category": by_category,
            "critical_count": by_severity.get("critical", 0),
            "high_count": by_severity.get("high", 0)
        }
