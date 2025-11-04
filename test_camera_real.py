#!/usr/bin/env python3
"""Test what the camera is actually seeing"""
import cv2
import numpy as np
import sys

camera_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
print(f"Opening camera /dev/video{camera_id}...")
cap = cv2.VideoCapture(camera_id)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

ret, frame = cap.read()
print(f"\n📷 Camera read successful: {ret}")

if ret:
    print(f"   Frame shape: {frame.shape}")
    print(f"   Mean brightness: {frame.mean():.1f} (0=black, 255=white)")
    print(f"   Min/Max values: {frame.min()}/{frame.max()}")
    print(f"   Standard deviation: {frame.std():.1f}")
    
    # Check if it's mostly black
    if frame.mean() < 10:
        print("\n⚠️  WARNING: Camera sees mostly BLACK!")
        print("   Your webcam might be covered or pointing at something dark.")
    elif frame.mean() > 240:
        print("\n⚠️  WARNING: Camera sees mostly WHITE!")
        print("   Your webcam might be pointing at a bright light.")
    else:
        print("\n✅ Camera is seeing a normal image with varying brightness")
        
    # Check for actual content variation
    if frame.std() < 5:
        print("⚠️  Very low variation - camera might be seeing a blank surface")
    else:
        print(f"✅ Good image variation (std dev: {frame.std():.1f})")
else:
    print("❌ Failed to read from camera!")

cap.release()
print("\n💡 Tip: Point your webcam at something with clear edges/lines to test properly")
