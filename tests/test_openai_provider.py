import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_openai_provider_requires_api_key():
    """Test that OpenAI provider requires an API key"""
    # Remove API key if exists
    old_key = os.environ.get("OPENAI_API_KEY")
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    
    try:
        from packages.core.openai_provider import OpenAIProvider
        
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            OpenAIProvider()
    finally:
        # Restore API key if it existed
        if old_key:
            os.environ["OPENAI_API_KEY"] = old_key


@pytest.mark.asyncio
async def test_openai_provider_chat_completion_non_streaming():
    """Test non-streaming chat completion"""
    # Set a dummy API key for testing
    os.environ["OPENAI_API_KEY"] = "test_key_12345"
    
    from packages.core.openai_provider import OpenAIProvider
    
    # Create mock response
    mock_choice = MagicMock()
    mock_choice.message.content = "Test response from OpenAI"
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    with patch('packages.core.openai_provider.AsyncOpenAI') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        provider = OpenAIProvider()
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ]
        
        # Collect response
        result = []
        async for chunk in provider.chat_completion(messages, stream=False):
            result.append(chunk)
        
        assert len(result) == 1
        assert result[0] == "Test response from OpenAI"
        
        # Verify that create was called correctly
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs['stream'] is False
        assert call_kwargs['messages'] == messages


@pytest.mark.asyncio
async def test_openai_provider_chat_completion_streaming():
    """Test streaming chat completion"""
    # Set a dummy API key for testing
    os.environ["OPENAI_API_KEY"] = "test_key_12345"
    
    from packages.core.openai_provider import OpenAIProvider
    
    # Create mock streaming response
    async def mock_stream():
        for word in ["Hello", " ", "from", " ", "OpenAI"]:
            mock_choice = MagicMock()
            mock_choice.delta.content = word
            mock_chunk = MagicMock()
            mock_chunk.choices = [mock_choice]
            yield mock_chunk
    
    with patch('packages.core.openai_provider.AsyncOpenAI') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_stream())
        mock_client_class.return_value = mock_client
        
        provider = OpenAIProvider()
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ]
        
        # Collect response chunks
        result = []
        async for chunk in provider.chat_completion(messages, stream=True):
            result.append(chunk)
        
        assert len(result) == 5
        assert "".join(result) == "Hello from OpenAI"
        
        # Verify that create was called correctly
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs['stream'] is True
        assert call_kwargs['messages'] == messages


@pytest.mark.asyncio
async def test_openai_provider_error_handling():
    """Test error handling in OpenAI provider"""
    # Set a dummy API key for testing
    os.environ["OPENAI_API_KEY"] = "test_key_12345"
    
    from packages.core.openai_provider import OpenAIProvider
    
    with patch('packages.core.openai_provider.AsyncOpenAI') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
        mock_client_class.return_value = mock_client
        
        provider = OpenAIProvider()
        
        messages = [{"role": "user", "content": "Hello!"}]
        
        # Should raise RuntimeError wrapping the original error
        with pytest.raises(RuntimeError, match="OpenAI API error"):
            async for chunk in provider.chat_completion(messages):
                pass


@pytest.mark.asyncio
async def test_openai_provider_max_tokens_none_excluded():
    """Test that max_tokens is not included in API call when None"""
    # Set a dummy API key for testing
    os.environ["OPENAI_API_KEY"] = "test_key_12345"
    
    from packages.core.openai_provider import OpenAIProvider
    
    # Create mock response
    mock_choice = MagicMock()
    mock_choice.message.content = "Test response"
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    with patch('packages.core.openai_provider.AsyncOpenAI') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        provider = OpenAIProvider()
        
        messages = [{"role": "user", "content": "Hello!"}]
        
        # Call with max_tokens=None (default)
        result = []
        async for chunk in provider.chat_completion(messages, max_tokens=None, stream=False):
            result.append(chunk)
        
        # Verify that create was called
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        
        # Verify max_tokens is NOT in the kwargs
        assert 'max_tokens' not in call_kwargs
        assert call_kwargs['model'] == 'gpt-4'
        assert call_kwargs['temperature'] == 0.7
        assert call_kwargs['stream'] is False


@pytest.mark.asyncio
async def test_openai_provider_max_tokens_value_included():
    """Test that max_tokens is included in API call when provided"""
    # Set a dummy API key for testing
    os.environ["OPENAI_API_KEY"] = "test_key_12345"
    
    from packages.core.openai_provider import OpenAIProvider
    
    # Create mock response
    mock_choice = MagicMock()
    mock_choice.message.content = "Test response"
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    with patch('packages.core.openai_provider.AsyncOpenAI') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        provider = OpenAIProvider()
        
        messages = [{"role": "user", "content": "Hello!"}]
        
        # Call with max_tokens=1000
        result = []
        async for chunk in provider.chat_completion(messages, max_tokens=1000, stream=False):
            result.append(chunk)
        
        # Verify that create was called
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        
        # Verify max_tokens IS in the kwargs with correct value
        assert 'max_tokens' in call_kwargs
        assert call_kwargs['max_tokens'] == 1000
        assert call_kwargs['model'] == 'gpt-4'
        assert call_kwargs['temperature'] == 0.7
        assert call_kwargs['stream'] is False
