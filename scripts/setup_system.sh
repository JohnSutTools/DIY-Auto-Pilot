#!/bin/bash
# Complete system setup script
# Sets up openpilot + your steering actuator as a unified system

set -e

echo "=========================================="
echo "Openpilot Steering Actuator - Full Setup"
echo "=========================================="
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "ERROR: This system requires Linux (Ubuntu/Debian)"
    echo "Raspberry Pi OS is also supported"
    exit 1
fi

# Check Python version
echo "Checking Python 3.8+..."
python3 --version
PYTHON_VERSION=$(python3 -c 'import sys; print(sys.version_info.major * 100 + sys.version_info.minor)')
if [ "$PYTHON_VERSION" -lt 308 ]; then
    echo "ERROR: Python 3.8+ required (found version below 3.8)"
    exit 1
fi
echo "✓ Python version OK"

# System dependencies
echo ""
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    git \
    curl \
    build-essential \
    python3-pip \
    python3-dev \
    libffi-dev \
    libssl-dev \
    libzmq5-dev \
    capnproto \
    libcapnp-dev \
    clang \
    scons \
    gcc \
    g++ \
    ffmpeg \
    libavformat-dev \
    libavcodec-dev \
    libavutil-dev \
    libswscale-dev \
    libv4l-dev \
    v4l-utils

# Serial port access
echo ""
echo "Setting up serial port access..."
sudo usermod -a -G dialout $USER
echo "⚠️  You need to log out and back in for serial port access"

# Install openpilot
OPENPILOT_DIR="$HOME/openpilot"

if [ -d "$OPENPILOT_DIR" ]; then
    echo ""
    echo "Openpilot directory exists: $OPENPILOT_DIR"
    read -p "Rebuild openpilot? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$OPENPILOT_DIR"
        git pull
        echo "Installing/updating Python dependencies..."
        ./tools/install_python_dependencies.sh
        echo "Building..."
        scons -j$(nproc)
    fi
else
    echo ""
    echo "Installing openpilot..."
    cd ~
    git clone --depth 1 https://github.com/commaai/openpilot.git
    cd openpilot
    git checkout release3
    
    echo ""
    echo "Installing openpilot Python dependencies..."
    ./tools/install_python_dependencies.sh
    
    echo ""
    echo "Building openpilot (this takes 10-30 minutes)..."
    scons -j$(nproc)
fi

# Add to bashrc if not already there
if ! grep -q "PYTHONPATH.*openpilot" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# Openpilot" >> ~/.bashrc
    echo "export PYTHONPATH=\"\${PYTHONPATH}:\$HOME/openpilot\"" >> ~/.bashrc
    echo "✓ Added openpilot to PYTHONPATH in ~/.bashrc"
fi

# Install Python dependencies for bridge
echo ""
echo "Installing bridge dependencies..."
cd "$(dirname "$0")/.."
pip3 install -r bridge/requirements.txt

# Configure webcam
echo ""
echo "Webcam setup..."
echo "Listing available video devices:"
v4l2-ctl --list-devices || echo "No cameras detected yet"

# Test ESP32
echo ""
echo "Checking for ESP32..."
if ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null; then
    echo "✓ USB serial devices found:"
    ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || true
    
    read -p "Test ESP32 now? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 scripts/test_esp32.py
    fi
else
    echo "⚠️  No ESP32 detected"
    echo "Connect ESP32 and check 'dmesg | tail' for device name"
fi

# Create systemd service (optional)
echo ""
read -p "Create systemd service for auto-start on boot? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
    SERVICE_FILE="/etc/systemd/system/openpilot-steering.service"
    
    sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Openpilot Steering Actuator System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $SCRIPT_DIR/launch.py --config $SCRIPT_DIR/bridge/config.yaml
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable openpilot-steering.service
    
    echo "✓ Systemd service created"
    echo "  Start: sudo systemctl start openpilot-steering"
    echo "  Stop:  sudo systemctl stop openpilot-steering"
    echo "  Logs:  journalctl -u openpilot-steering -f"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. ✓ Openpilot installed at: $OPENPILOT_DIR"
echo "2. Flash ESP32 firmware (see firmware/README.md)"
echo "3. Configure bridge/config.yaml with your serial port"
echo "4. Connect USB webcam"
echo "5. Launch system:"
echo ""
echo "   python3 launch.py"
echo ""
echo "The system will:"
echo "  - Start openpilot with webcam support"
echo "  - Enable LKAS only (no longitudinal control)"
echo "  - Start steering bridge"
echo "  - Run as unified system"
echo ""
echo "⚠️  Log out and back in for serial port access!"
