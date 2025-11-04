#!/bin/bash
# Native Ubuntu Setup Script for DIY Auto Pilot LKAS
# Installs all dependencies and builds openpilot with GPU support
# Run on fresh Ubuntu 24.04 installation

set -e

echo "========================================================================"
echo "DIY AUTO PILOT - NATIVE UBUNTU SETUP"
echo "========================================================================"
echo ""
echo "This script will install:"
echo "  • Build tools and dependencies"
echo "  • Python 3.11+"
echo "  • OpenCL drivers (Intel GPU)"
echo "  • OpenCV with V4L2 support"
echo "  • openpilot (full build)"
echo "  • Project dependencies"
echo ""
echo "Estimated time: 15-30 minutes"
echo "Internet connection required"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."
echo ""

# Update system
echo "========================================"
echo "Step 1/7: Updating system packages"
echo "========================================"
sudo apt update
sudo apt upgrade -y

# Install build tools
echo ""
echo "========================================"
echo "Step 2/7: Installing build tools"
echo "========================================"
sudo apt install -y \
    git \
    curl \
    wget \
    build-essential \
    cmake \
    pkg-config \
    clang \
    libtool \
    autoconf \
    automake

# Install Python and dependencies
echo ""
echo "========================================"
echo "Step 3/7: Installing Python environment"
echo "========================================"
sudo apt install -y \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    python3-opencv

# Install OpenCL for GPU acceleration
echo ""
echo "========================================"
echo "Step 4/7: Installing OpenCL drivers"
echo "========================================"
sudo apt install -y \
    intel-opencl-icd \
    ocl-icd-opencl-dev \
    opencl-headers \
    clinfo

# Verify OpenCL
echo ""
echo "Verifying OpenCL installation..."
if command -v clinfo &> /dev/null; then
    echo "✓ clinfo installed"
    clinfo | grep -A2 "Platform Name" || echo "⚠ No OpenCL platforms found (might need reboot)"
else
    echo "⚠ clinfo not found"
fi

# Install media libraries
echo ""
echo "========================================"
echo "Step 5/7: Installing media libraries"
echo "========================================"
sudo apt install -y \
    libopencv-dev \
    libavformat-dev \
    libavcodec-dev \
    libavutil-dev \
    libswscale-dev \
    libv4l-dev \
    v4l-utils \
    ffmpeg

# Add user to video group for camera access
echo ""
echo "Adding $USER to video group for camera access..."
sudo usermod -aG video $USER
echo "✓ User added to video group (log out and back in to apply)"

# Clone and build openpilot
echo ""
echo "========================================"
echo "Step 6/7: Installing openpilot"
echo "========================================"

if [ -d "$HOME/openpilot" ]; then
    echo "⚠ openpilot directory already exists at $HOME/openpilot"
    read -p "Remove and reinstall? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$HOME/openpilot"
    else
        echo "Skipping openpilot installation"
        exit 0
    fi
fi

echo "Cloning openpilot (this may take a few minutes)..."
cd "$HOME"
git clone --depth 1 https://github.com/commaai/openpilot.git
cd openpilot

echo ""
echo "Creating Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo ""
echo "Installing openpilot dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Building openpilot (this takes 10-20 minutes)..."
scons -j$(nproc)

echo ""
echo "✓ openpilot built successfully!"

# Install project dependencies
echo ""
echo "========================================"
echo "Step 7/7: Installing project dependencies"
echo "========================================"

# Install serial for bridge
pip install pyserial pyyaml

echo ""
echo "✓ All dependencies installed!"

# Summary
echo ""
echo "========================================================================"
echo "✅ SETUP COMPLETE!"
echo "========================================================================"
echo ""
echo "Installed:"
echo "  ✓ Build tools and Python"
echo "  ✓ OpenCL drivers (Intel GPU)"
echo "  ✓ OpenCV with V4L2"
echo "  ✓ openpilot at ~/openpilot"
echo "  ✓ Project dependencies"
echo ""
echo "Next steps:"
echo "  1. Log out and back in (for video group permissions)"
echo "  2. Run: cd ~/DIY-Auto-Pilot"
echo "  3. Run: ./vm-archive/apply-patches.sh"
echo "  4. Run: ~/openpilot/.venv/bin/python3 scripts/setup_honda_civic_carparams.py"
echo "  5. Connect webcam"
echo "  6. Run: ~/openpilot/.venv/bin/python3 scripts/launch_lkas.py --no-ui"
echo ""
echo "See vm-archive/NATIVE_UBUNTU_GUIDE.md for detailed instructions"
echo ""
echo "========================================================================"
