#!/bin/bash
# Integration test - runs webcam simulator and bridge together

set -e

OPENPILOT_PATH="$HOME/openpilot"
VENV_PYTHON="$OPENPILOT_PATH/.venv/bin/python"
PROJECT_ROOT="$HOME/steering-actuator"

echo "=================================================="
echo "Openpilot + Bridge Integration Test"
echo "=================================================="
echo ""

# Check openpilot exists
if [ ! -d "$OPENPILOT_PATH" ]; then
    echo "ERROR: openpilot not found at $OPENPILOT_PATH"
    exit 1
fi

# Check venv exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "ERROR: openpilot venv Python not found"
    exit 1
fi

# Install opencv if needed
echo "📦 Checking dependencies..."
$VENV_PYTHON -c "import cv2" 2>/dev/null || {
    echo "Installing opencv-python..."
    $OPENPILOT_PATH/.venv/bin/pip install opencv-python
}

# Copy files from Windows to WSL if needed
echo "📁 Syncing files from Windows..."
WIN_PATH="/mnt/c/Users/John/OneDrive - Sutton Tools Pty Ltd/Private/DIY Auto Pilot"
if [ -d "$WIN_PATH" ]; then
    cp "$WIN_PATH/scripts/test_with_webcam.py" "$PROJECT_ROOT/scripts/" 2>/dev/null || true
    cp "$WIN_PATH/bridge/config.yaml" "$PROJECT_ROOT/bridge/" 2>/dev/null || true
    cp "$WIN_PATH/bridge/op_serial_bridge.py" "$PROJECT_ROOT/bridge/" 2>/dev/null || true
    echo "✓ Files synced"
else
    echo "⚠️  Windows path not found, using existing files"
fi

cd "$PROJECT_ROOT"

echo ""
echo "🚀 Starting steering simulator + bridge..."
echo "=================================================="
echo ""
echo "This will run TWO processes side-by-side:"
echo "  � Simulator: Publishes steering commands via cereal"
echo "  🔧 Bridge: Receives commands and logs them (mock mode)"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Cleanup function
cleanup() {
    echo -e "\n\n🛑 Shutting down..."
    kill $SIMULATOR_PID 2>/dev/null || true
    kill $BRIDGE_PID 2>/dev/null || true
    wait 2>/dev/null
    echo "✓ Processes stopped"
}
trap cleanup EXIT INT TERM

# Start simulator in background
echo "Starting simulator..."
PYTHONPATH="$OPENPILOT_PATH" $VENV_PYTHON scripts/test_with_webcam.py 2>&1 | sed 's/^/[SIMULATOR] /' &
SIMULATOR_PID=$!

# Wait for simulator to initialize
sleep 2

# Start bridge
echo "Starting bridge..."
echo "=================================================="
echo ""
PYTHONPATH="$OPENPILOT_PATH" $VENV_PYTHON bridge/op_serial_bridge.py --config bridge/config.yaml --debug 2>&1 | sed 's/^/[BRIDGE] /'

# Script stays here until bridge exits or Ctrl+C
