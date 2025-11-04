#!/usr/bin/env python3
"""
Simple Webcam Viewer with Lane Detection Visualization
Shows your camera feed with simulated lane lines
"""

import sys
import time
import cv2
import numpy as np
from pathlib import Path

# Add openpilot to path
openpilot_path = Path.home() / "openpilot"
sys.path.insert(0, str(openpilot_path))

import cereal.messaging as messaging

def detect_lanes_simple(frame):
    """Simple lane detection using edge detection"""
    height, width = frame.shape[:2]
    
    # Region of interest (bottom half)
    roi = frame[height//2:, :]
    
    # Convert to grayscale
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Edge detection
    edges = cv2.Canny(blur, 50, 150)
    
    # Hough line detection
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=150)
    
    return lines, edges

def draw_lanes(frame, lines):
    """Draw detected lane lines on frame"""
    overlay = frame.copy()
    height, width = frame.shape[:2]
    
    if lines is not None:
        left_lines = []
        right_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # Adjust y coordinates (they're relative to ROI)
            y1 += height//2
            y2 += height//2
            
            # Calculate slope
            if x2 - x1 == 0:
                continue
            slope = (y2 - y1) / (x2 - x1)
            
            # Categorize as left or right lane
            if slope < -0.5:  # Left lane (negative slope)
                left_lines.append(line[0])
            elif slope > 0.5:  # Right lane (positive slope)
                right_lines.append(line[0])
        
        # Draw left lane (yellow)
        for line in left_lines:
            x1, y1, x2, y2 = line
            y1 += height//2
            y2 += height//2
            cv2.line(overlay, (x1, y1), (x2, y2), (0, 255, 255), 3)
        
        # Draw right lane (yellow)
        for line in right_lines:
            x1, y1, x2, y2 = line
            y1 += height//2
            y2 += height//2
            cv2.line(overlay, (x1, y1), (x2, y2), (0, 255, 255), 3)
        
        # Calculate steering based on lane center
        if left_lines and right_lines:
            # Find average x position of lanes at bottom of image
            left_x = np.mean([line[0] for line in left_lines])
            right_x = np.mean([line[0] for line in right_lines])
            
            lane_center = (left_x + right_x) / 2
            frame_center = width / 2
            
            deviation = (lane_center - frame_center) / (width / 2)
            steer = -deviation * 0.5
            
            # Draw center path (green)
            path_x = int(lane_center)
            cv2.line(overlay, (path_x, height), (path_x, height//2), (0, 255, 0), 2)
            
            return overlay, steer
    
    return overlay, 0.0

def main():
    print("="*70)
    print("  🚗 WEBCAM LANE DETECTION VIEWER")
    print("="*70)
    print("\n  Real-time webcam feed with lane detection overlay")
    print("  Yellow lines: Detected lanes")
    print("  Green line: Predicted path")
    print("\n  Press 'q' to quit")
    print("="*70 + "\n")
    
    # Setup messaging for steering commands
    pm = messaging.PubMaster(['carControl'])
    
    # Open webcam
    print("📷 Opening webcam...")
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 20)
    
    if not cap.isOpened():
        print("❌ ERROR: Cannot open camera!")
        return
    
    print("✓ Camera opened")
    print("🔴 Camera light should be ON\n")
    
    # Warm up
    for _ in range(5):
        cap.read()
        time.sleep(0.1)
    
    print("🎥 Starting live view...")
    print("   (Window will open - press 'q' to quit)\n")
    
    frame_count = 0
    start_time = time.time()
    
    cv2.namedWindow('Openpilot Lane Detection', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Openpilot Lane Detection', 1280, 720)
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("⚠️  Failed to read frame")
                continue
            
            frame_count += 1
            
            # Detect and draw lanes
            lines, edges = detect_lanes_simple(frame)
            output, steer = draw_lanes(frame, lines)
            
            # Calculate PWM
            pwm = int(steer * 150)
            
            # Add overlay info
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            
            # Status text
            cv2.putText(output, f"FPS: {fps:.1f}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(output, f"Frame: {frame_count}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(output, f"Steer: {steer:+.3f}", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            cv2.putText(output, f"PWM: {pwm:+4d}", (10, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            
            # Direction arrow
            direction = "RIGHT" if pwm > 10 else "LEFT" if pwm < -10 else "STRAIGHT"
            color = (0, 255, 255) if direction == "STRAIGHT" else (0, 165, 255)
            cv2.putText(output, direction, (10, 190), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            # Publish steering command
            msg = messaging.new_message('carControl')
            msg.carControl.enabled = True
            msg.carControl.actuators.torque = float(steer)
            pm.send('carControl', msg)
            
            # Display
            cv2.imshow('Openpilot Lane Detection', output)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        
        avg_fps = frame_count / (time.time() - start_time)
        print("\n" + "="*70)
        print("  ✅ SESSION COMPLETE")
        print("="*70)
        print(f"\n  Total frames: {frame_count}")
        print(f"  Average FPS: {avg_fps:.1f}")
        print("="*70 + "\n")

if __name__ == '__main__':
    main()
