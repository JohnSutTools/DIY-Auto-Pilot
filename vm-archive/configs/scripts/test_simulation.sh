#!/bin/bash
# Quick simulation test - runs everything needed for testing

set -e

echo "=========================================="
echo "Openpilot Steering - Simulation Mode"
echo "=========================================="
echo ""

# Check if openpilot is available
if [ ! -d "$HOME/openpilot" ]; then
    echo "ERROR: Openpilot not found at ~/openpilot"
    echo "Run: ./scripts/setup_system.sh"
    exit 1
fi

# Check Python dependencies
echo "Checking dependencies..."
python3 -c "import cereal.messaging" 2>/dev/null || {
    echo "ERROR: cereal not found"
    echo "Run: export PYTHONPATH=\"\${PYTHONPATH}:\$HOME/openpilot\""
    exit 1
}

python3 -c "import yaml" 2>/dev/null || {
    echo "ERROR: PyYAML not found"
    echo "Run: pip3 install -r bridge/requirements.txt"
    exit 1
}

echo "✓ All dependencies found"
echo ""

# Choose mode
echo "Simulation Options:"
echo "1. Simulated bridge only (you provide openpilot messages)"
echo "2. Full replay test (openpilot replay + simulated bridge)"
echo "3. Custom replay route"
echo ""
read -p "Select option [1-3]: " option

case $option in
    1)
        echo ""
        echo "Starting simulated bridge..."
        echo "In another terminal, send messages or run replay:"
        echo "  cd ~/openpilot"
        echo "  tools/replay/replay '<route>|<segment>'"
        echo ""
        python3 scripts/simulate.py --config bridge/config.yaml
        ;;
    
    2)
        # Use demo route
        DEMO_ROUTE="4cf7a6ad03080c90|2021-09-29--13-46-36|0"
        
        echo ""
        echo "Checking for demo route..."
        if [ ! -d "$HOME/.comma/media/0/realdata/${DEMO_ROUTE%%|*}" ]; then
            echo "Downloading demo route (one-time, ~100MB)..."
            cd ~/openpilot
            tools/replay/route_downloader.py "${DEMO_ROUTE%|*}"
        else
            echo "✓ Demo route available"
        fi
        
        echo ""
        echo "Starting simulation with demo route..."
        echo "This will run both openpilot replay AND simulated bridge"
        echo ""
        
        # Use tmux if available
        if command -v tmux &> /dev/null; then
            SESSION="sim_test"
            tmux kill-session -t $SESSION 2>/dev/null || true
            
            # Create tmux session
            tmux new-session -d -s $SESSION -n replay
            tmux send-keys -t $SESSION:replay "cd ~/openpilot" C-m
            tmux send-keys -t $SESSION:replay "tools/replay/replay '$DEMO_ROUTE'" C-m
            
            # Wait for replay to start
            sleep 3
            
            # Start bridge in second window
            tmux new-window -t $SESSION -n bridge
            tmux send-keys -t $SESSION:bridge "cd $PWD" C-m
            tmux send-keys -t $SESSION:bridge "python3 scripts/simulate.py --config bridge/config.yaml" C-m
            
            echo "✓ Started in tmux"
            echo ""
            echo "Commands:"
            echo "  tmux attach -t $SESSION  # View"
            echo "  Ctrl+B then D            # Detach"
            echo "  Ctrl+C in windows        # Stop"
            echo ""
            
            tmux attach -t $SESSION
        else
            echo "⚠️  tmux not found - running in foreground"
            echo "   Open another terminal to see replay output"
            echo ""
            
            # Start replay in background
            cd ~/openpilot
            tools/replay/replay "$DEMO_ROUTE" > /tmp/replay.log 2>&1 &
            REPLAY_PID=$!
            
            sleep 3
            
            # Start bridge in foreground
            cd "$OLDPWD"
            python3 scripts/simulate.py --config bridge/config.yaml
            
            # Cleanup
            kill $REPLAY_PID 2>/dev/null || true
        fi
        ;;
    
    3)
        echo ""
        read -p "Enter route (format: <route-name>|<segment>): " route
        
        echo ""
        echo "Checking route..."
        ROUTE_DIR="${route%%|*}"
        if [ ! -d "$HOME/.comma/media/0/realdata/$ROUTE_DIR" ]; then
            echo "Downloading route..."
            cd ~/openpilot
            tools/replay/route_downloader.py "${route%|*}"
        fi
        
        echo ""
        echo "Starting replay with: $route"
        echo "Open another terminal and run:"
        echo "  cd $PWD"
        echo "  python3 scripts/simulate.py --config bridge/config.yaml"
        echo ""
        
        cd ~/openpilot
        tools/replay/replay "$route"
        ;;
    
    *)
        echo "Invalid option"
        exit 1
        ;;
esac
