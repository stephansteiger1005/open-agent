import yaml
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Agent:
    id: str
    name: str
    role: str
    system_prompt: str
    model: str
    allowed_tools: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "system_prompt": self.system_prompt,
            "model": self.model,
            "allowed_tools": self.allowed_tools,
        }


class AgentRegistry:
    def __init__(self, config_path: str = "config/agents.yaml"):
        self.config_path = config_path
        self.agents: Dict[str, Agent] = {}
        self.load_agents()
    
    def load_agents(self):
        """Load agents from configuration file"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Agent configuration not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Expand environment variables in configuration
        default_model = os.getenv("DEFAULT_MODEL", "gpt-4")
        
        for agent_config in config.get("agents", []):
            # Expand ${DEFAULT_MODEL} in model field
            model = agent_config.get("model", default_model)
            if "${DEFAULT_MODEL}" in model:
                model = model.replace("${DEFAULT_MODEL}", default_model)
            
            agent = Agent(
                id=agent_config["id"],
                name=agent_config["name"],
                role=agent_config["role"],
                system_prompt=agent_config["system_prompt"],
                model=model,
                allowed_tools=agent_config.get("allowed_tools", []),
            )
            self.agents[agent.id] = agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Agent]:
        """List all registered agents"""
        return list(self.agents.values())
    
    def is_tool_allowed(self, agent_id: str, tool_name: str) -> bool:
        """Check if a tool is allowed for an agent"""
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        
        # If allowed_tools contains "*", all tools are allowed
        if "*" in agent.allowed_tools:
            return True
        
        return tool_name in agent.allowed_tools


# Global agent registry instance
_registry: Optional[AgentRegistry] = None


def get_agent_registry() -> AgentRegistry:
    """Get or create the global agent registry"""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry
