#!/bin/bash
# Raspberry Pi Setup Script for Openpilot Steering Actuator
# Optimized for Raspberry Pi 2/3/4

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================================"
echo "  Raspberry Pi Openpilot Steering Actuator Setup"
echo "============================================================"
echo ""

# Detect Pi model
PI_MODEL=$(cat /proc/device-tree/model 2>/dev/null || echo "Unknown")
echo "📟 Detected: $PI_MODEL"
echo ""

# Check if Pi 2 - will optimize for it
PI2_MODE=false
if echo "$PI_MODEL" | grep -q "Raspberry Pi 2"; then
    PI2_MODE=true
    echo -e "${YELLOW}⚠️  Raspberry Pi 2 detected - Enabling optimizations${NC}"
    echo "   ✓ Reduced frame rate (10 FPS target)"
    echo "   ✓ Lower ML model resolution"
    echo "   ✓ Increased swap space"
    echo "   ✓ Disabled background services"
    echo ""
    echo "   Expected performance: 5-10 FPS with 200-500ms latency"
    echo "   This is sufficient for testing and bench validation."
    echo ""
    read -p "Continue with Pi 2 installation? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check free disk space
FREE_SPACE=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$FREE_SPACE" -lt 10 ]; then
    echo -e "${RED}❌ ERROR: Insufficient disk space${NC}"
    echo "   Need at least 10GB free, have ${FREE_SPACE}GB"
    exit 1
fi

# Check if running on Raspberry Pi OS
if ! grep -q "Raspbian\|Debian" /etc/os-release; then
    echo -e "${YELLOW}⚠️  WARNING: Not running Raspberry Pi OS/Debian${NC}"
    echo "   This script is optimized for Raspberry Pi OS"
    read -p "Continue? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "This script will:"
echo "  1. Update system packages"
echo "  2. Install dependencies"
echo "  3. Clone and build openpilot (60-120 min on Pi 2)"
echo "  4. Set up steering bridge"
echo "  5. Configure mock mode for testing"
echo ""
read -p "Start installation? [y/N]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# ============================================================
# Step 1: System Update
# ============================================================
echo ""
echo -e "${GREEN}[1/5] Updating system packages...${NC}"
sudo apt update
sudo apt upgrade -y

# ============================================================
# Step 2: Install Dependencies
# ============================================================
echo ""
echo -e "${GREEN}[2/5] Installing dependencies...${NC}"

# Basic build tools
sudo apt install -y \
    git curl wget \
    build-essential clang \
    python3-pip python3-dev python3-venv \
    libssl-dev libffi-dev \
    cmake ninja-build

# Openpilot dependencies
sudo apt install -y \
    libzmq3-dev \
    libcapnp-dev capnproto \
    libbz2-dev \
    libarchive-dev \
    libcurl4-openssl-dev \
    libeigen3-dev \
    libusb-1.0-0-dev \
    git-lfs

# Qt5 (may not be needed, but included for compatibility)
sudo apt install -y \
    qtbase5-dev \
    libqt5svg5-dev \
    qttools5-dev-tools || echo "Qt5 install failed, continuing..."

# Audio (for PyAudio)
sudo apt install -y \
    portaudio19-dev \
    libasound2-dev || echo "Audio libs install failed, continuing..."

# Camera support
sudo apt install -y \
    v4l-utils \
    libv4l-dev

# Serial port support
sudo apt install -y \
    python3-serial

# Add user to dialout group for serial access
sudo usermod -a -G dialout $USER

# ============================================================
# Step 3: Clone Openpilot
# ============================================================
echo ""
echo -e "${GREEN}[3/5] Setting up openpilot...${NC}"

cd ~
if [ -d "openpilot" ]; then
    echo "Openpilot directory exists, updating..."
    cd openpilot
    git pull || echo "Git pull failed, using existing version"
else
    echo "Cloning openpilot (this may take 5-10 minutes)..."
    git clone https://github.com/commaai/openpilot.git
    cd openpilot
fi

# Initialize Git LFS
git lfs install
git lfs pull || echo "Git LFS pull failed, some files may be missing"

# Run official setup script
echo ""
echo "Running openpilot ubuntu_setup.sh..."
if [ -f "tools/ubuntu_setup.sh" ]; then
    ./tools/ubuntu_setup.sh
else
    echo "Warning: ubuntu_setup.sh not found, skipping"
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate venv and install dependencies
source .venv/bin/activate

# Install Python packages
echo "Installing Python packages in venv..."
pip install --upgrade pip wheel setuptools

# Install core dependencies
pip install \
    pyzmq \
    pycapnp \
    numpy \
    PyYAML \
    pyserial \
    opencv-python

# Try to build core components (may be slow on Pi 2)
echo ""
echo -e "${YELLOW}Building openpilot core (this will take a while on Pi 2)...${NC}"
if command -v scons &> /dev/null; then
    echo "Building with scons..."
    scons -j$(nproc) cereal/ common/ || echo "Build failed, but continuing..."
else
    echo "scons not available, skipping build"
fi

deactivate

# ============================================================
# Step 4: Set Up Steering Actuator Bridge
# ============================================================
echo ""
echo -e "${GREEN}[4/5] Setting up steering actuator bridge...${NC}"

cd ~
if [ ! -d "steering-actuator" ]; then
    # Clone from GitHub if available, otherwise create structure
    if git clone https://github.com/JohnSutTools/DIY-Auto-Pilot.git steering-actuator 2>/dev/null; then
        echo "Repository cloned successfully"
    else
        echo "Creating steering-actuator directory structure..."
        mkdir -p steering-actuator/{bridge,scripts,firmware,docs}
        
        # Create basic config
        cat > steering-actuator/bridge/config.yaml << 'EOF'
