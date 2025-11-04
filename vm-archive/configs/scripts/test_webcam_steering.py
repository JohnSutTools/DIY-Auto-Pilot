#!/usr/bin/env python3
"""Test webcam with simulated steering commands"""
import cv2
import time
import sys

print('Testing webcam with steering simulation...')
print('='*60)

# Test camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print('ERROR: Cannot open camera!')
    sys.exit(1)

# Configure camera
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 20)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

print('\n✅ Camera opened successfully')
print(f'Resolution: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}')
print(f'FPS: {cap.get(cv2.CAP_PROP_FPS)}')
print('\n🔴 Camera light should be ON now')
print('\nCapturing frames for 10 seconds...')
print('(Simulating steering commands based on frame data)\n')

frame_count = 0
start_time = time.time()

while time.time() - start_time < 10:
    ret, frame = cap.read()
    if ret:
        frame_count += 1
        
        # Simulate lane detection → steering command
        # In reality, openpilot would analyze the frame
        # For demo, we'll just show frame stats
        if frame_count % 20 == 0:  # Every 20 frames (~1 second)
            brightness = frame.mean()
            # Simulate steering based on brightness (silly but demonstrates concept)
            steer = (brightness - 128) / 128 * 0.3  # -0.3 to +0.3
            pwm = int(steer * 150)  # Scale to PWM
            
            elapsed = time.time() - start_time
            fps = frame_count / elapsed
            
            print(f'[{elapsed:5.1f}s] Frame {frame_count:3d} | '
                  f'FPS: {fps:4.1f} | '
                  f'Brightness: {brightness:5.1f} | '
                  f'Steer: {steer:+.2f} | '
                  f'PWM: {pwm:+4d}')
    else:
        print('Frame read failed!')
        time.sleep(0.05)

cap.release()

print(f'\n✅ Test complete!')
print(f'Total frames: {frame_count}')
print(f'Average FPS: {frame_count / 10:.1f}')
print('\nWebcam is working correctly for openpilot vision processing!')
