from typing import Dict, Any, AsyncGenerator, Optional
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from packages.core.models import Run, Step, ToolCall, Message, RunStatus, StepStatus
from packages.core.schemas import StreamEvent
from .agents import get_agent_registry, Agent
from apps.mcp_gateway.client import get_mcp_client


class Orchestrator:
    """Orchestrates agent execution and tool invocation"""
    
    def __init__(self):
        self.agent_registry = get_agent_registry()
        self.mcp_client = get_mcp_client()
    
    async def execute_run(
        self,
        session: AsyncSession,
        run: Run,
        stream: bool = False
    ) -> AsyncGenerator[StreamEvent, None]:
        """Execute a run with the specified agent"""
        
        # Update run status
        run.status = RunStatus.RUNNING.value
        await session.commit()
        
        if stream:
            yield StreamEvent(
                event="run.started",
                data={"run_id": run.id, "agent_id": run.agent_id}
            )
        
        try:
            # Get agent configuration
            agent = self.agent_registry.get_agent(run.agent_id)
            if not agent:
                raise ValueError(f"Agent not found: {run.agent_id}")
            
            # Get conversation messages for context
            result = await session.execute(
                select(Message)
                .filter(Message.conversation_id == run.conversation_id)
                .order_by(Message.created_at)
            )
            messages = result.scalars().all()
            
            # Create a step for this execution
            step = Step(
                id=str(uuid.uuid4()),
                run_id=run.id,
                step_number=1,
                agent_id=agent.id,
                status=StepStatus.RUNNING.value,
                input_data={"messages": [{"role": m.role, "content": m.content} for m in messages]},
                output_data={}
            )
            session.add(step)
            await session.commit()
            
            if stream:
                yield StreamEvent(
                    event="step.started",
                    data={"step_id": step.id, "agent_id": agent.id}
                )
            
            # Simulate agent processing (replace with actual LLM call)
            if stream:
                async for chunk in self._simulate_agent_response(agent, messages, stream):
                    yield StreamEvent(
                        event="model.delta",
                        data={"delta": chunk}
                    )
                # Get full content for saving
                final_content_parts = []
                async for part in self._simulate_agent_response(agent, messages, False):
                    final_content_parts.append(part)
                final_content = "".join(final_content_parts)
            else:
                # Non-streaming: collect all content
                final_content_parts = []
                async for part in self._simulate_agent_response(agent, messages, False):
                    final_content_parts.append(part)
                final_content = "".join(final_content_parts)
            
            # Update step with output
            step.status = StepStatus.COMPLETED.value
            step.output_data = {"content": final_content}
            step.completed_at = datetime.utcnow()
            
            # Create assistant message
            assistant_message = Message(
                id=str(uuid.uuid4()),
                conversation_id=run.conversation_id,
                role="assistant",
                content=final_content,
                attachments=[],
                metadata_={"run_id": run.id, "agent_id": agent.id}
            )
            session.add(assistant_message)
            
            # Complete the run
            run.status = RunStatus.COMPLETED.value
            run.completed_at = datetime.utcnow()
            await session.commit()
            
            if stream:
                yield StreamEvent(
                    event="run.completed",
                    data={"run_id": run.id, "message": final_content}
                )
        
        except Exception as e:
            run.status = RunStatus.FAILED.value
            run.error = str(e)
            run.completed_at = datetime.utcnow()
            await session.commit()
            
            if stream:
                yield StreamEvent(
                    event="run.failed",
                    data={"run_id": run.id, "error": str(e)}
                )
            raise
    
    async def _simulate_agent_response(
        self,
        agent: Agent,
        messages: list,
        stream: bool
    ) -> AsyncGenerator[str, None]:
        """Simulate agent response (replace with actual LLM integration)"""
        
        # Simple mock response based on agent role
        if agent.role == "routing":
            response = f"I am the router agent. Based on your request, I'll delegate to the general assistant."
        elif agent.role == "assistant":
            response = f"Hello! I'm the {agent.name}. How can I help you today?"
        elif agent.role == "tool_executor":
            response = "I can execute tools for you. What tool would you like to use?"
        elif agent.role == "specialist":
            response = f"I'm a {agent.name} specialist. I'm here to help with {agent.role}-related tasks."
        else:
            response = "I'm an agent ready to assist you."
        
        if stream:
            # Simulate streaming by yielding chunks
            words = response.split()
            for word in words:
                yield word + " "
        else:
            yield response


# Global orchestrator instance
_orchestrator: Optional[Orchestrator] = None


def get_orchestrator() -> Orchestrator:
    """Get or create the global orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator
