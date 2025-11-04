#!/bin/bash
# Setup X11 forwarding from VM to Windows host X server

# Try to detect Windows host IP
# First try: get gateway IP (may be NAT gateway, not actual host)
GATEWAY_IP=$(ip route | grep default | awk '{print $3}')

# Try to find the actual Windows host IP by looking at the VM's IP and guessing the host
VM_IP=$(hostname -I | awk '{print $1}')
VM_SUBNET=$(echo $VM_IP | cut -d. -f1-3)

# Common pattern: if VM is 192.168.68.115, Windows is likely 192.168.68.112 or similar
# Let's try to find it by pinging common host IPs
echo "Detecting Windows host IP..."
echo "VM IP: $VM_IP"
echo "Gateway: $GATEWAY_IP"
echo ""

# Allow manual override
read -p "Enter Windows PC IP address (default: 192.168.68.112): " WINDOWS_IP
WINDOWS_IP=${WINDOWS_IP:-192.168.68.112}

echo ""
echo "======================================================================="
echo "X11 FORWARDING TO WINDOWS X SERVER"
echo "======================================================================="
echo ""
echo "Using Windows host IP: $WINDOWS_IP"
echo ""
echo "IMPORTANT: Make sure your Windows X server allows connections!"
echo ""
echo "For VcXsrv (XLaunch):"
echo "  - Check 'Disable access control' when starting"
echo "  - Or add '-ac' to the command line"
echo ""
echo "For Xming:"
echo "  - Use XLaunch with 'No Access Control'"
echo ""
echo "For X410:"
echo "  - Enable 'Allow Public Access' in settings"
echo ""
read -p "Press Enter once X server is configured to allow connections..."

# Set DISPLAY and launch
export DISPLAY=$WINDOWS_IP:0.0
echo ""
echo "Setting DISPLAY=$DISPLAY"
echo "Launching LKAS system with UI..."
echo ""

cd ~/DIY-Auto-Pilot
source ~/openpilot/.venv/bin/activate
python3 scripts/launch_lkas.py
