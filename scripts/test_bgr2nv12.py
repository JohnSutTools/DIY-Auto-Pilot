#!/usr/bin/env python3
import cv2
import av

# Test the exact conversion camerad does
device = "/dev/video0"
print(f"Opening {device}...")
cap = cv2.VideoCapture(device)

if not cap.isOpened():
    print("❌ Failed to open camera")
    exit(1)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280.0)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720.0)

print("Reading one frame...")
ret, frame = cap.read()
if not ret:
    print("❌ Failed to read frame")
    exit(1)

print(f"✅ Frame read: {frame.shape}")

# Try bgr2nv12 conversion like camerad does
print("\nTrying bgr2nv12 conversion...")
try:
    av_frame = av.VideoFrame.from_ndarray(frame, format='bgr24')
    print(f"✅ Created av.VideoFrame: {av_frame.width}x{av_frame.height}")
    
    nv12_frame = av_frame.reformat(format='nv12')
    print(f"✅ Converted to nv12: {nv12_frame.width}x{nv12_frame.height}")
    
    nv12_data = nv12_frame.to_ndarray()
    print(f"✅ Got ndarray: {nv12_data.shape}")
    
    yuv_bytes = nv12_data.data.tobytes()
    print(f"✅ Got bytes: {len(yuv_bytes)} bytes")
    
    print("\n✓ bgr2nv12 conversion works!")
except Exception as e:
    print(f"❌ Conversion failed: {e}")
    import traceback
    traceback.print_exc()

cap.release()
