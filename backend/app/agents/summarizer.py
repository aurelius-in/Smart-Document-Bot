from typing import Dict, Any, List, Optional
import json
import re
from datetime import datetime
import uuid

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

from .base import BaseAgent, AgentResult
from ..core.config import get_settings

settings = get_settings()

class SummarizerAgent(BaseAgent):
    """Agent for generating comprehensive document summaries"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__(agent_type="summarizer", llm_model=llm_model)
        self.llm = ChatOpenAI(
            model=llm_model,
            temperature=0.1,
            max_tokens=4000,
            openai_api_key=settings.LLM_API_KEY
        )
        
        # Initialize tools
        self.tools = {
            "extractive_summary": self.extractive_summary_tool,
            "abstractive_summary": self.abstractive_summary_tool,
            "executive_summary": self.executive_summary_tool,
            "technical_summary": self.technical_summary_tool,
            "key_points_extraction": self.key_points_extraction_tool,
            "summary_comparison": self.summary_comparison_tool,
            "summary_validation": self.summary_validation_tool
        }
    
    def extractive_summary_tool(self, document_content: str, summary_length: str = "medium", 
                               focus_areas: List[str] = None) -> Dict[str, Any]:
        """Generate extractive summary by selecting key sentences"""
        
        system_prompt = """You are an expert document summarizer specializing in extractive summarization. 
        Your task is to identify and extract the most important sentences from the document to create a coherent summary.
        
        Guidelines:
        - Select sentences that contain key information, facts, and important details
        - Maintain the original wording of selected sentences
        - Ensure the summary flows logically
        - Focus on the specified areas if provided
        - Respect the requested summary length
        
        Summary lengths:
        - short: 2-3 sentences
        - medium: 4-6 sentences  
        - long: 8-10 sentences
        
        Return a JSON object with:
        - summary: the extracted summary text
        - selected_sentences: list of sentence indices used
        - key_topics: main topics covered
        - confidence_score: confidence in the summary quality (0-1)
        - rationale: explanation of selection criteria
        """
        
        focus_text = ""
        if focus_areas:
            focus_text = f"\nFocus areas: {', '.join(focus_areas)}"
        
        human_prompt = f"""Document content:
{document_content}

Generate an extractive summary with length: {summary_length}{focus_text}

