#!/usr/bin/env python3
"""
Test if openpilot is actually processing REAL camera frames
This will print raw data from modelV2 to prove it's not fake
"""

import sys
import time
from pathlib import Path

# Add openpilot to path
openpilot_path = Path.home() / "openpilot"
sys.path.insert(0, str(openpilot_path))

import cereal.messaging as messaging

print("="*70)
print("  🔍 OPENPILOT REAL DATA VERIFICATION TEST")
print("="*70)
print("\nThis will show RAW values from openpilot's modelV2")
print("If the numbers change frame-to-frame, it's REAL data!")
print("If the numbers are identical every time, it's FAKE data!")
print("\nMake sure camerad and modeld are running first!")
print("="*70 + "\n")

# Subscribe to model output
sm = messaging.SubMaster(['modelV2'])

frame_count = 0
last_frame_id = None
last_position_y = []

try:
    while frame_count < 30:  # Test 30 frames
        sm.update(1000)  # 1 second timeout
        
        if sm.updated['modelV2']:
            model = sm['modelV2']
            frame_count += 1
            
            # Get frame ID (should increment if real data)
            frame_id = model.frameId if hasattr(model, 'frameId') else 0
            
            # Get path position data (should vary if real camera)
            position_y = list(model.position.y[:10]) if hasattr(model.position, 'y') else []
            
            # Get lane line count (should vary based on what camera sees)
            lane_count = len(model.laneLines) if hasattr(model, 'laneLines') else 0
            
            # Check if data is changing
            frame_changed = (frame_id != last_frame_id) if last_frame_id is not None else True
            position_changed = (position_y != last_position_y) if last_position_y else True
            
            print(f"\n📊 Frame {frame_count}:")
            print(f"   frameId: {frame_id} {'✓ CHANGED' if frame_changed else '❌ SAME AS LAST'}")
            print(f"   Lane lines detected: {lane_count}")
            print(f"   Path Y positions (first 5): {[f'{y:.3f}' for y in position_y[:5]]}")
            print(f"   Position data: {'✓ CHANGED' if position_changed else '❌ SAME AS LAST'}")
            
            # Save for comparison
            last_frame_id = frame_id
            last_position_y = position_y
            
            time.sleep(0.1)
        else:
            print(".", end="", flush=True)
            time.sleep(0.1)
            
except KeyboardInterrupt:
    print("\n\n🛑 Stopped by user")

print("\n\n" + "="*70)
print("  📊 VERIFICATION RESULTS")
print("="*70)
print(f"\nFrames analyzed: {frame_count}")

if frame_count > 5:
    print("\n✅ OPENPILOT IS PROCESSING DATA!")
    print("   (If frameId incremented, data is being updated)")
    print("\n💡 Now point your camera at different things:")
    print("   - A blank wall (should see fewer lanes)")
    print("   - Paper with drawn lines (should see more lanes)")
    print("   - Your hand moving (should see position changes)")
else:
    print("\n❌ NO DATA RECEIVED!")
    print("   Make sure camerad and modeld are running!")

print("="*70 + "\n")
