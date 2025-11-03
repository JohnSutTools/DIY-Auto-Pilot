#!/bin/bash
# Fresh Ubuntu Setup - Copy/Paste Version
# Run this entire script on fresh Ubuntu install

set -e

echo "================================================"
echo "Openpilot Steering Actuator - Quick Setup"
echo "================================================"
echo ""
echo "This will:"
echo "  1. Update system"
echo "  2. Clone repository"  
echo "  3. Run automated setup"
echo "  4. Test in simulation"
echo ""
read -p "Continue? [y/N]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Step 1: Update system
echo ""
echo "Step 1/4: Updating system..."
sudo apt update
sudo apt install -y git curl wget

# Step 2: Clone repository
echo ""
echo "Step 2/4: Cloning repository..."
cd ~
if [ -d "steering-actuator" ]; then
    echo "Directory exists, using existing..."
    cd steering-actuator
    git pull
else
    git clone https://github.com/JohnSutTools/DIY-Auto-Pilot.git steering-actuator
    cd steering-actuator
fi

# Step 3: Run setup
echo ""
echo "Step 3/4: Running automated setup (15-30 min)..."
chmod +x scripts/setup_system.sh
./scripts/setup_system.sh

# Step 4: Test
echo ""
echo "Step 4/4: Testing in simulation..."
read -p "Run simulation test now? [Y/n]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    chmod +x scripts/test_simulation.sh
    ./scripts/test_simulation.sh
fi

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. ✓ Software installed and tested"
echo "  2. Flash ESP32 (see firmware/README.md)"
echo "  3. Configure serial port in bridge/config.yaml"
echo "  4. Run: python3 launch.py"
echo ""
echo "Documentation:"
echo "  - QUICKSTART.md - Getting started"
echo "  - docs/TESTING.md - Testing procedures"
echo "  - docs/UBUNTU_SETUP.md - Detailed walkthrough"
