#!/bin/bash
# X Server setup for WSL

# Get Windows host IP
export WINDOWS_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
export DISPLAY=$WINDOWS_IP:0.0
export LIBGL_ALWAYS_INDIRECT=1

echo "X Server Configuration:"
echo "  Windows IP: $WINDOWS_IP"
echo "  DISPLAY: $DISPLAY"
echo ""
echo "Add this to your ~/.bashrc to make it permanent:"
echo ""
echo "export DISPLAY=\$(cat /etc/resolv.conf | grep nameserver | awk '{print \$2}'):0.0"
echo "export LIBGL_ALWAYS_INDIRECT=1"
