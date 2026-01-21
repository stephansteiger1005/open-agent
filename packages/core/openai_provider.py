"""
OpenAI provider for agent responses.
This module integrates OpenAI API to provide LLM capabilities for agents.
"""
import os
import logging
import time
from typing import List, Dict, Any, AsyncGenerator, Optional
from openai import AsyncOpenAI

# Configure logging
logger = logging.getLogger(__name__)


class OpenAIProvider:
    """Provider for OpenAI API interactions"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Configure timeout settings (default: 60 seconds for connection, 600 for read)
        timeout = float(os.getenv("OPENAI_TIMEOUT", "60.0"))
        
        logger.info(f"Initializing OpenAI provider with timeout: {timeout}s")
        self.client = AsyncOpenAI(
            api_key=api_key,
            timeout=timeout
        )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Generate chat completion using OpenAI API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (e.g., 'gpt-4', 'gpt-3.5-turbo')
            stream: Whether to stream the response
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Yields:
            str: Response content chunks if streaming, full response otherwise
        """
        start_time = time.time()
        
        # Log the request details
        logger.info(
            f"OpenAI API request starting - Model: {model}, Stream: {stream}, "
            f"Messages: {len(messages)}, Temperature: {temperature}, "
            f"Max Tokens: {max_tokens or 'default'}"
        )
        logger.debug(f"OpenAI request messages: {messages}")
        
        try:
            if stream:
                # Streaming mode
                logger.debug("Initiating streaming chat completion")
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                )
                
                chunk_count = 0
                async for chunk in response:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if delta and delta.content:
                            chunk_count += 1
                            yield delta.content
                
                elapsed_time = time.time() - start_time
                logger.info(
                    f"OpenAI streaming completed - Model: {model}, "
                    f"Chunks: {chunk_count}, Time: {elapsed_time:.2f}s"
                )
            else:
                # Non-streaming mode
                logger.debug("Initiating non-streaming chat completion")
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=False,
                )
                
                if response.choices and len(response.choices) > 0:
                    message = response.choices[0].message
                    if message and message.content:
                        elapsed_time = time.time() - start_time
                        content_length = len(message.content)
                        logger.info(
                            f"OpenAI request completed - Model: {model}, "
                            f"Response length: {content_length} chars, "
                            f"Time: {elapsed_time:.2f}s"
                        )
                        logger.debug(f"OpenAI response content: {message.content[:200]}...")
                        yield message.content
                    else:
                        logger.warning("OpenAI response has no content")
                else:
                    logger.warning("OpenAI response has no choices")
                    
        except Exception as e:
            elapsed_time = time.time() - start_time
            error_type = type(e).__name__
            error_message = str(e)
            
            logger.error(
                f"OpenAI API error - Model: {model}, Error Type: {error_type}, "
                f"Message: {error_message}, Time: {elapsed_time:.2f}s",
                exc_info=True
            )
            
            raise RuntimeError(f"OpenAI API error: {error_message}")


# Global provider instance
_provider: Optional[OpenAIProvider] = None


def get_openai_provider() -> OpenAIProvider:
    """Get or create the global OpenAI provider"""
    global _provider
    if _provider is None:
        _provider = OpenAIProvider()
    return _provider
