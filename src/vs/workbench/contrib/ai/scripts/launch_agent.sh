#!/bin/bash
AGENT_DIR="$(dirname "$0")/../agent_link/DeepAgent"
echo "Launching DeepAgent from $AGENT_DIR..."

if [ ! -d "$AGENT_DIR" ]; then
    echo "Error: DeepAgent directory not linked."
    exit 1
fi

cd "$AGENT_DIR"
# Assuming python3 is available and has necessary deps. 
# If venv exists, use it:
if [ -d "venv" ]; then
    source venv/bin/activate
fi

python3 chat_server.py
