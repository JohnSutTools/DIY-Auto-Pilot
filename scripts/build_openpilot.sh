#!/bin/bash
# Quick fix script - installs dependencies, builds openpilot and tests the environment

set -e

echo "==========================================="
echo "Installing Openpilot Dependencies"
echo "==========================================="

cd ~/openpilot

# Install Python dependencies first
echo "Installing Python dependencies (this may take a few minutes)..."
./tools/install_python_dependencies.sh

echo ""
echo "✓ Python dependencies installed!"

echo ""
echo "==========================================="
echo "Building Openpilot"
echo "==========================================="

# Build openpilot
echo "Building openpilot (this takes 10-15 minutes)..."
scons -j$(nproc)

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
