import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..models.base import AgentResult, AgentType


class Tool:
    """Base class for agent tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters"""
        pass


class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, name: str, agent_type: AgentType):
        self.name = name
        self.agent_type = agent_type
        self.tools: List[Tool] = []
        self.confidence_threshold = 0.7
        
    def add_tool(self, tool: Tool):
        """Add a tool to the agent's toolkit"""
        self.tools.append(tool)
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a tool by name"""
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None
    
    @abstractmethod
    async def run(self, goal: str, context: Dict[str, Any]) -> AgentResult:
        """
        Main execution method for the agent
        
        Args:
            goal: The goal/objective for this agent
            context: Context information including previous agent outputs
            
        Returns:
            AgentResult with output, rationale, confidence, and next action
        """
        pass
    
    async def execute_with_timing(self, goal: str, context: Dict[str, Any]) -> AgentResult:
        """Execute agent with timing information"""
        start_time = time.time()
        
        try:
            result = await self.run(goal, context)
            duration_ms = int((time.time() - start_time) * 1000)
            result.duration_ms = duration_ms
            return result
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return AgentResult(
                output=None,
                rationale=f"Error in {self.name}: {str(e)}",
                confidence=0.0,
                duration_ms=duration_ms
            )
    
    def validate_confidence(self, confidence: float) -> bool:
        """Check if confidence meets threshold"""
        return confidence >= self.confidence_threshold
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return [tool.name for tool in self.tools]
    
    def __str__(self) -> str:
        return f"{self.name} ({self.agent_type.value})"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.name}' type='{self.agent_type.value}'>"
