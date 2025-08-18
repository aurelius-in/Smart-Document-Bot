import json
import re
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from .base import BaseAgent, Tool
from ..models.base import AgentResult, AgentType, Document


class QuestionType(Enum):
    """Question type enumeration"""
    FACTUAL = "factual"
    ANALYTICAL = "analytical"
    COMPLIANCE = "compliance"
    RISK = "risk"
    ACTION = "action"


class QuestionDifficulty(Enum):
    """Question difficulty enumeration"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class FactualQuestionGeneratorTool(Tool):
    """Tool for generating factual questions about document content"""
    
    def __init__(self):
        super().__init__("generate_factual", "Generate factual questions about document content")
    
    async def execute(self, content: str, doc_type: str, entities: List[Dict], **kwargs) -> List[Dict[str, Any]]:
        """Generate factual questions"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.3)
            
            system_prompt = f"""You are an expert document analyst. Generate factual questions about this {doc_type} document.
            
            For each question, provide:
            - question: Clear, specific question about document content
            - answer: Accurate answer based on document content
            - difficulty: EASY/MEDIUM/HARD
            - category: Specific category (dates, amounts, parties, terms, etc.)
            - confidence: Confidence in answer accuracy (0.0-1.0)
            - source_location: Where in document the answer can be found
            
            Generate 5-8 factual questions covering key information.
            
            Respond with JSON array:
            [
                {{
                    "question": "What is the effective date of this contract?",
                    "answer": "January 1, 2024",
                    "difficulty": "EASY",
                    "category": "dates",
                    "confidence": 0.95,
                    "source_location": "Section 1.1, page 1"
                }}
            ]
            """
            
            # Include extracted entities for context
            entity_context = ""
            if entities:
                entity_context = f"\n\nKEY ENTITIES:\n{json.dumps(entities[:10], indent=2)}"
            
            user_prompt = f"Generate factual questions about this {doc_type} document:{entity_context}\n\n{content[:3000]}..."
            
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
            
            questions = json.loads(result_text)
            
            # Validate questions
            valid_questions = []
            for question in questions:
                if self._validate_question(question):
                    valid_questions.append(question)
            
            return valid_questions
            
        except Exception as e:
            return []
    
    def _validate_question(self, question: Dict[str, Any]) -> bool:
        """Validate generated question"""
        required_fields = ["question", "answer", "difficulty", "category", "confidence", "source_location"]
        
        # Check required fields
        for field in required_fields:
            if field not in question:
                return False
        
        # Validate difficulty
        difficulty = question.get("difficulty", "").upper()
        if difficulty not in ["EASY", "MEDIUM", "HARD"]:
            return False
        
        # Validate confidence
        confidence = question.get("confidence", 0)
        if not (0.0 <= confidence <= 1.0):
            return False
        
        # Validate question and answer are not empty
        if not question.get("question", "").strip() or not question.get("answer", "").strip():
            return False
        
        return True


