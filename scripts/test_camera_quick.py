#!/usr/bin/env python3
import cv2
cap = cv2.VideoCapture(0)
print(f"Camera opened: {cap.isOpened()}")
if cap.isOpened():
    ret, frame = cap.read()
    print(f"Frame read: {ret}")
    if ret:
        print(f"Frame shape: {frame.shape}")
        print("✅ Camera is working!")
    else:
        print("❌ Failed to read frame")
else:
    print("❌ Failed to open camera")
cap.release()
