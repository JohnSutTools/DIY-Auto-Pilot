#!/usr/bin/env python3
"""Quick webcam test script"""
import cv2
import sys

print("Testing webcam access...")

# Try to open camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ ERROR: Could not open webcam")
    sys.exit(1)

# Try to read a frame
ret, frame = cap.read()

if ret:
    print(f"✅ SUCCESS: Webcam working!")
    print(f"   Frame shape: {frame.shape}")
    print(f"   Resolution: {frame.shape[1]}x{frame.shape[0]}")
else:
    print("❌ ERROR: Could not read frame from webcam")
    cap.release()
    sys.exit(1)

cap.release()
print("\nWebcam test complete! Ready to run openpilot.")