class ComplianceQuestionGeneratorTool(Tool):
    """Tool for generating compliance-related questions"""
    
    def __init__(self):
        super().__init__("generate_compliance", "Generate compliance-related questions")
    
    async def execute(self, content: str, doc_type: str, risk_assessment: Dict, **kwargs) -> List[Dict[str, Any]]:
        """Generate compliance questions"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.3)
            
            system_prompt = f"""You are an expert compliance analyst. Generate compliance-related questions about this {doc_type} document.
            
            Focus on:
            - Regulatory compliance requirements
            - Policy adherence
            - Legal obligations
            - Industry standards
            - Risk mitigation measures
            
            For each question, provide:
            - question: Compliance-focused question
            - answer: Detailed compliance assessment
            - difficulty: EASY/MEDIUM/HARD
            - compliance_area: Specific compliance area
            - risk_level: LOW/MEDIUM/HIGH/CRITICAL
            - recommendation: Compliance recommendation
            - confidence: Confidence in assessment (0.0-1.0)
            
            Generate 3-5 compliance questions.
            
            Respond with JSON array:
            [
                {{
                    "question": "Does this contract comply with data privacy regulations?",
                    "answer": "The contract includes standard data protection clauses but lacks specific GDPR compliance measures.",
                    "difficulty": "MEDIUM",
                    "compliance_area": "data_privacy",
                    "risk_level": "MEDIUM",
                    "recommendation": "Add GDPR-specific clauses and data processing agreements",
                    "confidence": 0.85
                }}
            ]
            """
            
            # Include risk assessment context
            risk_context = ""
            if risk_assessment:
                risk_context = f"\n\nRISK ASSESSMENT:\n{json.dumps(risk_assessment, indent=2)}"
            
            user_prompt = f"Generate compliance questions about this {doc_type} document:{risk_context}\n\n{content[:3000]}..."
            
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
            
            questions = json.loads(result_text)
            
            # Validate questions
            valid_questions = []
            for question in questions:
                if self._validate_compliance_question(question):
                    valid_questions.append(question)
            
            return valid_questions
            
        except Exception as e:
            return []
    
    def _validate_compliance_question(self, question: Dict[str, Any]) -> bool:
        """Validate compliance question"""
        required_fields = ["question", "answer", "difficulty", "compliance_area", "risk_level", "recommendation", "confidence"]
        
        # Check required fields
        for field in required_fields:
            if field not in question:
                return False
        
        # Validate difficulty
        difficulty = question.get("difficulty", "").upper()
        if difficulty not in ["EASY", "MEDIUM", "HARD"]:
            return False
        
        # Validate risk level
        risk_level = question.get("risk_level", "").upper()
        if risk_level not in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            return False
        
        # Validate confidence
        confidence = question.get("confidence", 0)
        if not (0.0 <= confidence <= 1.0):
            return False
        
        return True


class RiskQuestionGeneratorTool(Tool):
    """Tool for generating risk-focused questions"""
    
    def __init__(self):
        super().__init__("generate_risk", "Generate risk-focused questions")
    
    async def execute(self, content: str, doc_type: str, risk_assessment: Dict, **kwargs) -> List[Dict[str, Any]]:
        """Generate risk questions"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.3)
            
            system_prompt = f"""You are an expert risk analyst. Generate risk-focused questions about this {doc_type} document.
            
            Focus on:
            - Financial risks
            - Operational risks
            - Legal risks
            - Reputational risks
            - Mitigation strategies
            
            For each question, provide:
            - question: Risk-focused question
            - answer: Detailed risk analysis
            - difficulty: EASY/MEDIUM/HARD
            - risk_category: Specific risk category
            - severity: LOW/MEDIUM/HIGH/CRITICAL
            - mitigation: Risk mitigation strategy
            - confidence: Confidence in analysis (0.0-1.0)
            
            Generate 3-5 risk questions.
            
            Respond with JSON array:
            [
                {{
                    "question": "What are the main financial risks in this contract?",
                    "answer": "The contract exposes the company to payment default risk ($50K), liability risk (unlimited), and currency fluctuation risk.",
                    "difficulty": "HARD",
                    "risk_category": "financial",
                    "severity": "HIGH",
                    "mitigation": "Implement payment guarantees, limit liability clauses, and hedge currency exposure",
                    "confidence": 0.9
                }}
            ]
            """
            
            # Include risk assessment context
            risk_context = ""
            if risk_assessment:
                risk_context = f"\n\nRISK ASSESSMENT:\n{json.dumps(risk_assessment, indent=2)}"
            
            user_prompt = f"Generate risk questions about this {doc_type} document:{risk_context}\n\n{content[:3000]}..."
            
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
            
            questions = json.loads(result_text)
            
            # Validate questions
            valid_questions = []
            for question in questions:
                if self._validate_risk_question(question):
                    valid_questions.append(question)
            
            return valid_questions
            
        except Exception as e:
            return []
    
    def _validate_risk_question(self, question: Dict[str, Any]) -> bool:
        """Validate risk question"""
        required_fields = ["question", "answer", "difficulty", "risk_category", "severity", "mitigation", "confidence"]
        
        # Check required fields
        for field in required_fields:
            if field not in question:
                return False
        
        # Validate difficulty
        difficulty = question.get("difficulty", "").upper()
        if difficulty not in ["EASY", "MEDIUM", "HARD"]:
            return False
        
        # Validate severity
        severity = question.get("severity", "").upper()
        if severity not in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            return False
        
        # Validate confidence
        confidence = question.get("confidence", 0)
        if not (0.0 <= confidence <= 1.0):
            return False
        
        return True


