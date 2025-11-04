#!/usr/bin/env python3
"""
Test end-to-end message flow: publisher → bridge
Publishes carControl messages and monitors bridge to verify reception.
"""

import time
import subprocess
import sys
from pathlib import Path

# Add openpilot to path
openpilot_path = Path.home() / "openpilot"
sys.path.insert(0, str(openpilot_path))

import cereal.messaging as messaging


def test_end_to_end():
    """Test that bridge receives carControl messages"""
    
    print("=" * 70)
    print("END-TO-END MESSAGE FLOW TEST")
    print("=" * 70)
    print()
    
    # Start bridge process
    print("▶ Starting bridge...")
    bridge_proc = subprocess.Popen(
        ["python3", "bridge/op_serial_bridge.py", "--config", "bridge/config.yaml", "--debug"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    print(f"✓ Bridge started (PID: {bridge_proc.pid})")
    print()
    time.sleep(2)  # Give bridge time to initialize
    
    # Create publisher
    print("▶ Creating carControl publisher...")
    pm = messaging.PubMaster(['carControl'])
    print("✓ Publisher ready")
    print()
    
    # Publish test messages
    print("=" * 70)
    print("PUBLISHING TEST MESSAGES")
    print("=" * 70)
    
    test_angles = [0.0, 15.0, -15.0, 30.0, -30.0, 0.0]
    
    for angle in test_angles:
        msg = messaging.new_message('carControl')
        msg.carControl.actuators.steeringAngleDeg = angle
        
        pm.send('carControl', msg)
        print(f"📤 Published: steeringAngleDeg = {angle:+.1f}°")
        time.sleep(0.5)
    
    print()
    print("✓ All messages published")
    print()
    
    # Give bridge time to process
    print("⏳ Waiting for bridge to process messages...")
    time.sleep(2)
    
    # Read bridge output
    print()
    print("=" * 70)
    print("BRIDGE OUTPUT (last 20 lines):")
    print("=" * 70)
    
    # Terminate bridge gracefully
    bridge_proc.terminate()
    try:
        output, _ = bridge_proc.communicate(timeout=3)
        lines = output.strip().split('\n')
        for line in lines[-20:]:
            print(line)
    except subprocess.TimeoutExpired:
        bridge_proc.kill()
        print("⚠ Bridge didn't terminate gracefully")
    
    print()
    print("=" * 70)
    print("✓ TEST COMPLETE")
    print("=" * 70)
    print()
    print("Expected output:")
    print("  - Bridge should show 'Steer: XX.XX' messages (not 'No steer command')")
    print("  - Steering values should match published angles")
    print()


if __name__ == "__main__":
    test_end_to_end()
