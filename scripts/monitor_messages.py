#!/usr/bin/env python3
"""
Diagnostic tool to monitor cereal messaging bus
Shows what messages are being published
"""

import sys
import time
from pathlib import Path

# Add openpilot to path
openpilot_path = Path.home() / "openpilot"
sys.path.insert(0, str(openpilot_path))

import cereal.messaging as messaging


def monitor_messages(duration=10):
    """Monitor all carControl and controlsState messages"""
    
    print("=" * 70)
    print("CEREAL MESSAGING MONITOR")
    print("=" * 70)
    print()
    print("Monitoring topics: carControl, controlsState")
    print(f"Duration: {duration} seconds")
    print()
    print("=" * 70)
    print()
    
    sm = messaging.SubMaster(['carControl', 'controlsState'])
    
    start_time = time.time()
    car_control_count = 0
    controls_state_count = 0
    
    while time.time() - start_time < duration:
        sm.update(10)  # 10ms timeout
        
        if sm.updated['carControl']:
            car_control_count += 1
            cc = sm['carControl']
            if hasattr(cc, 'actuators') and hasattr(cc.actuators, 'steeringAngleDeg'):
                angle = cc.actuators.steeringAngleDeg
                print(f"[{time.time() - start_time:6.2f}s] carControl: steeringAngleDeg = {angle:+.2f}°")
            else:
                print(f"[{time.time() - start_time:6.2f}s] carControl: (no steering angle)")
        
        if sm.updated['controlsState']:
            controls_state_count += 1
            cs = sm['controlsState']
            if hasattr(cs, 'desiredCurvature'):
                curvature = cs.desiredCurvature
                print(f"[{time.time() - start_time:6.2f}s] controlsState: curvature = {curvature:.4f}")
        
        time.sleep(0.01)  # 100 Hz polling
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"carControl messages received: {car_control_count}")
    print(f"controlsState messages received: {controls_state_count}")
    print()
    
    if car_control_count == 0 and controls_state_count == 0:
        print("⚠ NO MESSAGES RECEIVED")
        print()
        print("Possible causes:")
        print("  1. No publisher is running (controlsd not active)")
        print("  2. Publisher/subscriber mismatch (different process contexts)")
        print("  3. ZMQ socket binding issue")
    else:
        print("✓ Messages are being published successfully")


if __name__ == "__main__":
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    monitor_messages(duration)
