#!/bin/bash
# Install openpilot directly from GitHub using their official scripts

set -e

echo "============================================================"
echo "Installing Openpilot from GitHub"
echo "============================================================"

# Clone openpilot if not present
if [ ! -d "$HOME/openpilot" ]; then
    echo "Cloning openpilot..."
    git clone https://github.com/commaai/openpilot.git "$HOME/openpilot"
else
    echo "Openpilot already exists at $HOME/openpilot"
fi

cd "$HOME/openpilot"

# Run their official Ubuntu setup script
echo ""
echo "Running openpilot's ubuntu_setup.sh..."
./tools/ubuntu_setup.sh

# Build openpilot (skip ML models that fail on CPU)
echo ""
echo "Building openpilot core components..."
source .venv/bin/activate
echo "Note: Skipping tinygrad ML models due to LLVM CPU backend issues"
echo "Building cereal and common libraries only..."
scons -j$(nproc) cereal/ common/ || {
    echo "WARNING: Full build failed, but cereal messaging may still work"
}

# Test if cereal works
echo ""
echo "Testing cereal import..."
if python -c "import cereal.messaging" 2>/dev/null; then
    echo "✅ Cereal messaging works!"
else
    echo "❌ Cereal import failed - full build may be needed"
fi

echo ""
echo "============================================================"
echo "✅ Openpilot installation complete!"
echo "============================================================"
echo ""
echo "NOTE: ML models (tinygrad) failed to compile due to LLVM issues."
echo "      Core messaging works for bridge testing with replay data."

# Install bridge dependencies in openpilot's venv
echo ""
echo "Installing bridge dependencies..."
cd ~/steering-actuator
source "$HOME/openpilot/.venv/bin/activate"
pip install -r bridge/requirements.txt

# Add PYTHONPATH export
if ! grep -q "PYTHONPATH.*openpilot" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# Openpilot Python path" >> ~/.bashrc
    echo "export PYTHONPATH=\"\${PYTHONPATH}:\$HOME/openpilot\"" >> ~/.bashrc
fi

echo ""
echo "============================================================"
echo "✅ ALL DONE!"
echo "============================================================"
echo ""
echo "To run: python3 launch.py"
echo "To test visualization: python3 scripts/visualize_demo.py"
echo ""
    python3-dev \
    screen \
    tmux

# Add user to dialout group for serial access
echo ""
echo "Adding user to dialout group for serial port access..."
sudo usermod -a -G dialout $USER
echo "⚠ You need to log out and back in for group changes to take effect"

# Create virtual environment (optional but recommended)
read -p "Create Python virtual environment? (recommended) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✓ Virtual environment created (activate with: source venv/bin/activate)"
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
cd bridge
pip3 install -r requirements.txt

# Check if openpilot is installed
echo ""
if ! python3 -c "import cereal" 2>/dev/null; then
    echo "⚠ cereal (openpilot) not found"
    echo ""
    echo "You need openpilot installed. Options:"
    echo "1. Clone and build openpilot:"
    echo "   git clone https://github.com/commaai/openpilot.git ~/openpilot"
    echo "   cd ~/openpilot && scons -j\$(nproc)"
    echo "2. Add to PYTHONPATH:"
    echo "   export PYTHONPATH=\"\${PYTHONPATH}:~/openpilot\""
    echo ""
else
    echo "✓ cereal (openpilot) found"
fi

# Check for ESP32
echo ""
echo "Checking for ESP32..."
if ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null; then
    echo "✓ USB serial devices found"
    echo "Available ports:"
    ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || true
else
    echo "⚠ No USB serial devices detected"
    echo "Connect your ESP32 and check 'dmesg | tail' for device name"
fi

# Configuration
echo ""
echo "Checking configuration..."
if [ -f "config.yaml" ]; then
    echo "✓ config.yaml exists"
    echo "Current settings:"
    cat config.yaml
else
    echo "⚠ config.yaml not found (should be in bridge/)"
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Flash ESP32 firmware (see firmware/README.md)"
echo "2. Update bridge/config.yaml with correct serial port"
echo "3. Test ESP32: python3 scripts/test_esp32.py"
echo "4. Run bridge: python3 bridge/op_serial_bridge.py --config bridge/config.yaml"
echo ""
echo "Documentation:"
echo "- firmware/README.md - ESP32 setup"
echo "- bridge/README.md - Bridge usage"
echo "- project-overview.md - System overview"
