#!/usr/bin/env python3
"""
Complete System Demo - Shows openpilot steering pipeline working
Simulates driving scenarios and displays steering responses
"""

import sys
import time
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
    print("Make sure openpilot is installed at ~/openpilot")
    sys.exit(1)

def print_banner():
    print("\n" + "="*70)
    print("  🚗 OPENPILOT STEERING ACTUATOR - LIVE DEMO")
    print("="*70)
    print("\n  Simulating real-world driving scenarios...")
    print("  Watch the steering commands that would be sent to your motor!\n")
    print("="*70 + "\n")

def print_steering_visual(steer_value, pwm_value):
    """Print visual representation of steering wheel"""
    # Scale -1.0 to +1.0 into 0-40 bar length
    bar_length = 40
    center = bar_length // 2
    offset = int(steer_value * center)
    position = center + offset
    position = max(0, min(bar_length - 1, position))
    
    # Create bar
    bar = [' '] * bar_length
    bar[center] = '|'  # Center line
    bar[position] = '●'  # Current position
    
    # Direction arrows
    left_arrow = '←' * max(0, -(pwm_value // 10))
    right_arrow = '→' * max(0, (pwm_value // 10))
    
    direction = "STRAIGHT"
    if pwm_value > 10:
        direction = "RIGHT"
    elif pwm_value < -10:
        direction = "LEFT"
    
    print(f"  {''.join(bar)}")
    print(f"  {left_arrow:<20} {direction:^20} {right_arrow:>20}")
    print(f"  Steer: {steer_value:+.3f}  |  PWM: {pwm_value:+4d}")

def scenario_straight_road(pm, duration=5):
    """Simulate driving on straight road"""
    print("\n📍 SCENARIO 1: Straight Road (Highway)")
    print("   Expected: Minimal steering corrections\n")
    
    start = time.time()
    count = 0
    
    while time.time() - start < duration:
        # Small corrections around zero
        elapsed = time.time() - start
        steer = 0.05 * math.sin(2 * math.pi * elapsed / 3.0)  # Tiny wobble
        pwm = int(steer * 150)
        
        if count % 10 == 0:  # Update display every 0.5s
            print(f"\r  Time: {elapsed:.1f}s ", end='')
            print_steering_visual(steer, pwm)
        
        # Publish message
        msg = messaging.new_message('carControl')
        msg.carControl.enabled = True
        msg.carControl.actuators.torque = steer
        pm.send('carControl', msg)
        
        time.sleep(0.05)  # 20 Hz
        count += 1
    
    print(f"\n  ✓ Completed: {count} steering commands sent\n")

def scenario_gentle_curve(pm, duration=8):
    """Simulate gentle curve (freeway exit)"""
    print("\n📍 SCENARIO 2: Gentle Curve (Freeway Exit)")
    print("   Expected: Smooth progressive turn\n")
    
    start = time.time()
    count = 0
    
    while time.time() - start < duration:
        elapsed = time.time() - start
        # Gradual increase then decrease
        progress = elapsed / duration
        if progress < 0.5:
            steer = 0.4 * (progress * 2)  # Ramp up
        else:
            steer = 0.4 * (2 - progress * 2)  # Ramp down
        
        pwm = int(steer * 150)
        
        if count % 10 == 0:
            print(f"\r  Time: {elapsed:.1f}s ", end='')
            print_steering_visual(steer, pwm)
        
        msg = messaging.new_message('carControl')
        msg.carControl.enabled = True
        msg.carControl.actuators.steer = steer
        pm.send('carControl', msg)
        
        time.sleep(0.05)
        count += 1
    
    print(f"\n  ✓ Completed: {count} steering commands sent\n")

def scenario_sharp_turn(pm, duration=6):
    """Simulate sharp turn (city intersection)"""
    print("\n📍 SCENARIO 3: Sharp Turn (City Intersection)")
    print("   Expected: Strong steering command\n")
    
    start = time.time()
    count = 0
    
    while time.time() - start < duration:
        elapsed = time.time() - start
        # Quick ramp to full steer, hold, then return
        if elapsed < 2:
            steer = -0.5 * (elapsed / 2)  # Ramp left
        elif elapsed < 4:
            steer = -0.5  # Hold left
        else:
            steer = -0.5 * (1 - (elapsed - 4) / 2)  # Return to center
        
        pwm = int(steer * 150)
        
        if count % 10 == 0:
            print(f"\r  Time: {elapsed:.1f}s ", end='')
            print_steering_visual(steer, pwm)
        
        msg = messaging.new_message('carControl')
        msg.carControl.enabled = True
        msg.carControl.actuators.steer = steer
        pm.send('carControl', msg)
        
        time.sleep(0.05)
        count += 1
    
    print(f"\n  ✓ Completed: {count} steering commands sent\n")

def scenario_lane_change(pm, duration=7):
    """Simulate lane change maneuver"""
    print("\n📍 SCENARIO 4: Lane Change (Passing Maneuver)")
    print("   Expected: Brief right, straighten, brief left\n")
    
    start = time.time()
    count = 0
    
    while time.time() - start < duration:
        elapsed = time.time() - start
        # Multi-phase: right → straight → left
        if elapsed < 2:
            steer = 0.3 * math.sin(math.pi * elapsed / 2)  # Smooth right
        elif elapsed < 5:
            steer = 0.0  # Straight
        else:
            steer = -0.3 * math.sin(math.pi * (elapsed - 5) / 2)  # Smooth left
        
        pwm = int(steer * 150)
        
        if count % 10 == 0:
            print(f"\r  Time: {elapsed:.1f}s ", end='')
            print_steering_visual(steer, pwm)
        
        msg = messaging.new_message('carControl')
        msg.carControl.enabled = True
        msg.carControl.actuators.steer = steer
        pm.send('carControl', msg)
        
        time.sleep(0.05)
        count += 1
    
    print(f"\n  ✓ Completed: {count} steering commands sent\n")

def main():
    print_banner()
    
    print("📡 Initializing openpilot messaging...")
    pm = messaging.PubMaster(['carControl'])
    print("✓ Connected to cereal (openpilot's messaging system)\n")
    
    print("🎬 Running driving scenarios...")
    print("   (In real setup, bridge would convert these to motor PWM)\n")
    
    try:
        scenario_straight_road(pm)
        time.sleep(1)
        
        scenario_gentle_curve(pm)
        time.sleep(1)
        
        scenario_sharp_turn(pm)
        time.sleep(1)
        
        scenario_lane_change(pm)
        
        print("\n" + "="*70)
        print("  ✅ DEMO COMPLETE!")
        print("="*70)
        print("\n  What just happened:")
        print("    1. Simulated 4 real driving scenarios")
        print("    2. Generated steering commands (-1.0 to +1.0)")
        print("    3. Converted to PWM values for motor control")
        print("    4. Published via cereal (openpilot's message bus)")
        print("\n  Next steps:")
        print("    • Connect ESP32 + motor to see actual movement")
        print("    • Add webcam to replace simulation with real vision")
        print("    • Run 'python3 launch.py' for complete system")
        print("\n" + "="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo stopped by user\n")

if __name__ == '__main__':
    main()
