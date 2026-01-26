#!/bin/bash

# Start Ollama in the background
/bin/ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
for i in {1..30}; do
    if ollama list > /dev/null 2>&1; then
        echo "Ollama is ready!"
        break
    fi
    echo "Still waiting... (attempt $i/30)"
    sleep 2
done

# Verify Ollama is running
if ! ollama list > /dev/null 2>&1; then
    echo "ERROR: Ollama failed to start properly"
    exit 1
fi

# Pull llama3 model
echo "Pulling llama3 model..."
if ollama pull llama3; then
    echo "Successfully pulled llama3 model!"
else
    echo "WARNING: Failed to pull llama3 model. Please check your internet connection."
    echo "You can manually pull the model later with: docker exec <ollama-container-name> ollama pull llama3"
    echo "Ollama will continue running, but the llama3 model may not be available."
fi

# Keep the container running by waiting for the Ollama server process
wait $OLLAMA_PID
