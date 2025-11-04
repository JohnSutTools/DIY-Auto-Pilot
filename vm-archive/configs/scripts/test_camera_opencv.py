#!/usr/bin/env python3
import cv2
import time

device = "/dev/video0"
print(f"Opening {device}...")
cap = cv2.VideoCapture(device)

if not cap.isOpened():
    print("❌ Failed to open camera")
    exit(1)

print("✅ Camera opened")

# Try to set resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280.0)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720.0)
cap.set(cv2.CAP_PROP_FPS, 25.0)

# Get actual resolution
W = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
H = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
FPS = cap.get(cv2.CAP_PROP_FPS)

print(f"Resolution: {W}x{H} @ {FPS} FPS")

# Try to read 5 frames
print("\nReading frames...")
for i in range(5):
    ret, frame = cap.read()
    print(f"Frame {i+1}: ret={ret}, shape={frame.shape if ret else None}")
    if not ret:
        print("❌ Failed to read frame!")
        break
    time.sleep(0.1)

cap.release()
print("\n✓ Test complete")
