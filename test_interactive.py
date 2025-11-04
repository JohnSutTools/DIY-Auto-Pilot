#!/usr/bin/env python3
"""
INTERACTIVE TEST: Prove openpilot responds to what the camera sees
Move objects in front of camera and watch the steering change!
"""

import sys
import time
from pathlib import Path

# Add openpilot to path
openpilot_path = Path.home() / "openpilot"
sys.path.insert(0, str(openpilot_path))

import cereal.messaging as messaging

print("="*70)
print("  🎯 INTERACTIVE OPENPILOT RESPONSE TEST")
print("="*70)
print("\n🎬 TEST PROCEDURE:")
print("   1. Start with camera pointing at blank surface")
print("   2. Move your HAND across the camera view")
print("   3. Watch steering angle values change")
print("   4. If steering changes when you move = REAL DATA!")
print("   5. If steering stays same = FAKE DATA!")
print("\nMake sure camerad and modeld are running first!")
print("="*70 + "\n")

input("Press ENTER when ready to start test...")

# Subscribe to model output
sm = messaging.SubMaster(['modelV2'])

print("\n📹 MONITORING CAMERA...")
print("Move objects in front of camera NOW!\n")

frame_count = 0
steering_values = []

try:
    while frame_count < 100:
        sm.update(100)
        
        if sm.updated['modelV2']:
            model = sm['modelV2']
            frame_count += 1
            
            # Calculate steering (same as bridge does)
            if hasattr(model.position, 'y') and len(model.position.y) > 5:
                lookahead_idx = min(5, len(model.position.y) - 1)
                lateral_offset = model.position.y[lookahead_idx]
                lookahead_dist = model.position.x[lookahead_idx]
                
                import math
                if lookahead_dist > 0.1:
                    steer_rad = math.atan2(lateral_offset, lookahead_dist)
                    steer_deg = steer_rad * 57.3
                else:
                    steer_deg = 0
                    
                steering_values.append(steer_deg)
                
                # Lane count
                lane_count = len(model.laneLines) if hasattr(model, 'laneLines') else 0
                
                # Print with visual indicator
                bars = "█" * int(abs(steer_deg * 5))
                direction = "→" if steer_deg > 0.5 else "←" if steer_deg < -0.5 else "="
                
                print(f"[{frame_count:3d}] Steer: {steer_deg:+6.1f}° {direction} {bars:20s} Lanes: {lane_count}")
                
            time.sleep(0.05)
            
except KeyboardInterrupt:
    print("\n\n🛑 Stopped")

# Analysis
print("\n\n" + "="*70)
print("  📊 TEST RESULTS")
print("="*70)

if len(steering_values) > 10:
    import statistics
    avg = statistics.mean(steering_values)
    std_dev = statistics.stdev(steering_values)
    min_steer = min(steering_values)
    max_steer = max(steering_values)
    range_steer = max_steer - min_steer
    
    print(f"\n📈 Steering Statistics:")
    print(f"   Average: {avg:+.2f}°")
    print(f"   Std Dev: {std_dev:.2f}°")
    print(f"   Range: {min_steer:+.2f}° to {max_steer:+.2f}° (span: {range_steer:.2f}°)")
    
    print(f"\n🔍 VERDICT:")
    if range_steer > 2.0:
        print("   ✅ REAL DATA - Steering changed significantly!")
        print("   💡 Openpilot is responding to camera input")
    elif range_steer > 0.5:
        print("   ⚠️  SMALL CHANGES - May be real but camera sees similar scene")
        print("   💡 Try moving more objects in front of camera")
    else:
        print("   ❌ NO SIGNIFICANT CHANGE - Possible issues:")
        print("      • Camera not working")
        print("      • modeld not processing frames")
        print("      • Camera seeing unchanging scene")
    
print("="*70 + "\n")