Provide the summary in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Validate and enhance result
            confidence = self._calculate_extractive_confidence(
                result.get("selected_sentences", []), 
                len(document_content.split('.'))
            )
            
            return {
                "summary": result.get("summary", ""),
                "selected_sentences": result.get("selected_sentences", []),
                "key_topics": result.get("key_topics", []),
                "confidence_score": confidence,
                "rationale": result.get("rationale", ""),
                "summary_length": summary_length,
                "focus_areas": focus_areas or [],
                "extraction_method": "extractive"
            }
            
        except Exception as e:
            return {
                "summary": "",
                "selected_sentences": [],
                "key_topics": [],
                "confidence_score": 0.0,
                "rationale": f"Error in extractive summarization: {str(e)}",
                "summary_length": summary_length,
                "focus_areas": focus_areas or [],
                "extraction_method": "extractive"
            }
    
    def abstractive_summary_tool(self, document_content: str, summary_style: str = "informative",
                                target_audience: str = "general") -> Dict[str, Any]:
        """Generate abstractive summary by creating new text"""
        
        system_prompt = """You are an expert document summarizer specializing in abstractive summarization.
        Your task is to understand the document content and create a new, coherent summary that captures the essence.
        
        Guidelines:
        - Create new sentences that capture the main ideas
        - Maintain accuracy and factual correctness
        - Adapt the style and complexity for the target audience
        - Focus on the most important information
        - Ensure logical flow and coherence
        
        Summary styles:
        - informative: factual and comprehensive
        - narrative: story-like and engaging
        - analytical: focused on analysis and insights
        - technical: detailed and precise
        
        Target audiences:
        - general: accessible to everyone
        - professional: for business/industry professionals
        - technical: for subject matter experts
        - executive: high-level for decision makers
        
        Return a JSON object with:
        - summary: the generated summary text
        - main_ideas: list of key ideas covered
        - tone: the tone/style used
        - confidence_score: confidence in the summary quality (0-1)
        - rationale: explanation of summarization approach
        """
        
        human_prompt = f"""Document content:
{document_content}

Generate an abstractive summary with style: {summary_style} for audience: {target_audience}

Provide the summary in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Validate and enhance result
            confidence = self._calculate_abstractive_confidence(
                result.get("summary", ""), 
                document_content
            )
            
            return {
                "summary": result.get("summary", ""),
                "main_ideas": result.get("main_ideas", []),
                "tone": result.get("tone", summary_style),
                "confidence_score": confidence,
                "rationale": result.get("rationale", ""),
                "summary_style": summary_style,
                "target_audience": target_audience,
                "extraction_method": "abstractive"
            }
            
        except Exception as e:
            return {
                "summary": "",
                "main_ideas": [],
                "tone": summary_style,
                "confidence_score": 0.0,
                "rationale": f"Error in abstractive summarization: {str(e)}",
                "summary_style": summary_style,
                "target_audience": target_audience,
                "extraction_method": "abstractive"
            }
    
    def executive_summary_tool(self, document_content: str, business_context: str = "general") -> Dict[str, Any]:
        """Generate executive summary for business decision makers"""
        
        system_prompt = """You are an expert business analyst creating executive summaries for senior decision makers.
        Your task is to create a concise, high-level summary that highlights key business implications and recommendations.
        
        Guidelines:
        - Focus on business impact and strategic implications
        - Highlight key risks, opportunities, and recommendations
        - Use clear, actionable language
        - Include financial implications if relevant
        - Structure with clear sections (Overview, Key Findings, Recommendations)
        - Keep it concise but comprehensive
        
        Business contexts:
        - general: broad business perspective
        - financial: focus on financial implications
        - legal: focus on legal/regulatory aspects
        - operational: focus on operational impact
        - strategic: focus on strategic implications
        
        Return a JSON object with:
        - executive_summary: the complete executive summary
        - key_findings: list of main findings
        - recommendations: list of actionable recommendations
        - business_impact: assessment of business impact
        - risk_assessment: key risks identified
        - confidence_score: confidence in the summary quality (0-1)
        """
        
        human_prompt = f"""Document content:
{document_content}

Generate an executive summary for business context: {business_context}

Provide the summary in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Validate and enhance result
            confidence = self._calculate_executive_confidence(
                result.get("key_findings", []),
                result.get("recommendations", [])
            )
            
            return {
                "executive_summary": result.get("executive_summary", ""),
                "key_findings": result.get("key_findings", []),
                "recommendations": result.get("recommendations", []),
                "business_impact": result.get("business_impact", ""),
                "risk_assessment": result.get("risk_assessment", ""),
                "confidence_score": confidence,
                "business_context": business_context,
                "summary_type": "executive"
            }
            
        except Exception as e:
            return {
                "executive_summary": "",
                "key_findings": [],
                "recommendations": [],
                "business_impact": "",
                "risk_assessment": "",
                "confidence_score": 0.0,
                "business_context": business_context,
                "summary_type": "executive"
            }
    
    def technical_summary_tool(self, document_content: str, technical_domain: str = "general") -> Dict[str, Any]:
        """Generate technical summary for subject matter experts"""
        
        system_prompt = """You are an expert technical analyst creating detailed technical summaries.
        Your task is to create a comprehensive technical summary that covers all technical aspects and details.
        
        Guidelines:
        - Include technical specifications, methodologies, and procedures
        - Highlight technical innovations, challenges, and solutions
        - Use appropriate technical terminology
        - Include data, metrics, and technical findings
        - Structure with technical sections (Methodology, Results, Technical Details)
        - Maintain technical accuracy and precision
        
        Technical domains:
        - general: broad technical perspective
        - software: focus on software/IT aspects
        - engineering: focus on engineering details
        - scientific: focus on scientific methodology
        - medical: focus on medical/healthcare aspects
        
        Return a JSON object with:
        - technical_summary: the complete technical summary
        - technical_specifications: list of technical specs
        - methodologies: list of methods used
        - technical_findings: list of technical findings
        - technical_challenges: list of challenges identified
        - confidence_score: confidence in the summary quality (0-1)
        """
        
        human_prompt = f"""Document content:
{document_content}

Generate a technical summary for domain: {technical_domain}

Provide the summary in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Validate and enhance result
            confidence = self._calculate_technical_confidence(
                result.get("technical_specifications", []),
                result.get("methodologies", [])
            )
            
            return {
                "technical_summary": result.get("technical_summary", ""),
                "technical_specifications": result.get("technical_specifications", []),
                "methodologies": result.get("methodologies", []),
                "technical_findings": result.get("technical_findings", []),
                "technical_challenges": result.get("technical_challenges", []),
                "confidence_score": confidence,
                "technical_domain": technical_domain,
                "summary_type": "technical"
            }
            
        except Exception as e:
            return {
                "technical_summary": "",
                "technical_specifications": [],
                "methodologies": [],
                "technical_findings": [],
                "technical_challenges": [],
                "confidence_score": 0.0,
                "technical_domain": technical_domain,
                "summary_type": "technical"
            }
    
    def key_points_extraction_tool(self, document_content: str, point_categories: List[str] = None) -> Dict[str, Any]:
        """Extract key points organized by categories"""
        
        if not point_categories:
            point_categories = ["main_points", "key_facts", "important_dates", "critical_issues"]
        
        system_prompt = """You are an expert at extracting and categorizing key points from documents.
        Your task is to identify and organize the most important information into logical categories.
        
        Guidelines:
        - Extract factual, actionable, and important information
        - Organize points into the specified categories
        - Ensure accuracy and relevance
        - Provide context for each point when necessary
        - Prioritize points by importance
        
        Return a JSON object with:
        - categorized_points: object with category names as keys and lists of points as values
        - point_count: total number of points extracted
        - importance_ranking: ranking of points by importance
        - confidence_score: confidence in the extraction quality (0-1)
        """
        
        categories_text = ", ".join(point_categories)
        
        human_prompt = f"""Document content:
{document_content}

