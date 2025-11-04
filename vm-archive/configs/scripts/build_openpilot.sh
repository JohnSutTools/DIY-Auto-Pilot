#!/bin/bash
# This script is deprecated - use install.sh instead
# Kept for reference only

echo "ERROR: This script is deprecated."
echo ""
echo "Use the proper installation script instead:"
echo "  cd ~/steering-actuator"
echo "  ./scripts/install.sh"
echo ""
exit 1

echo ""
echo "✓ Openpilot build complete!"

# Add to bashrc
if ! grep -q "PYTHONPATH.*openpilot" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# Openpilot" >> ~/.bashrc
    echo "export PYTHONPATH=\"\${PYTHONPATH}:\$HOME/openpilot\"" >> ~/.bashrc
    echo "✓ Added openpilot to PYTHONPATH in ~/.bashrc"
fi

# Test cereal import
echo ""
echo "==========================================="
echo "Testing cereal import..."
echo "==========================================="

cd ~/steering-actuator
PYTHONPATH=~/openpilot python3 scripts/test_cereal.py

echo ""
echo "==========================================="
echo "✅ SETUP COMPLETE!"
echo "==========================================="
echo ""
echo "You can now run:"
echo "  cd ~/steering-actuator"
echo "  python3 launch.py"
echo ""
