#!/bin/bash
# Pre-build verification test for Chunk 1
# Checks that files are in place before building openpilot

set -e

echo "======================================================================"
echo "  Pre-Build Verification (Chunk 1)"
echo "======================================================================"
echo ""

# Find project root
PROJECT_ROOT="/mnt/c/Users/John/OneDrive - Sutton Tools Pty Ltd/Private/DIY Auto Pilot"
cd "$PROJECT_ROOT"

echo "Project root: $PROJECT_ROOT"
echo ""

# Test 1: Check our scripts exist
echo "Test 1: Checking Chunk 1 scripts..."
if [ -f "scripts/setup_mock_carparams.py" ]; then
    echo "✓ setup_mock_carparams.py exists"
else
    echo "✗ setup_mock_carparams.py MISSING"
    exit 1
fi

if [ -f "scripts/test_carparams.py" ]; then
    echo "✓ test_carparams.py exists"
else
    echo "✗ test_carparams.py MISSING"
    exit 1
fi

# Test 2: Check openpilot is cloned
echo ""
echo "Test 2: Checking openpilot..."
if [ -d "openpilot/openpilot" ]; then
    echo "✓ openpilot directory exists"
else
    echo "✗ openpilot NOT cloned"
    exit 1
fi

if [ -f "openpilot/openpilot/SConstruct" ]; then
    echo "✓ openpilot appears valid (SConstruct found)"
else
    echo "✗ openpilot appears incomplete"
    exit 1
fi

# Test 3: Check if built
echo ""
echo "Test 3: Checking openpilot build status..."
if [ -d "openpilot/openpilot/.venv" ]; then
    echo "✓ openpilot is BUILT (.venv exists)"
    BUILD_NEEDED=false
else
    echo "⚠ openpilot NOT built yet (.venv missing)"
    BUILD_NEEDED=true
fi

echo ""
echo "======================================================================"
echo "  Pre-Build Verification Results"
echo "======================================================================"
echo ""

if [ "$BUILD_NEEDED" = true ]; then
    echo "Status: ⚠️  Openpilot needs to be built"
    echo ""
    echo "To build openpilot (one-time, takes 10-30 minutes):"
    echo ""
    echo "  cd '$PROJECT_ROOT/openpilot/openpilot'"
    echo "  scons -j\$(nproc)"
    echo ""
    echo "After building, run the full test:"
    echo "  bash scripts/test_chunk1.sh"
    echo ""
    exit 2
else
    echo "Status: ✅ Ready for full testing"
    echo ""
    echo "Run full test suite:"
    echo "  bash scripts/test_chunk1.sh"
    echo ""
    exit 0
fi
