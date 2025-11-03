#!/bin/bash
# Quick fix script - installs dependencies, builds openpilot and tests the environment

set -e

echo "==========================================="
echo "Installing System Dependencies"
echo "==========================================="

# Install system libraries needed for openpilot Python packages
echo "Installing required system libraries..."
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pyaudio

echo ""
echo "✓ System dependencies installed!"

echo ""
echo "==========================================="
echo "Initializing Openpilot Submodules"
echo "==========================================="

cd ~/openpilot

# Initialize git submodules (rednose, panda, opendbc, etc.)
echo "Initializing git submodules (rednose, panda, etc.)..."
git submodule update --init --recursive

echo ""
echo "✓ Submodules initialized!"

echo ""
echo "==========================================="
echo "Installing Openpilot Python Dependencies"
echo "==========================================="

# Install Python dependencies
echo "Installing Python dependencies (this may take a few minutes)..."
./tools/install_python_dependencies.sh

echo ""
echo "✓ Python dependencies installed!"

echo ""
echo "==========================================="
echo "Building Openpilot"
echo "==========================================="

# Activate the virtual environment that was just created
echo "Activating openpilot virtual environment..."
source .venv/bin/activate

# Verify we're using the right Python
echo "Using Python: $(which python3)"
echo "Python version: $(python3 --version)"

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