class ActionQuestionGeneratorTool(Tool):
    """Tool for generating action-oriented questions"""
    
    def __init__(self):
        super().__init__("generate_action", "Generate action-oriented questions")
    
    async def execute(self, content: str, doc_type: str, entities: List[Dict], risk_assessment: Dict, **kwargs) -> List[Dict[str, Any]]:
        """Generate action questions"""
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = ChatOpenAI(model="gpt-4", temperature=0.3)
            
            system_prompt = f"""You are an expert business analyst. Generate action-oriented questions about this {doc_type} document.
            
            Focus on:
            - Required actions
            - Deadlines and timelines
            - Responsibilities and obligations
            - Next steps
            - Decision points
            
            For each question, provide:
            - question: Action-focused question
            - answer: Detailed action plan or response
            - difficulty: EASY/MEDIUM/HARD
            - action_type: Type of action required
            - priority: HIGH/MEDIUM/LOW
            - timeline: When action is needed
            - responsible_party: Who should take action
            - confidence: Confidence in assessment (0.0-1.0)
            
            Generate 3-5 action questions.
            
            Respond with JSON array:
            [
                {{
                    "question": "What actions are required within 30 days of contract signing?",
                    "answer": "1. Set up payment processing system, 2. Assign contract manager, 3. Schedule kickoff meeting, 4. Begin vendor onboarding process",
                    "difficulty": "MEDIUM",
                    "action_type": "implementation",
                    "priority": "HIGH",
                    "timeline": "30 days",
                    "responsible_party": "Project Manager",
                    "confidence": 0.9
                }}
            ]
            """
            
            # Include context
            context = ""
            if entities:
                context += f"\n\nKEY ENTITIES:\n{json.dumps(entities[:10], indent=2)}"
            if risk_assessment:
                context += f"\n\nRISK ASSESSMENT:\n{json.dumps(risk_assessment, indent=2)}"
            
            user_prompt = f"Generate action questions about this {doc_type} document:{context}\n\n{content[:3000]}..."
            
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
            
            questions = json.loads(result_text)
            
            # Validate questions
            valid_questions = []
            for question in questions:
                if self._validate_action_question(question):
                    valid_questions.append(question)
            
            return valid_questions
            
        except Exception as e:
            return []
    
    def _validate_action_question(self, question: Dict[str, Any]) -> bool:
        """Validate action question"""
        required_fields = ["question", "answer", "difficulty", "action_type", "priority", "timeline", "responsible_party", "confidence"]
        
        # Check required fields
        for field in required_fields:
            if field not in question:
                return False
        
        # Validate difficulty
        difficulty = question.get("difficulty", "").upper()
        if difficulty not in ["EASY", "MEDIUM", "HARD"]:
            return False
        
        # Validate priority
        priority = question.get("priority", "").upper()
        if priority not in ["HIGH", "MEDIUM", "LOW"]:
            return False
        
        # Validate confidence
        confidence = question.get("confidence", 0)
        if not (0.0 <= confidence <= 1.0):
            return False
        
        return True