Extract key points organized into these categories: {categories_text}

Provide the results in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Validate and enhance result
            confidence = self._calculate_key_points_confidence(
                result.get("categorized_points", {}),
                len(document_content.split())
            )
            
            return {
                "categorized_points": result.get("categorized_points", {}),
                "point_count": result.get("point_count", 0),
                "importance_ranking": result.get("importance_ranking", []),
                "confidence_score": confidence,
                "point_categories": point_categories,
                "extraction_method": "categorized"
            }
            
        except Exception as e:
            return {
                "categorized_points": {},
                "point_count": 0,
                "importance_ranking": [],
                "confidence_score": 0.0,
                "point_categories": point_categories,
                "extraction_method": "categorized"
            }
    
    def summary_comparison_tool(self, summary_a: str, summary_b: str, comparison_criteria: List[str] = None) -> Dict[str, Any]:
        """Compare two summaries and identify differences"""
        
        if not comparison_criteria:
            comparison_criteria = ["completeness", "accuracy", "clarity", "coverage"]
        
        system_prompt = """You are an expert at comparing and evaluating document summaries.
        Your task is to compare two summaries and identify their relative strengths and differences.
        
        Guidelines:
        - Compare summaries based on the specified criteria
        - Identify unique information in each summary
        - Assess relative quality and completeness
        - Provide specific examples of differences
        - Give balanced, objective assessment
        
        Return a JSON object with:
        - comparison_results: detailed comparison for each criterion
        - unique_information_a: information only in summary A
        - unique_information_b: information only in summary B
        - quality_assessment: overall quality comparison
        - recommendations: suggestions for improvement
        - confidence_score: confidence in the comparison (0-1)
        """
        
        criteria_text = ", ".join(comparison_criteria)
        
        human_prompt = f"""Summary A:
{summary_a}

Summary B:
{summary_b}

Compare these summaries based on: {criteria_text}

Provide the comparison in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Validate and enhance result
            confidence = self._calculate_comparison_confidence(
                result.get("comparison_results", {}),
                len(summary_a) + len(summary_b)
            )
            
            return {
                "comparison_results": result.get("comparison_results", {}),
                "unique_information_a": result.get("unique_information_a", []),
                "unique_information_b": result.get("unique_information_b", []),
                "quality_assessment": result.get("quality_assessment", ""),
                "recommendations": result.get("recommendations", []),
                "confidence_score": confidence,
                "comparison_criteria": comparison_criteria,
                "comparison_method": "criteria_based"
            }
            
        except Exception as e:
            return {
                "comparison_results": {},
                "unique_information_a": [],
                "unique_information_b": [],
                "quality_assessment": "",
                "recommendations": [],
                "confidence_score": 0.0,
                "comparison_criteria": comparison_criteria,
                "comparison_method": "criteria_based"
            }
    
    def summary_validation_tool(self, summary: str, original_content: str, validation_criteria: List[str] = None) -> Dict[str, Any]:
        """Validate summary accuracy and completeness"""
        
        if not validation_criteria:
            validation_criteria = ["factual_accuracy", "completeness", "coherence", "relevance"]
        
        system_prompt = """You are an expert at validating document summaries.
        Your task is to assess whether a summary accurately represents the original content.
        
        Guidelines:
        - Check factual accuracy against original content
        - Assess completeness of information coverage
        - Evaluate logical coherence and flow
        - Verify relevance of included information
        - Identify any errors or omissions
        
        Return a JSON object with:
        - validation_results: detailed validation for each criterion
        - accuracy_score: overall accuracy score (0-1)
        - completeness_score: completeness score (0-1)
        - coherence_score: coherence score (0-1)
        - relevance_score: relevance score (0-1)
        - errors_found: list of errors or issues
        - missing_information: important information not included
        - confidence_score: confidence in the validation (0-1)
        """
        
        criteria_text = ", ".join(validation_criteria)
        
        human_prompt = f"""Original content:
{original_content}

