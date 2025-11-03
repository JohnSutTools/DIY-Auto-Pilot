#!/bin/bash
# Installation script for Ubuntu/Debian systems

set -e

echo "=========================================="
echo "Openpilot Steering Actuator - Setup"
echo "=========================================="

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "ERROR: This script is for Linux systems only"
    exit 1
fi

# Check Python version
echo "Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python 3 not found"
    exit 1
fi

# Install system dependencies
echo ""
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-venv \
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
