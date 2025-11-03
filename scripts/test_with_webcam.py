#!/usr/bin/env python3
"""
Test script to simulate openpilot steering commands
Publishes steering commands that the bridge can receive (headless, no GUI)
"""

import time
import sys
import math
from pathlib import Path

# Add openpilot to path
openpilot_path = Path.home() / "openpilot"
sys.path.insert(0, str(openpilot_path))

try:
    import cereal.messaging as messaging
    from cereal import log
except ImportError as e:
    print(f"ERROR: Cannot import cereal: {e}")
    print("Make sure PYTHONPATH includes openpilot")
    sys.exit(1)

def main():
    print("="*60)
    print("Openpilot Steering Simulator (Headless)")
    print("="*60)
    
    # Create messaging publishers
    print("\n📡 Setting up cereal messaging...")
    pm = messaging.PubMaster(['carControl'])
    print("✓ Publisher created for 'carControl'")
    
    print("\n🚗 Publishing steering commands (sine wave pattern)")
    print("   Range: -0.5 to +0.5 over 10 second cycle")
    print("   Rate: 20 Hz")
    print("\nPress Ctrl+C to stop\n")
    
    loop_count = 0
    start_time = time.time()
    
    try:
        while True:
            elapsed = time.time() - start_time
            
            # Calculate steering (sine wave for demo: -0.5 to +0.5 over 10 seconds)
            steer_normalized = 0.5 * math.sin(2 * math.pi * elapsed / 10.0)
            
            # Create carControl message with steering
            # Use torque field (normalized -1 to +1) for lateral control
            dat = messaging.new_message('carControl')
            dat.carControl.enabled = True
            dat.carControl.actuators.torque = steer_normalized
            pm.send('carControl', dat)
            
            # Display info every 20 iterations (~1 second at 20 Hz)
            loop_count += 1
            if loop_count % 20 == 0:
                pwm = int(steer_normalized * 150)  # Simulate PWM calculation
                print(f"[{elapsed:6.1f}s] Steer: {steer_normalized:+.3f} → PWM: {pwm:+4d}")
            
            # Run at 20 Hz
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user")
        elapsed = time.time() - start_time
        print(f"✓ Published {loop_count} messages over {elapsed:.1f} seconds ({loop_count/elapsed:.1f} Hz)")

if __name__ == "__main__":
    main()
