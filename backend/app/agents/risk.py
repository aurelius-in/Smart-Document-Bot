import json
import re
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from .base import BaseAgent, Tool
from ..models.base import AgentResult, AgentType, Document


class RiskLevel(Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCategory(Enum):
    """Risk category enumeration"""
    COMPLIANCE = "compliance"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    LEGAL = "legal"
    REPUTATIONAL = "reputational"
    TECHNICAL = "technical"


class ComplianceRiskAnalysisTool(Tool):
    """Tool for analyzing compliance risks"""
    
    def __init__(self):
        super().__init__("analyze_compliance", "Analyze compliance risks in documents")
    
    async def execute(self, content: str, doc_type: str, entities: List[Dict], **kwargs) -> Dict[str, Any]:
        """Analyze compliance risks"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            # Get compliance frameworks based on document type
            frameworks = self._get_compliance_frameworks(doc_type)
            
            system_prompt = f"""You are an expert compliance risk analyst. Analyze this {doc_type} document for compliance risks.
            
            COMPLIANCE FRAMEWORKS TO CHECK: {', '.join(frameworks)}
            
            For each compliance risk found, provide:
            - risk_type: Type of compliance risk
            - description: Detailed description of the risk
            - severity: LOW/MEDIUM/HIGH/CRITICAL
            - regulation: Specific regulation or standard violated
            - impact: Potential impact of non-compliance
            - recommendation: How to address the risk
            - confidence: Confidence score (0.0-1.0)
            
            Respond with JSON:
            {{
                "compliance_risks": [
                    {{
                        "risk_type": "risk_category",
                        "description": "detailed description",
                        "severity": "HIGH",
                        "regulation": "specific regulation",
                        "impact": "potential impact",
                        "recommendation": "how to address",
                        "confidence": 0.95
                    }}
                ],
                "overall_compliance_score": 0.85,
                "summary": "Overall compliance assessment"
            }}
            """
            
            # Include extracted entities for context
            entity_context = ""
            if entities:
                entity_context = f"\n\nEXTRACTED ENTITIES:\n{json.dumps(entities[:10], indent=2)}"
            
            user_prompt = f"Analyze compliance risks in this {doc_type} document:{entity_context}\n\n{content[:3000]}..."
            
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
                "compliance_risks": [],
                "overall_compliance_score": 0.0,
                "summary": f"Compliance analysis failed: {str(e)}"
            }
    
    def _get_compliance_frameworks(self, doc_type: str) -> List[str]:
        """Get compliance frameworks based on document type"""
        base_frameworks = ["General Business Standards", "Data Protection"]
        
        framework_mapping = {
            "contract": base_frameworks + ["Contract Law", "Industry Standards", "Data Privacy"],
            "invoice": base_frameworks + ["Tax Compliance", "Financial Reporting", "Vendor Management"],
            "policy": base_frameworks + ["Insurance Regulations", "Industry Standards", "Consumer Protection"],
            "regulation": base_frameworks + ["Regulatory Compliance", "Industry Standards", "Enforcement Requirements"],
            "financial_statement": base_frameworks + ["GAAP", "IFRS", "SEC Requirements", "Audit Standards"],
            "medical_record": base_frameworks + ["HIPAA", "Medical Privacy", "Clinical Standards", "Data Security"]
        }
        
        return framework_mapping.get(doc_type, base_frameworks)


class FinancialRiskAnalysisTool(Tool):
    """Tool for analyzing financial risks"""
    
    def __init__(self):
        super().__init__("analyze_financial", "Analyze financial risks in documents")
    
    async def execute(self, content: str, doc_type: str, entities: List[Dict], **kwargs) -> Dict[str, Any]:
        """Analyze financial risks"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            risk_types = self._get_financial_risk_types(doc_type)
            
            system_prompt = f"""You are an expert financial risk analyst. Analyze this {doc_type} document for financial risks.
            
            FINANCIAL RISK TYPES TO CHECK: {', '.join(risk_types)}
            
            For each financial risk found, provide:
            - risk_type: Type of financial risk
            - description: Detailed description of the risk
            - severity: LOW/MEDIUM/HIGH/CRITICAL
            - potential_loss: Estimated potential financial loss
            - probability: Likelihood of risk occurring (0.0-1.0)
            - mitigation: How to mitigate the risk
            - confidence: Confidence score (0.0-1.0)
            
            Respond with JSON:
            {{
                "financial_risks": [
                    {{
                        "risk_type": "risk_category",
                        "description": "detailed description",
                        "severity": "HIGH",
                        "potential_loss": "estimated loss amount",
                        "probability": 0.75,
                        "mitigation": "how to mitigate",
                        "confidence": 0.95
                    }}
                ],
                "total_potential_loss": "total estimated loss",
                "risk_score": 0.65,
                "summary": "Overall financial risk assessment"
            }}
            """
            
            # Include extracted entities for context
            entity_context = ""
            if entities:
                entity_context = f"\n\nEXTRACTED ENTITIES:\n{json.dumps(entities[:10], indent=2)}"
            
            user_prompt = f"Analyze financial risks in this {doc_type} document:{entity_context}\n\n{content[:3000]}..."
            
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
                "financial_risks": [],
                "total_potential_loss": "$0",
                "risk_score": 0.0,
                "summary": f"Financial analysis failed: {str(e)}"
            }
    
    def _get_financial_risk_types(self, doc_type: str) -> List[str]:
        """Get financial risk types based on document type"""
        base_types = ["Credit Risk", "Market Risk", "Operational Risk"]
        
        type_mapping = {
            "contract": base_types + ["Contractual Risk", "Payment Risk", "Liability Risk"],
            "invoice": base_types + ["Payment Default", "Tax Risk", "Billing Risk"],
            "policy": base_types + ["Claims Risk", "Premium Risk", "Coverage Risk"],
            "financial_statement": base_types + ["Reporting Risk", "Audit Risk", "Disclosure Risk"],
            "investment": base_types + ["Investment Risk", "Portfolio Risk", "Volatility Risk"]
        }
        
        return type_mapping.get(doc_type, base_types)


