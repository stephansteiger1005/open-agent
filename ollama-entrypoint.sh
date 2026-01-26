#!/bin/bash

# Start Ollama in the background
/bin/ollama serve &

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
sleep 5

# Pull llama3 model
echo "Pulling llama3 model..."
ollama pull llama3

# Keep the container running
wait
