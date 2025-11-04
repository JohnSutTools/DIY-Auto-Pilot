#!/usr/bin/env python3
"""Test real webcam capture with multiple backends"""
import cv2
import sys

print("Testing webcam with different configurations...")
print("="*60)

# Try different backends and settings
configs = [
    ("V4L2 + MJPEG", cv2.CAP_V4L2, 0, "MJPG", 640, 480),
    ("V4L2 + YUYV", cv2.CAP_V4L2, 0, "YUYV", 640, 480),
    ("Default backend", None, 0, "MJPG", 640, 480),
    ("Video1 device", cv2.CAP_V4L2, 1, "MJPG", 640, 480),
]

for name, backend, device, fourcc, width, height in configs:
    print(f"\n{name}:")
    print(f"  Device: /dev/video{device}")
    
    try:
        if backend:
            cap = cv2.VideoCapture(device, backend)
        else:
            cap = cv2.VideoCapture(device)
        
        if not cap.isOpened():
            print("  ❌ Failed to open")
            continue
        
        # Set format
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fourcc))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        print(f"  ✓ Opened camera")
        print(f"    Resolution: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
        
        # Try to read a frame
        print(f"    Reading frame...", end=" ")
        ret, frame = cap.read()
        
        if ret:
            print(f"✅ SUCCESS!")
            print(f"    Frame shape: {frame.shape}")
            print(f"    Frame type: {frame.dtype}")
            print(f"\n🎉 THIS CONFIG WORKS! Use this in your code.")
            cap.release()
            sys.exit(0)
        else:
            print(f"❌ Failed to read frame")
        
        cap.release()
        
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "="*60)
print("❌ None of the configurations worked")
print("\nTroubleshooting:")
print("1. Check camera permissions: ls -la /dev/video*")
print("2. Verify camera is attached: usbipd list")
print("3. Try detaching and reattaching: usbipd detach --busid <ID>")
print("4. Check kernel messages: sudo dmesg | tail -20")