class QASummaryGeneratorTool(Tool):
    """Tool for generating QA summary and insights"""
    
    def __init__(self):
        super().__init__("generate_summary", "Generate QA summary and insights")
    
    async def execute(self, all_questions: List[Dict], doc_type: str, **kwargs) -> Dict[str, Any]:
        """Generate QA summary"""
        try:
            # Categorize questions
            factual_questions = [q for q in all_questions if "category" in q]
            compliance_questions = [q for q in all_questions if "compliance_area" in q]
            risk_questions = [q for q in all_questions if "risk_category" in q]
            action_questions = [q for q in all_questions if "action_type" in q]
            
            # Calculate statistics
            total_questions = len(all_questions)
            avg_confidence = sum(q.get("confidence", 0) for q in all_questions) / total_questions if total_questions > 0 else 0
            
            # Difficulty distribution
            difficulty_dist = {"EASY": 0, "MEDIUM": 0, "HARD": 0}
            for q in all_questions:
                difficulty = q.get("difficulty", "MEDIUM").upper()
                difficulty_dist[difficulty] += 1
            
            # Priority distribution (for action questions)
            priority_dist = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
            for q in action_questions:
                priority = q.get("priority", "MEDIUM").upper()
                priority_dist[priority] += 1
            
            # Risk level distribution (for risk questions)
            risk_dist = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
            for q in risk_questions:
                risk_level = q.get("severity", "MEDIUM").upper()
                risk_dist[risk_level] += 1
            
            # Generate insights
            insights = []
            
            if factual_questions:
                insights.append(f"Generated {len(factual_questions)} factual questions covering key document information")
            
            if compliance_questions:
                high_risk_compliance = [q for q in compliance_questions if q.get("risk_level") in ["HIGH", "CRITICAL"]]
                insights.append(f"Identified {len(high_risk_compliance)} high/critical compliance concerns")
            
            if risk_questions:
                high_risk = [q for q in risk_questions if q.get("severity") in ["HIGH", "CRITICAL"]]
                insights.append(f"Found {len(high_risk)} high/critical risk areas requiring attention")
            
            if action_questions:
                high_priority_actions = [q for q in action_questions if q.get("priority") == "HIGH"]
                insights.append(f"Identified {len(high_priority_actions)} high-priority actions")
            
            return {
                "summary": {
                    "total_questions": total_questions,
                    "question_types": {
                        "factual": len(factual_questions),
                        "compliance": len(compliance_questions),
                        "risk": len(risk_questions),
                        "action": len(action_questions)
                    },
                    "average_confidence": avg_confidence,
                    "difficulty_distribution": difficulty_dist,
                    "priority_distribution": priority_dist,
                    "risk_distribution": risk_dist
                },
                "insights": insights,
                "recommendations": self._generate_recommendations(all_questions)
            }
            
        except Exception as e:
            return {
                "summary": {},
                "insights": [f"Summary generation failed: {str(e)}"],
                "recommendations": ["Manual review required"]
            }
    
    def _generate_recommendations(self, questions: List[Dict]) -> List[str]:
        """Generate recommendations based on questions"""
        recommendations = []
        
        # Check for high-risk items
        high_risk_compliance = [q for q in questions if q.get("risk_level") in ["HIGH", "CRITICAL"]]
        if high_risk_compliance:
            recommendations.append("Immediate attention required for high-risk compliance issues")
        
        high_risk = [q for q in questions if q.get("severity") in ["HIGH", "CRITICAL"]]
        if high_risk:
            recommendations.append("Urgent action needed for high/critical risk areas")
        
        # Check for high-priority actions
        high_priority = [q for q in questions if q.get("priority") == "HIGH"]
        if high_priority:
            recommendations.append("Prioritize high-priority action items")
        
        # Check confidence levels
        low_confidence = [q for q in questions if q.get("confidence", 1) < 0.7]
        if low_confidence:
            recommendations.append("Review low-confidence assessments for accuracy")
        
        if not recommendations:
            recommendations.append("Document appears well-structured with manageable risks")
        
        return recommendations