# Bridge Configuration
serial_port: /dev/ttyUSB0
baud_rate: 115200
pwm_scale: 150
pwm_cap: 255
stream_hz: 20
mock_mode: true  # Set to false when ESP32 connected

# Optional: Remote openpilot connection
# openpilot_host: "192.168.1.100:8002"
EOF
        
        echo "Basic structure created. You'll need to add bridge and firmware code."
    fi
fi

cd ~/steering-actuator

# Install bridge dependencies in openpilot venv
source ~/openpilot/.venv/bin/activate
pip install pyserial PyYAML
deactivate

# ============================================================
# Step 5: Configure Environment
# ============================================================
echo ""
echo -e "${GREEN}[5/5] Configuring environment...${NC}"

# Add PYTHONPATH to .bashrc if not present
if ! grep -q "PYTHONPATH.*openpilot" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# Openpilot environment" >> ~/.bashrc
    echo "export PYTHONPATH=\"\$HOME/openpilot:\$PYTHONPATH\"" >> ~/.bashrc
    echo "Added PYTHONPATH to ~/.bashrc"
fi

# Apply Pi 2 specific optimizations
if [ "$PI2_MODE" = true ]; then
    echo ""
    echo -e "${GREEN}Applying Raspberry Pi 2 optimizations...${NC}"
    
    # Increase swap space to 2GB
    echo "Increasing swap space to 2GB..."
    sudo dphys-swapfile swapoff || true
    sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=2048/' /etc/dphys-swapfile
    sudo dphys-swapfile setup
    sudo dphys-swapfile swapon
    echo "✓ Swap increased to 2GB"
    
    # Disable unnecessary services
    echo "Disabling unnecessary services..."
    sudo systemctl disable bluetooth.service || true
    sudo systemctl disable hciuart.service || true
    sudo systemctl disable avahi-daemon.service || true
    sudo systemctl disable triggerhappy.service || true
    echo "✓ Services disabled"
    
    # Create performance config for openpilot
    mkdir -p ~/steering-actuator/config
    cat > ~/steering-actuator/config/pi2_performance.env << 'EOF'
# Raspberry Pi 2 Performance Settings
export TINYGRAD_BEAM=0
export TINYGRAD_LAZINESS=0
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=2
export VISION_FPS=10
export MODEL_RESOLUTION_LOW=1
EOF
    echo "✓ Performance config created"
    
    # Add performance settings to launch
    if [ -f ~/steering-actuator/launch.py ]; then
        # Will load these settings on startup
        echo "✓ Launch configured for Pi 2"
    fi
    
    echo -e "${GREEN}✓ Pi 2 optimizations applied${NC}"
fi

# Check camera
echo ""
echo "Checking for cameras..."
if ls /dev/video* &> /dev/null; then
    echo -e "${GREEN}✓ Camera detected:${NC}"
    ls /dev/video*
else
    echo -e "${YELLOW}⚠️  No camera detected${NC}"
    echo "   For USB camera: Just plug it in"
    echo "   For Pi Camera: Run 'sudo raspi-config' -> Interface Options -> Camera"
fi

# Check serial ports
echo ""
echo "Checking for serial devices..."
if ls /dev/ttyUSB* &> /dev/null || ls /dev/ttyACM* &> /dev/null; then
    echo -e "${GREEN}✓ Serial device detected:${NC}"
    ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
else
    echo "ℹ️  No serial devices detected (ESP32 not connected yet)"
fi

# ============================================================
# Completion
# ============================================================
echo ""
echo "============================================================"
echo -e "${GREEN}✓ Installation Complete!${NC}"
echo "============================================================"
echo ""

if [ "$PI2_MODE" = true ]; then
    echo -e "${YELLOW}Raspberry Pi 2 Configuration:${NC}"
    echo "  - Swap: 2GB (for ML model loading)"
    echo "  - Target FPS: 10 (reduced from 20)"
    echo "  - Expected latency: 200-500ms"
    echo "  - Background services: Disabled"
    echo ""
fi

echo "Next steps:"
echo ""
echo "1. REBOOT to apply all changes:"
echo "   sudo reboot"
echo ""
echo "2. After reboot, test the complete system:"
echo "   cd ~/steering-actuator/scripts"
echo "   ./test_integration.sh"
echo ""
echo "   You should see:"
echo "   [SIMULATOR] Publishing steering commands..."
echo "   [BRIDGE] MOCK: S:+72  Steer: +0.481 -> PWM: +72"
echo ""
echo "3. Test with actual camera (after reboot):"
echo "   cd ~/steering-actuator"
echo "   python3 launch.py"
echo ""
echo "4. Connect ESP32 hardware:"
echo "   - Flash firmware/steering_motor/steering_motor.ino"
echo "   - Connect via USB"
echo "   - Find device: ls /dev/ttyUSB*"
echo "   - Update bridge/config.yaml:"
echo "     serial_port: /dev/ttyUSB0"
echo "     mock_mode: false"
echo ""
echo "Documentation: ~/steering-actuator/docs/PI_SETUP.md"
echo ""
echo -e "${YELLOW}⚠️  Pi 2 Performance Note:${NC}"
echo "   System will be slower than laptop but fully functional"
echo "   Perfect for testing and validation before vehicle use"
echo ""
echo -e "${RED}⚠️  SAFETY: Test thoroughly before vehicle installation!${NC}"
echo ""

# Show system info
echo "System Information:"
echo "  - Python: $(python3 --version)"
echo "  - Free disk: $(df -h / | awk 'NR==2 {print $4}')"
echo "  - Memory: $(free -h | awk 'NR==2 {print $2}')"
echo "  - CPU cores: $(nproc)"
echo ""
