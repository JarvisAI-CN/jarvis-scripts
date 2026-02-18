#!/bin/bash
# Start script for Jarvis OpenAI Proxy

cd /home/ubuntu/.openclaw/workspace/openai-proxy

# Load environment variables from .env if exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "🚀 Starting Jarvis OpenAI Proxy..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 9000 --reload
