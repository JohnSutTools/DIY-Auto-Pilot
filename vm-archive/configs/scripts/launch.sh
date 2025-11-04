#!/bin/bash
# Launch script - starts bridge with openpilot in tmux

set -e

CONFIG="${1:-bridge/config.yaml}"

if [ ! -f "$CONFIG" ]; then
    echo "ERROR: Config file not found: $CONFIG"
    exit 1
fi

echo "Starting openpilot steering bridge..."
echo "Config: $CONFIG"
echo ""

# Check if tmux is available
if ! command -v tmux &> /dev/null; then
    echo "ERROR: tmux not installed"
    echo "Install with: sudo apt-get install tmux"
    exit 1
fi

# Check if openpilot is available
if ! python3 -c "import cereal" 2>/dev/null; then
    echo "ERROR: cereal (openpilot) not found"
    echo "Add to PYTHONPATH: export PYTHONPATH=\"\${PYTHONPATH}:~/openpilot\""
    exit 1
fi

# Create tmux session
SESSION="openpilot_bridge"

# Kill existing session if any
tmux kill-session -t $SESSION 2>/dev/null || true

# Start new session
tmux new-session -d -s $SESSION -n bridge

# Window 1: Bridge
tmux send-keys -t $SESSION:bridge "cd $(pwd)" C-m
tmux send-keys -t $SESSION:bridge "python3 bridge/op_serial_bridge.py --config $CONFIG --debug" C-m

# Window 2: Monitor (for watching messages)
tmux new-window -t $SESSION -n monitor
tmux send-keys -t $SESSION:monitor "# Use this window to monitor openpilot messages" C-m
tmux send-keys -t $SESSION:monitor "# Example: cereal-replay <route> --services carControl" C-m

# Window 3: ESP32 serial monitor
tmux new-window -t $SESSION -n esp32
tmux send-keys -t $SESSION:esp32 "# ESP32 serial monitor" C-m
tmux send-keys -t $SESSION:esp32 "# screen /dev/ttyUSB0 115200" C-m

# Attach to session
tmux select-window -t $SESSION:bridge
tmux attach-session -t $SESSION

echo ""
echo "Tmux session closed"
echo "To reattach: tmux attach -t $SESSION"
