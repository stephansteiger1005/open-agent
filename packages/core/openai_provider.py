"""
OpenAI provider for agent responses.
This module integrates OpenAI API to provide LLM capabilities for agents.
"""
import os
from typing import List, Dict, Any, AsyncGenerator, Optional
from openai import AsyncOpenAI


class OpenAIProvider:
    """Provider for OpenAI API interactions"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = AsyncOpenAI(api_key=api_key)
    
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
        try:
            if stream:
                # Streaming mode
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                )
                
                async for chunk in response:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if delta and delta.content:
                            yield delta.content
            else:
                # Non-streaming mode
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
                        yield message.content
                    
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")


# Global provider instance
_provider: Optional[OpenAIProvider] = None


def get_openai_provider() -> OpenAIProvider:
    """Get or create the global OpenAI provider"""
    global _provider
    if _provider is None:
        _provider = OpenAIProvider()
    return _provider
