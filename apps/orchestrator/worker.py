"""
Worker module for the orchestrator service.
This runs as a standalone process to handle background task orchestration.
"""
import asyncio
import os
import logging
from packages.core.database import init_db

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point for the orchestrator worker"""
    logger.info("Starting orchestrator worker...")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    # Initialize orchestrator components
    from apps.orchestrator.engine import get_orchestrator
    from apps.orchestrator.agents import get_agent_registry
    
    orchestrator = get_orchestrator()
    agent_registry = get_agent_registry()
    
    logger.info(f"Orchestrator initialized with {len(agent_registry.list_agents())} agents")
    
    # Keep the worker running
    logger.info("Orchestrator worker is running. Press Ctrl+C to stop.")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down orchestrator worker...")


if __name__ == "__main__":
    asyncio.run(main())
