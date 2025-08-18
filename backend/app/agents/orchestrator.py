import json
import time
from typing import Any, Dict, List, Optional

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

from .base import BaseAgent
from ..models.base import AgentResult, AgentType, AgentTrace, AgentStep


class OrchestratorAgent(BaseAgent):
    """LLM-based orchestrator that plans and coordinates agent execution"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__("Orchestrator", AgentType.ORCHESTRATOR)
        self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
        self.available_agents: Dict[str, BaseAgent] = {}
        self.max_steps = 10
        self.confidence_threshold = 0.8
        
    def register_agent(self, agent: BaseAgent):
        """Register an agent for orchestration"""
        self.available_agents[agent.agent_type.value] = agent
    
    def get_planning_prompt(self, goal: str, context: Dict[str, Any], available_agents: List[str]) -> str:
        """Generate planning prompt for LLM"""
        return f"""
You are an intelligent orchestrator for a regulatory document processing system. Your goal is to plan the execution of specialized agents to achieve the given objective.

GOAL: {goal}

CURRENT CONTEXT:
{json.dumps(context, indent=2)}

AVAILABLE AGENTS:
{chr(10).join([f"- {agent}" for agent in available_agents])}

AGENT CAPABILITIES:
- ingestion: Extract and normalize text from documents (OCR, PDF parsing)
- classifier: Determine document type and domain
- entity: Extract named entities, clauses, and key information
- risk: Evaluate compliance risks using policy rules
- qa: Answer questions about documents with citations
- compare: Compare two documents for differences and risk changes
- audit: Generate audit trails and compliance reports

TASK: Plan the next agent to execute. Consider:
1. What is the most logical next step?
2. What information is needed from previous steps?
3. What is the expected confidence level?
4. Should we continue or stop?

Respond with JSON:
{{
    "next_agent": "agent_name",
    "goal": "specific goal for this agent",
    "rationale": "why this agent should run next",
    "expected_confidence": 0.85,
    "should_continue": true,
    "stop_reason": null
}}
"""
    
    async def plan_next_step(self, goal: str, context: Dict[str, Any], trace: AgentTrace) -> Dict[str, Any]:
        """Use LLM to plan the next agent execution"""
        available_agents = list(self.available_agents.keys())
        
        # Remove agents that have already run to avoid loops
        executed_agents = [step.agent.value for step in trace.steps]
        available_agents = [agent for agent in available_agents if agent not in executed_agents]
        
        if not available_agents:
            return {
                "next_agent": None,
                "goal": "Complete",
                "rationale": "All available agents have been executed",
                "expected_confidence": 1.0,
                "should_continue": False,
                "stop_reason": "All agents completed"
            }
        
        prompt = self.get_planning_prompt(goal, context, available_agents)
        
        try:
            response = await self.llm.agenerate([[HumanMessage(content=prompt)]])
            plan_text = response.generations[0][0].text.strip()
            
            # Extract JSON from response
            if "```json" in plan_text:
                plan_text = plan_text.split("```json")[1].split("```")[0]
            elif "```" in plan_text:
                plan_text = plan_text.split("```")[1]
            
            plan = json.loads(plan_text)
            return plan
        except Exception as e:
            # Fallback: execute agents in order
            return {
                "next_agent": available_agents[0] if available_agents else None,
                "goal": f"Execute {available_agents[0]} for {goal}",
                "rationale": f"Fallback execution of {available_agents[0]}",
                "expected_confidence": 0.7,
                "should_continue": True,
                "stop_reason": None
            }
    
    async def run(self, goal: str, context: Dict[str, Any]) -> AgentResult:
        """Main orchestration loop"""
        trace = AgentTrace(goal=goal, context=context)
        step_count = 0
        
        while step_count < self.max_steps:
            # Plan next step
            plan = await self.plan_next_step(goal, context, trace)
            
            if not plan["should_continue"] or not plan["next_agent"]:
                trace.status = "completed"
                trace.completed_at = time.time()
                return AgentResult(
                    output=trace,
                    rationale=f"Orchestration completed: {plan.get('stop_reason', 'All steps done')}",
                    confidence=1.0,
                    next_suggested_action=None
                )
            
            # Execute next agent
            agent = self.available_agents.get(plan["next_agent"])
            if not agent:
                trace.status = "failed"
                return AgentResult(
                    output=trace,
                    rationale=f"Agent {plan['next_agent']} not found",
                    confidence=0.0,
                    next_suggested_action=None
                )
            
            # Execute agent
            agent_result = await agent.execute_with_timing(plan["goal"], context)
            
            # Record step
            step = AgentStep(
                step_no=step_count + 1,
                agent=agent.agent_type,
                rationale=agent_result.rationale,
                confidence=agent_result.confidence,
                duration_ms=agent_result.duration_ms,
                metadata={
                    "planned_goal": plan["goal"],
                    "planned_rationale": plan["rationale"],
                    "agent_output": agent_result.output
                }
            )
            trace.steps.append(step)
            
            # Update context with agent output
            context[f"{agent.agent_type.value}_result"] = agent_result.output
            context[f"{agent.agent_type.value}_confidence"] = agent_result.confidence
            
            # Check if we should stop based on confidence
            if agent_result.confidence >= self.confidence_threshold:
                trace.status = "completed"
                trace.completed_at = time.time()
                return AgentResult(
                    output=trace,
                    rationale=f"High confidence achieved by {agent.agent_type.value}",
                    confidence=agent_result.confidence,
                    next_suggested_action=None
                )
            
            step_count += 1
        
        # Max steps reached
        trace.status = "completed"
        trace.completed_at = time.time()
        return AgentResult(
            output=trace,
            rationale=f"Maximum steps ({self.max_steps}) reached",
            confidence=0.5,
            next_suggested_action="Review results and consider manual intervention"
        )
    
    def get_agent_summary(self) -> Dict[str, Any]:
        """Get summary of available agents"""
        return {
            "total_agents": len(self.available_agents),
            "agents": [
                {
                    "name": agent.name,
                    "type": agent.agent_type.value,
                    "tools": agent.get_available_tools()
                }
                for agent in self.available_agents.values()
            ]
        }
