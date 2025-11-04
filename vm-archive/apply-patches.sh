#!/bin/bash
# Apply all VM patches to fresh openpilot installation
# Run this after installing openpilot on native Ubuntu

set -e

OPENPILOT=~/openpilot
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ARCHIVE="$SCRIPT_DIR/openpilot-patches"

echo "========================================"
echo "Applying VM Patches to Openpilot"
echo "========================================"
echo ""

# Check if openpilot exists
if [ ! -d "$OPENPILOT" ]; then
    echo "❌ Error: openpilot not found at $OPENPILOT"
    echo "Please install openpilot first!"
    exit 1
fi

# Check if patches exist
if [ ! -d "$ARCHIVE" ]; then
    echo "❌ Error: Patch directory not found at $ARCHIVE"
    exit 1
fi

echo "📁 Openpilot: $OPENPILOT"
echo "📦 Patches: $ARCHIVE"
echo ""

# Backup original files
echo "💾 Creating backups..."
mkdir -p "$OPENPILOT/.backups"
cp "$OPENPILOT/selfdrive/selfdrived/state.py" "$OPENPILOT/.backups/state.py.orig" 2>/dev/null || true
cp "$OPENPILOT/selfdrive/car/card.py" "$OPENPILOT/.backups/card.py.orig" 2>/dev/null || true
cp "$OPENPILOT/selfdrive/controls/controlsd.py" "$OPENPILOT/.backups/controlsd.py.orig" 2>/dev/null || true
cp "$OPENPILOT/tools/webcam/camera.py" "$OPENPILOT/.backups/camera.py.orig" 2>/dev/null || true
echo "✓ Backups saved to $OPENPILOT/.backups/"
echo ""

# Apply patches
echo "🔧 Applying patches..."

echo "  → state.py (force engagement)"
cp "$ARCHIVE/state.py" "$OPENPILOT/selfdrive/selfdrived/"

echo "  → card.py (inject fake car state)"
cp "$ARCHIVE/card.py" "$OPENPILOT/selfdrive/car/"

echo "  → controlsd.py (force latActive=True)"
cp "$ARCHIVE/controlsd.py" "$OPENPILOT/selfdrive/controls/"

echo "  → camera.py (webcam V4L2 + MJPEG fix)"
cp "$ARCHIVE/camera.py" "$OPENPILOT/tools/webcam/"

echo ""
echo "🧹 Clearing Python cache..."
find "$OPENPILOT" -name "*.pyc" -delete 2>/dev/null || true
find "$OPENPILOT" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo ""
echo "========================================"
echo "✅ All patches applied successfully!"
echo "========================================"
echo ""
echo "Patched files:"
echo "  • selfdrive/selfdrived/state.py"
echo "  • selfdrive/car/card.py"
echo "  • selfdrive/controls/controlsd.py"
echo "  • tools/webcam/camera.py"
echo ""
echo "To restore originals:"
echo "  cp $OPENPILOT/.backups/*.orig <target>"
echo ""
echo "Ready to launch LKAS!"