Summary to validate:
{summary}

Validate the summary based on: {criteria_text}

Provide the validation in JSON format."""
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt), 
                                      HumanMessage(content=human_prompt)])
            
            result = json.loads(response.content)
            
            # Calculate overall confidence
            scores = [
                result.get("accuracy_score", 0),
                result.get("completeness_score", 0),
                result.get("coherence_score", 0),
                result.get("relevance_score", 0)
            ]
            overall_confidence = sum(scores) / len(scores) if scores else 0.0
            
            return {
                "validation_results": result.get("validation_results", {}),
                "accuracy_score": result.get("accuracy_score", 0.0),
                "completeness_score": result.get("completeness_score", 0.0),
                "coherence_score": result.get("coherence_score", 0.0),
                "relevance_score": result.get("relevance_score", 0.0),
                "errors_found": result.get("errors_found", []),
                "missing_information": result.get("missing_information", []),
                "confidence_score": overall_confidence,
                "validation_criteria": validation_criteria,
                "validation_method": "criteria_based"
            }
            
        except Exception as e:
            return {
                "validation_results": {},
                "accuracy_score": 0.0,
                "completeness_score": 0.0,
                "coherence_score": 0.0,
                "relevance_score": 0.0,
                "errors_found": [],
                "missing_information": [],
                "confidence_score": 0.0,
                "validation_criteria": validation_criteria,
                "validation_method": "criteria_based"
            }
    
    def _calculate_extractive_confidence(self, selected_sentences: List[int], total_sentences: int) -> float:
        """Calculate confidence for extractive summary"""
        if not selected_sentences or total_sentences == 0:
            return 0.0
        
        # Base confidence on selection ratio and number of sentences
        selection_ratio = len(selected_sentences) / total_sentences
        optimal_ratio = 0.1  # 10% of sentences is often optimal
        
        # Higher confidence if ratio is close to optimal
        ratio_confidence = 1.0 - abs(selection_ratio - optimal_ratio) / optimal_ratio
        ratio_confidence = max(0.0, min(1.0, ratio_confidence))
        
        # Bonus for having multiple sentences
        sentence_bonus = min(1.0, len(selected_sentences) / 5.0)
        
        return (ratio_confidence + sentence_bonus) / 2.0
    
    def _calculate_abstractive_confidence(self, summary: str, original_content: str) -> float:
        """Calculate confidence for abstractive summary"""
        if not summary or not original_content:
            return 0.0
        
        # Base confidence on summary length relative to original
        summary_ratio = len(summary) / len(original_content)
        optimal_ratio = 0.15  # 15% is often good for abstractive
        
        ratio_confidence = 1.0 - abs(summary_ratio - optimal_ratio) / optimal_ratio
        ratio_confidence = max(0.0, min(1.0, ratio_confidence))
        
        # Bonus for coherent structure
        sentences = summary.split('.')
        structure_bonus = min(1.0, len(sentences) / 3.0)
        
        return (ratio_confidence + structure_bonus) / 2.0
    
    def _calculate_executive_confidence(self, key_findings: List[str], recommendations: List[str]) -> float:
        """Calculate confidence for executive summary"""
        if not key_findings and not recommendations:
            return 0.0
        
        # Base confidence on having both findings and recommendations
        findings_score = min(1.0, len(key_findings) / 3.0)
        recommendations_score = min(1.0, len(recommendations) / 2.0)
        
        return (findings_score + recommendations_score) / 2.0
    
    def _calculate_technical_confidence(self, specifications: List[str], methodologies: List[str]) -> float:
        """Calculate confidence for technical summary"""
        if not specifications and not methodologies:
            return 0.0
        
        # Base confidence on having technical details
        specs_score = min(1.0, len(specifications) / 2.0)
        methods_score = min(1.0, len(methodologies) / 2.0)
        
        return (specs_score + methods_score) / 2.0
    
    def _calculate_key_points_confidence(self, categorized_points: Dict[str, List[str]], content_length: int) -> float:
        """Calculate confidence for key points extraction"""
        if not categorized_points:
            return 0.0
        
        total_points = sum(len(points) for points in categorized_points.values())
        
        # Base confidence on number of points relative to content length
        points_per_word = total_points / max(content_length, 1)
        optimal_ratio = 0.01  # 1 point per 100 words
        
        ratio_confidence = 1.0 - abs(points_per_word - optimal_ratio) / optimal_ratio
        ratio_confidence = max(0.0, min(1.0, ratio_confidence))
        
        # Bonus for categorization
        category_bonus = min(1.0, len(categorized_points) / 4.0)
        
        return (ratio_confidence + category_bonus) / 2.0
    
    def _calculate_comparison_confidence(self, comparison_results: Dict[str, Any], total_length: int) -> float:
        """Calculate confidence for summary comparison"""
        if not comparison_results:
            return 0.0
        
        # Base confidence on having detailed comparison results
        criteria_count = len(comparison_results)
        criteria_score = min(1.0, criteria_count / 4.0)
        
        # Bonus for longer content (more to compare)
        length_bonus = min(1.0, total_length / 1000.0)
        
        return (criteria_score + length_bonus) / 2.0
    
    async def execute(self, document_content: str, goal: str = "Generate comprehensive summary", 
                     **kwargs) -> AgentResult:
        """Execute the summarizer agent"""
        
        try:
            # Determine summary type from goal
            summary_type = kwargs.get("summary_type", "abstractive")
            
            if summary_type == "extractive":
                result = self.extractive_summary_tool(
                    document_content,
                    summary_length=kwargs.get("summary_length", "medium"),
                    focus_areas=kwargs.get("focus_areas")
                )
            elif summary_type == "executive":
                result = self.executive_summary_tool(
                    document_content,
                    business_context=kwargs.get("business_context", "general")
                )
            elif summary_type == "technical":
                result = self.technical_summary_tool(
                    document_content,
                    technical_domain=kwargs.get("technical_domain", "general")
                )
            else:  # abstractive
                result = self.abstractive_summary_tool(
                    document_content,
                    summary_style=kwargs.get("summary_style", "informative"),
                    target_audience=kwargs.get("target_audience", "general")
                )
            
            return AgentResult(
                output=result,
                confidence=result.get("confidence_score", 0.0),
                rationale=f"Generated {summary_type} summary with {result.get('confidence_score', 0.0):.2f} confidence",
                execution_id=str(uuid.uuid4()),
                agent_type=self.agent_type,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return AgentResult(
                output={"error": str(e)},
                confidence=0.0,
                rationale=f"Error in summarization: {str(e)}",
                execution_id=str(uuid.uuid4()),
                agent_type=self.agent_type,
                timestamp=datetime.utcnow()
            )
