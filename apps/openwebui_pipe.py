"""
OpenWebUI Pipe for Multi-Agent System

This pipe integrates the multi-agent system with OpenWebUI by exposing agents as models.
It provides both the router agent for intelligent coordination and individual agents
for direct interaction.
"""
import os
import requests
import json
import logging
from typing import List, Union, Generator, Iterator
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger(__name__)


class Pipe:
    """OpenWebUI pipe that exposes multi-agent system as models"""
    
    class Valves(BaseModel):
        """Configuration for the pipe"""
        API_BASE_URL: str = os.getenv("AGENT_API_BASE_URL", "http://localhost:8000")
        API_KEY: str = os.getenv("AGENT_API_KEY", "dev_key_123456789")
    
    def __init__(self):
        self.type = "manifold"
        self.id = "multi_agent_system"
        self.name = "Multi-Agent System"
        self.valves = self.Valves()
    
    def pipes(self) -> List[dict]:
        """
        Return list of available models (agents).
        This method is called by OpenWebUI to discover available models.
        """
        try:
            response = requests.get(
                f"{self.valves.API_BASE_URL}/v1/agents",
                headers={"Authorization": f"Bearer {self.valves.API_KEY}"},
                timeout=10
            )
            response.raise_for_status()
            agents = response.json()
            
            # Convert agents to OpenWebUI model format
            models = []
            for agent in agents:
                models.append({
                    "id": agent["id"],
                    "name": agent["name"],
                })
            
            return models
            
        except Exception as e:
            logger.error(f"Error fetching agents: {e}")
            # Return fallback models
            return [
                {"id": "router", "name": "Router/Planner"},
                {"id": "general", "name": "General Assistant"},
                {"id": "tool", "name": "Tool Agent"},
                {"id": "sql", "name": "SQL Agent"},
                {"id": "devops", "name": "DevOps Agent"},
                {"id": "docs", "name": "Documentation Agent"},
            ]
    
    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        """
        Process a chat completion request.
        
        Args:
            user_message: The user's message
            model_id: The agent ID to use
            messages: Full conversation history
            body: Additional parameters from OpenWebUI
            
        Returns:
            Response string or generator for streaming
        """
        try:
            # Create a new conversation for this request
            # Note: Each chat request creates a new conversation to ensure clean state
            # For production use, consider implementing conversation reuse or cleanup
            conv_response = requests.post(
                f"{self.valves.API_BASE_URL}/v1/conversations",
                headers={
                    "Authorization": f"Bearer {self.valves.API_KEY}",
                    "Content-Type": "application/json"
                },
                json={"metadata": {"model_id": model_id}},
                timeout=10
            )
            conv_response.raise_for_status()
            conv_id = conv_response.json()["id"]
            
            # Add all messages from history to the conversation
            for msg in messages:
                if msg.get("role") in ["user", "assistant"]:
                    msg_response = requests.post(
                        f"{self.valves.API_BASE_URL}/v1/conversations/{conv_id}/messages",
                        headers={
                            "Authorization": f"Bearer {self.valves.API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "role": msg["role"],
                            "content": msg.get("content", "")
                        },
                        timeout=10
                    )
                    msg_response.raise_for_status()  # Raise error if message posting fails
            
            # Determine if streaming is requested
            stream = body.get("stream", True)
            
            # Create and execute run
            run_response = requests.post(
                f"{self.valves.API_BASE_URL}/v1/conversations/{conv_id}/runs",
                headers={
                    "Authorization": f"Bearer {self.valves.API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "agent_id": model_id,
                    "stream": stream,
                    "metadata": {}
                },
                stream=stream,
                timeout=300  # Longer timeout for LLM responses
            )
            run_response.raise_for_status()
            
            if stream:
                # Stream response tokens
                return self._stream_response(run_response)
            else:
                # Return complete response
                result = run_response.json()
                return result.get("message", "Response received")
                
        except requests.exceptions.Timeout:
            return "Error: Request timeout. The agent took too long to respond."
        except requests.exceptions.RequestException as e:
            return f"Error communicating with agent system: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    def _stream_response(self, response) -> Generator[str, None, None]:
        """
        Parse SSE stream and yield content chunks.
        
        Args:
            response: Streaming HTTP response
            
        Yields:
            Content chunks from the agent
        """
        try:
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    
                    # Parse SSE format: "event: <type>\ndata: <json>\n\n"
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # Remove "data: " prefix
                        try:
                            data = json.loads(data_str)
                            
                            # Yield content deltas
                            if "delta" in data:
                                yield data["delta"]
                            elif "content" in data:
                                yield data["content"]
                            elif "message" in data:
                                yield data["message"]
                                
                        except json.JSONDecodeError:
                            # If not JSON, yield raw data
                            yield data_str
                            
        except Exception as e:
            yield f"\n\nError during streaming: {str(e)}"