class OperationalRiskAnalysisTool(Tool):
    """Tool for analyzing operational risks"""
    
    def __init__(self):
        super().__init__("analyze_operational", "Analyze operational risks in documents")
    
    async def execute(self, content: str, doc_type: str, entities: List[Dict], **kwargs) -> Dict[str, Any]:
        """Analyze operational risks"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.1)
            
            risk_types = self._get_operational_risk_types(doc_type)
            
            system_prompt = f"""You are an expert operational risk analyst. Analyze this {doc_type} document for operational risks.
            
            OPERATIONAL RISK TYPES TO CHECK: {', '.join(risk_types)}
            
            For each operational risk found, provide:
            - risk_type: Type of operational risk
            - description: Detailed description of the risk
            - severity: LOW/MEDIUM/HIGH/CRITICAL
            - business_impact: Impact on business operations
            - likelihood: Likelihood of occurrence (0.0-1.0)
            - controls: Existing or recommended controls
            - confidence: Confidence score (0.0-1.0)
            
            Respond with JSON:
            {{
                "operational_risks": [
                    {{
                        "risk_type": "risk_category",
                        "description": "detailed description",
                        "severity": "HIGH",
                        "business_impact": "impact description",
                        "likelihood": 0.75,
                        "controls": "existing/recommended controls",
                        "confidence": 0.95
                    }}
                ],
                "operational_risk_score": 0.65,
                "summary": "Overall operational risk assessment"
            }}
            """
            
            # Include extracted entities for context
            entity_context = ""
            if entities:
                entity_context = f"\n\nEXTRACTED ENTITIES:\n{json.dumps(entities[:10], indent=2)}"
            
            user_prompt = f"Analyze operational risks in this {doc_type} document:{entity_context}\n\n{content[:3000]}..."
            
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
                "operational_risks": [],
                "operational_risk_score": 0.0,
                "summary": f"Operational analysis failed: {str(e)}"
            }
    
    def _get_operational_risk_types(self, doc_type: str) -> List[str]:
        """Get operational risk types based on document type"""
        base_types = ["Process Risk", "Technology Risk", "Human Risk"]
        
        type_mapping = {
            "contract": base_types + ["Vendor Risk", "Service Delivery Risk", "Contract Management Risk"],
            "policy": base_types + ["Claims Processing Risk", "Underwriting Risk", "Customer Service Risk"],
            "regulation": base_types + ["Compliance Monitoring Risk", "Reporting Risk", "Enforcement Risk"],
            "financial_statement": base_types + ["Financial Reporting Risk", "Audit Risk", "Data Quality Risk"],
            "medical_record": base_types + ["Patient Safety Risk", "Data Security Risk", "Clinical Process Risk"]
        }
        
        return type_mapping.get(doc_type, base_types)


class RiskScoringTool(Tool):
    """Tool for calculating overall risk scores"""
    
    def __init__(self):
        super().__init__("calculate_risk_score", "Calculate overall risk scores")
    
    async def execute(self, compliance_risks: List[Dict], financial_risks: List[Dict], operational_risks: List[Dict], **kwargs) -> Dict[str, Any]:
        """Calculate overall risk scores"""
        try:
            # Calculate risk scores by category
            compliance_score = self._calculate_category_score(compliance_risks)
            financial_score = self._calculate_category_score(financial_risks)
            operational_score = self._calculate_category_score(operational_risks)
            
            # Calculate weighted overall score
            weights = {
                "compliance": 0.4,
                "financial": 0.35,
                "operational": 0.25
            }
            
            overall_score = (
                compliance_score * weights["compliance"] +
                financial_score * weights["financial"] +
                operational_score * weights["operational"]
            )
            
            # Determine overall risk level
            risk_level = self._determine_risk_level(overall_score)
            
            # Get top risks
            all_risks = []
            for risk in compliance_risks:
                risk["category"] = "compliance"
                all_risks.append(risk)
            for risk in financial_risks:
                risk["category"] = "financial"
                all_risks.append(risk)
            for risk in operational_risks:
                risk["category"] = "operational"
                all_risks.append(risk)
            
            # Sort by severity and confidence
            all_risks.sort(key=lambda x: (
                self._severity_to_numeric(x.get("severity", "LOW")),
                x.get("confidence", 0)
            ), reverse=True)
            
            return {
                "overall_risk_score": overall_score,
                "risk_level": risk_level,
                "category_scores": {
                    "compliance": compliance_score,
                    "financial": financial_score,
                    "operational": operational_score
                },
                "top_risks": all_risks[:5],
                "risk_summary": {
                    "total_risks": len(all_risks),
                    "high_critical_risks": len([r for r in all_risks if r.get("severity") in ["HIGH", "CRITICAL"]]),
                    "recommendations": self._generate_recommendations(all_risks)
                }
            }
            
        except Exception as e:
            return {
                "overall_risk_score": 0.0,
                "risk_level": "UNKNOWN",
                "category_scores": {},
                "top_risks": [],
                "risk_summary": {
                    "total_risks": 0,
                    "high_critical_risks": 0,
                    "recommendations": [f"Risk scoring failed: {str(e)}"]
                }
            }
    
    def _calculate_category_score(self, risks: List[Dict]) -> float:
        """Calculate risk score for a category"""
        if not risks:
            return 0.0
        
        severity_weights = {
            "LOW": 0.25,
            "MEDIUM": 0.5,
            "HIGH": 0.75,
            "CRITICAL": 1.0
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for risk in risks:
            severity = risk.get("severity", "LOW")
            confidence = risk.get("confidence", 0.5)
            weight = severity_weights.get(severity, 0.25)
            
            total_score += weight * confidence
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _determine_risk_level(self, score: float) -> str:
        """Determine risk level based on score"""
        if score >= 0.8:
            return "CRITICAL"
        elif score >= 0.6:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _severity_to_numeric(self, severity: str) -> int:
        """Convert severity to numeric for sorting"""
        severity_map = {
            "CRITICAL": 4,
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1
        }
        return severity_map.get(severity.upper(), 1)
    
    def _generate_recommendations(self, risks: List[Dict]) -> List[str]:
        """Generate recommendations based on risks"""
        recommendations = []
        
        high_critical_risks = [r for r in risks if r.get("severity") in ["HIGH", "CRITICAL"]]
        
        if len(high_critical_risks) > 5:
            recommendations.append("Immediate action required: Document has 5+ high/critical risks")
        
        compliance_risks = [r for r in high_critical_risks if r.get("category") == "compliance"]
        if compliance_risks:
            recommendations.append("Legal review recommended for compliance risks")
        
        financial_risks = [r for r in high_critical_risks if r.get("category") == "financial"]
        if financial_risks:
            recommendations.append("Financial review recommended for monetary risks")
        
        if not recommendations:
            recommendations.append("Document appears to have acceptable risk levels")
        
        return recommendations


class RiskAgent(BaseAgent):
    """Agent responsible for risk assessment and analysis"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__("RiskAgent", AgentType.RISK)
        self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
        
        # Add tools
        self.add_tool(ComplianceRiskAnalysisTool())
        self.add_tool(FinancialRiskAnalysisTool())
        self.add_tool(OperationalRiskAnalysisTool())
        self.add_tool(RiskScoringTool())
    
    async def run(self, goal: str, context: Dict[str, Any]) -> AgentResult:
        """Main risk assessment process"""
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
            entities = document.metadata.get("entities", [])
            
            # Analyze compliance risks
            compliance_tool = self.get_tool("analyze_compliance")
            compliance_analysis = await compliance_tool.execute(
                content=document.content,
                doc_type=doc_type,
                entities=entities
            )
            
            # Analyze financial risks
            financial_tool = self.get_tool("analyze_financial")
            financial_analysis = await financial_tool.execute(
                content=document.content,
                doc_type=doc_type,
                entities=entities
            )
            
            # Analyze operational risks
            operational_tool = self.get_tool("analyze_operational")
            operational_analysis = await operational_tool.execute(
                content=document.content,
                doc_type=doc_type,
                entities=entities
            )
            
            # Calculate overall risk scores
            scoring_tool = self.get_tool("calculate_risk_score")
            risk_scores = await scoring_tool.execute(
                compliance_risks=compliance_analysis.get("compliance_risks", []),
                financial_risks=financial_analysis.get("financial_risks", []),
                operational_risks=operational_analysis.get("operational_risks", [])
            )
            
            # Update document metadata
            document.metadata.update({
                "risk_assessment": {
                    "compliance": compliance_analysis,
                    "financial": financial_analysis,
                    "operational": operational_analysis,
                    "overall": risk_scores,
                    "assessed_at": datetime.utcnow().isoformat()
                }
            })
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                compliance_analysis,
                financial_analysis,
                operational_analysis
            )
            
            # Generate rationale
            total_risks = risk_scores.get("risk_summary", {}).get("total_risks", 0)
            high_critical = risk_scores.get("risk_summary", {}).get("high_critical_risks", 0)
            risk_level = risk_scores.get("risk_level", "UNKNOWN")
            
            rationale = f"Risk assessment completed: {total_risks} total risks identified, {high_critical} high/critical risks. Overall risk level: {risk_level}"
            
            return AgentResult(
                output=document,
                rationale=rationale,
                confidence=confidence,
                next_suggested_action="Proceed to QA generation",
                metadata={
                    "compliance_analysis": compliance_analysis,
                    "financial_analysis": financial_analysis,
                    "operational_analysis": operational_analysis,
                    "risk_scores": risk_scores
                }
            )
            
        except Exception as e:
            return AgentResult(
                output=None,
                rationale=f"Risk assessment failed: {str(e)}",
                confidence=0.0,
                next_suggested_action="Manual risk assessment required"
            )
    
    def _calculate_confidence(self, compliance_analysis: Dict, financial_analysis: Dict, operational_analysis: Dict) -> float:
        """Calculate confidence based on analysis results"""
        confidence = 0.5  # Base confidence
        
        # Compliance confidence
        compliance_score = compliance_analysis.get("overall_compliance_score", 0.0)
        confidence += compliance_score * 0.2
        
        # Financial confidence
        financial_score = financial_analysis.get("risk_score", 0.0)
        confidence += (1.0 - financial_score) * 0.2  # Lower risk = higher confidence
        
        # Operational confidence
        operational_score = operational_analysis.get("operational_risk_score", 0.0)
        confidence += (1.0 - operational_score) * 0.2  # Lower risk = higher confidence
        
        # Analysis completeness
        total_risks = (
            len(compliance_analysis.get("compliance_risks", [])) +
            len(financial_analysis.get("financial_risks", [])) +
            len(operational_analysis.get("operational_risks", []))
        )
        
        if total_risks > 0:
            confidence += 0.1
        
        return min(1.0, max(0.0, confidence))
