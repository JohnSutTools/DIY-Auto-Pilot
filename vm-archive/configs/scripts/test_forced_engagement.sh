#!/bin/bash
# Test if forced engagement produces steering commands

cd ~/DIY-Auto-Pilot/scripts
source ~/openpilot/.venv/bin/activate
export DISPLAY=192.168.68.112:0.0

# Start the system in background
echo "Starting openpilot system..."
python3 launch_lkas.py > /tmp/launch.log 2>&1 &
LAUNCH_PID=$!

# Wait for system to initialize
sleep 15

# Monitor for steering commands
echo "Monitoring for steering commands (15 seconds)..."
timeout 15 python3 monitor_steering.py

# Cleanup
echo "Stopping system..."
pkill -u $USER -f "python3.*launch_lkas"
pkill -u $USER -f "python3.*selfdrive"

echo "Done!"