class QAAgent(BaseAgent):
    """Agent responsible for generating questions and answers"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__("QAAgent", AgentType.QA)
        self.llm = ChatOpenAI(model=llm_model, temperature=0.3)
        
        # Add tools
        self.add_tool(FactualQuestionGeneratorTool())
        self.add_tool(ComplianceQuestionGeneratorTool())
        self.add_tool(RiskQuestionGeneratorTool())
        self.add_tool(ActionQuestionGeneratorTool())
        self.add_tool(QASummaryGeneratorTool())
    
    async def run(self, goal: str, context: Dict[str, Any]) -> AgentResult:
        """Main QA generation process"""
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
            risk_assessment = document.metadata.get("risk_assessment", {})
            
            # Generate factual questions
            factual_tool = self.get_tool("generate_factual")
            factual_questions = await factual_tool.execute(
                content=document.content,
                doc_type=doc_type,
                entities=entities
            )
            
            # Generate compliance questions
            compliance_tool = self.get_tool("generate_compliance")
            compliance_questions = await compliance_tool.execute(
                content=document.content,
                doc_type=doc_type,
                risk_assessment=risk_assessment
            )
            
            # Generate risk questions
            risk_tool = self.get_tool("generate_risk")
            risk_questions = await risk_tool.execute(
                content=document.content,
                doc_type=doc_type,
                risk_assessment=risk_assessment
            )
            
            # Generate action questions
            action_tool = self.get_tool("generate_action")
            action_questions = await action_tool.execute(
                content=document.content,
                doc_type=doc_type,
                entities=entities,
                risk_assessment=risk_assessment
            )
            
            # Combine all questions
            all_questions = factual_questions + compliance_questions + risk_questions + action_questions
            
            # Generate summary
            summary_tool = self.get_tool("generate_summary")
            qa_summary = await summary_tool.execute(
                all_questions=all_questions,
                doc_type=doc_type
            )
            
            # Update document metadata
            document.metadata.update({
                "qa_generation": {
                    "questions": all_questions,
                    "summary": qa_summary,
                    "generated_at": datetime.utcnow().isoformat()
                }
            })
            
            # Calculate confidence
            confidence = self._calculate_confidence(all_questions, qa_summary)
            
            # Generate rationale
            total_questions = len(all_questions)
            question_types = qa_summary.get("summary", {}).get("question_types", {})
            
            rationale = f"Generated {total_questions} questions: {question_types.get('factual', 0)} factual, {question_types.get('compliance', 0)} compliance, {question_types.get('risk', 0)} risk, {question_types.get('action', 0)} action questions"
            
            return AgentResult(
                output=document,
                rationale=rationale,
                confidence=confidence,
                next_suggested_action="Proceed to document comparison",
                metadata={
                    "questions": all_questions,
                    "summary": qa_summary
                }
            )
            
        except Exception as e:
            return AgentResult(
                output=None,
                rationale=f"QA generation failed: {str(e)}",
                confidence=0.0,
                next_suggested_action="Manual QA generation required"
            )
    
    def _calculate_confidence(self, questions: List[Dict], summary: Dict) -> float:
        """Calculate confidence based on QA generation results"""
        confidence = 0.5  # Base confidence
        
        # Question quantity and quality
        if len(questions) >= 10:
            confidence += 0.2
        elif len(questions) >= 5:
            confidence += 0.1
        
        # Average confidence of questions
        if questions:
            avg_question_confidence = sum(q.get("confidence", 0) for q in questions) / len(questions)
            confidence += avg_question_confidence * 0.2
        
        # Summary completeness
        summary_data = summary.get("summary", {})
        if summary_data.get("total_questions", 0) > 0:
            confidence += 0.1
        
        # Insights quality
        insights = summary.get("insights", [])
        if len(insights) >= 3:
            confidence += 0.1
        
        return min(1.0, max(0.0, confidence))
