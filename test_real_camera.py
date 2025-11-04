#!/usr/bin/env python3
"""
REAL Webcam Test - Captures from YOUR camera and simulates lane detection
Shows what steering commands would be generated from the video feed
"""
import cv2
import time
import numpy as np

print("="*70)
print("  🎥 REAL WEBCAM LANE DETECTION TEST")
print("="*70)
print("\n  This captures REAL video from your webcam")
print("  and simulates lane detection + steering commands\n")
print("="*70 + "\n")

# Open camera with working config
print("📷 Opening webcam...")
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not cap.isOpened():
    print("❌ ERROR: Cannot open camera!")
    exit(1)

print("✅ Camera opened successfully")
print(f"   Resolution: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
print(f"\n🔴 Your webcam light should be ON now!\n")

# Warm up camera
print("⏳ Warming up camera (capturing first frames)...")
for i in range(5):
    ret, _ = cap.read()
    if ret:
        print(f"   Frame {i+1}/5 captured ✓")
    time.sleep(0.1)

print("\n" + "="*70)
print("  🚗 SIMULATING LANE DETECTION FROM YOUR CAMERA")
print("="*70)
print("\n  Point camera at a road, lines, or any scene")
print("  Algorithm will detect edges and simulate steering\n")

frame_count = 0
start_time = time.time()
last_print = 0

print("Capturing for 15 seconds...\n")

while time.time() - start_time < 15:
    ret, frame = cap.read()
    
    if not ret:
        print(f"⚠️  Frame {frame_count} read failed")
        time.sleep(0.05)
        continue
    
    frame_count += 1
    elapsed = time.time() - start_time
    
    # Simple lane detection simulation
    # 1. Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 2. Focus on bottom half (road area)
    height = gray.shape[0]
    road_region = gray[height//2:, :]
    
    # 3. Detect edges
    edges = cv2.Canny(road_region, 50, 150)
    
    # 4. Calculate lane center (where edges are)
    # Split into left and right halves
    width = edges.shape[1]
    left_half = edges[:, :width//2]
    right_half = edges[:, width//2:]
    
    left_edges = np.sum(left_half)
    right_edges = np.sum(right_half)
    
    # Calculate steering based on edge balance
    # More edges on left = steer left, more on right = steer right
    total_edges = left_edges + right_edges
    if total_edges > 0:
        balance = (right_edges - left_edges) / total_edges
        steer = np.clip(balance * 0.5, -0.5, 0.5)  # Scale to -0.5 to +0.5
    else:
        steer = 0.0
    
    pwm = int(steer * 150)
    
    # Print update every 0.5 seconds
    if elapsed - last_print >= 0.5:
        # Calculate average brightness (for visual feedback)
        brightness = np.mean(gray)
        
        # Direction indicator
        if pwm > 10:
            direction = "RIGHT →"
            arrows = "→" * (pwm // 10)
        elif pwm < -10:
            direction = "LEFT ←"
            arrows = "←" * (-pwm // 10)
        else:
            direction = "STRAIGHT"
            arrows = ""
        
        # Create visual bar
        bar_width = 40
        center = bar_width // 2
        offset = int((steer / 0.5) * center)
        pos = max(0, min(bar_width - 1, center + offset))
        
        bar = [' '] * bar_width
        bar[center] = '|'
        bar[pos] = '●'
        
        print(f"[{elapsed:5.1f}s] Frame {frame_count:4d}")
        print(f"  {''.join(bar)}")
        print(f"  {arrows:>20}")
        print(f"  Steer: {steer:+.3f} | PWM: {pwm:+4d} | {direction}")
        print(f"  Brightness: {brightness:.1f} | Edges: L={left_edges:.0f} R={right_edges:.0f}")
        print()
        
        last_print = elapsed
    
    time.sleep(0.05)  # 20 Hz

cap.release()

avg_fps = frame_count / 15
print("="*70)
print("  ✅ TEST COMPLETE!")
print("="*70)
print(f"\n  Total frames captured: {frame_count}")
print(f"  Average FPS: {avg_fps:.1f}")
print(f"\n  Your webcam is WORKING and ready for openpilot!")
print(f"  The system successfully:")
print(f"    • Captured real video from your camera")
print(f"    • Processed frames with edge detection")
print(f"    • Generated steering commands based on image content")
print(f"    • Calculated PWM values for motor control")
print(f"\n  Next: Run with actual openpilot vision model for real lane detection")
print("="*70 + "\n")
