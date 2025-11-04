#!/bin/bash
# Quick setup script for CarParams - handles environment automatically

set -e

echo "======================================================================"
echo "  CarParams Setup - Automated"
echo "======================================================================"
echo ""

# Find project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OPENPILOT_PATH="$PROJECT_ROOT/openpilot/openpilot"

echo "Project root: $PROJECT_ROOT"
echo "Openpilot path: $OPENPILOT_PATH"
echo ""

# Check if openpilot exists
if [ ! -d "$OPENPILOT_PATH" ]; then
    echo "❌ ERROR: openpilot not found at $OPENPILOT_PATH"
    echo ""
    echo "Please install openpilot first:"
    echo "  cd $PROJECT_ROOT"
    echo "  ./scripts/setup_system.sh"
    exit 1
fi

echo "✓ Openpilot found"

# Check if venv exists
if [ ! -d "$OPENPILOT_PATH/.venv" ]; then
    echo "❌ ERROR: openpilot venv not found"
    echo ""
    echo "Openpilot needs to be built first:"
    echo "  cd $OPENPILOT_PATH"
    echo "  ./build.sh"
    exit 1
fi

echo "✓ Openpilot venv found"
echo ""

# Activate venv and run setup
echo "Running setup_mock_carparams.py..."
echo ""

cd "$OPENPILOT_PATH"
source .venv/bin/activate

cd "$PROJECT_ROOT"
python3 scripts/setup_mock_carparams.py

# Check if it succeeded
if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================================"
    echo "  Testing CarParams..."
    echo "======================================================================"
    echo ""
    
    python3 scripts/test_carparams.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "======================================================================"
        echo "  ✅ SUCCESS! CarParams is ready"
        echo "======================================================================"
        echo ""
        echo "Next steps:"
        echo "  1. Fix bridge message handling (Chunk 2)"
        echo "  2. Update launcher (Chunk 3)"
        echo "  3. Test full system (Chunk 4)"
        exit 0
    else
        echo ""
        echo "❌ Verification failed"
        exit 1
    fi
else
    echo ""
    echo "❌ Setup failed"
    exit 1
fi
