#!/usr/bin/env python3
"""
Enhanced Webcam Viewer with Virtual Steering Wheel Animation
Shows camera feed with smooth curved lane detection and animated steering wheel
"""

import sys
import time
import cv2
import numpy as np
from pathlib import Path
from collections import deque

# Add openpilot to path
openpilot_path = Path.home() / "openpilot"
sys.path.insert(0, str(openpilot_path))

import cereal.messaging as messaging

class SteeringHistory:
    """Track steering history for smoothing"""
    def __init__(self, size=10):
        self.history = deque(maxlen=size)
    
    def add(self, value):
        self.history.append(value)
    
    def get_smooth(self):
        if not self.history:
            return 0.0
        return float(np.mean(self.history))

def fit_lane_curve(lines, height, width, is_left=True):
    """Fit a polynomial curve to lane lines"""
    if not lines:
        return None
    
    points = []
    for line in lines:
        x1, y1, x2, y2 = line
        y1 += height//2
        y2 += height//2
        points.extend([(x1, y1), (x2, y2)])
    
    if len(points) < 3:
        return None
    
    # Convert to numpy arrays
    points = np.array(points)
    x = points[:, 0]
    y = points[:, 1]
    
    # Fit polynomial (2nd degree for curves)
    try:
        z = np.polyfit(y, x, 2)
        return np.poly1d(z)
    except:
        return None

def draw_curved_lane(overlay, poly, height, width, color):
    """Draw smooth curved lane line"""
    if poly is None:
        return
    
    y_points = np.linspace(height//2, height-1, 50)
    points = []
    
    for y in y_points:
        x = poly(y)
        if 0 <= x < width:
            points.append([int(x), int(y)])
    
    if len(points) > 1:
        points = np.array(points, dtype=np.int32)
        cv2.polylines(overlay, [points], False, color, 5, cv2.LINE_AA)

def draw_steering_wheel(img, steer_angle, pwm_value):
    """Draw virtual steering wheel with motor position"""
    # Position in top-right corner
    center_x = img.shape[1] - 150
    center_y = 150
    radius = 100
    
    # Draw outer circle (steering wheel)
    cv2.circle(img, (center_x, center_y), radius, (200, 200, 200), 3)
    cv2.circle(img, (center_x, center_y), radius-10, (150, 150, 150), 1)
    
    # Draw center dot
    cv2.circle(img, (center_x, center_y), 5, (100, 100, 100), -1)
    
    # Calculate rotation angle (steer_angle is -1 to +1, convert to degrees)
    # Full lock is typically 450 degrees, so use 720 degrees range for visualization
    rotation_deg = steer_angle * 360  # -360 to +360 degrees
    rotation_rad = np.deg2rad(rotation_deg)
    
    # Draw steering indicator (like a spoke)
    spoke_length = radius - 15
    spoke_x = int(center_x + spoke_length * np.sin(rotation_rad))
    spoke_y = int(center_y - spoke_length * np.cos(rotation_rad))
    cv2.line(img, (center_x, center_y), (spoke_x, spoke_y), (0, 255, 255), 4)
    
    # Draw rotation marker on rim
    rim_x = int(center_x + radius * np.sin(rotation_rad))
    rim_y = int(center_y - radius * np.cos(rotation_rad))
    cv2.circle(img, (rim_x, rim_y), 8, (0, 165, 255), -1)
    
    # Color coding based on steering intensity
    if abs(pwm_value) > 100:
        color = (0, 0, 255)  # Red - strong steering
    elif abs(pwm_value) > 50:
        color = (0, 165, 255)  # Orange - moderate steering
    else:
        color = (0, 255, 0)  # Green - light steering
    
    cv2.circle(img, (rim_x, rim_y), 6, color, -1)
    
    # Draw angle text
    cv2.putText(img, f"{rotation_deg:.0f}°", 
                (center_x - 30, center_y + radius + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Draw PWM motor command
    cv2.putText(img, f"Motor: {pwm_value:+4d}", 
                (center_x - 55, center_y + radius + 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    # Direction arrows
    if pwm_value > 10:
        # Right arrow
        cv2.arrowedLine(img, (center_x + radius + 20, center_y), 
                       (center_x + radius + 60, center_y), 
                       (0, 165, 255), 3, tipLength=0.4)
    elif pwm_value < -10:
        # Left arrow
        cv2.arrowedLine(img, (center_x - radius - 20, center_y), 
                       (center_x - radius - 60, center_y), 
                       (0, 165, 255), 3, tipLength=0.4)

def detect_lanes_improved(frame):
    """Improved lane detection with better edge detection"""
    height, width = frame.shape[:2]
    
    # Region of interest (bottom 60%)
    roi = frame[int(height*0.4):, :]
    
    # Convert to HLS color space (better for lane detection)
    hls = cv2.cvtColor(roi, cv2.COLOR_BGR2HLS)
    
    # Extract L channel (lightness)
    l_channel = hls[:,:,1]
    
    # Apply CLAHE for better contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(l_channel)
    
    # Apply Gaussian blur
    blur = cv2.GaussianBlur(enhanced, (7, 7), 0)
    
    # Adaptive threshold for better line detection
    edges = cv2.Canny(blur, 30, 100)
    
    # Morphological operations to connect broken lines
    kernel = np.ones((3,3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    
    # Hough line detection with adjusted parameters
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 40, 
                           minLineLength=40, maxLineGap=200)
    
    return lines, edges

def draw_lanes_with_curves(frame, lines):
    """Draw curved lane lines with better visualization"""
    overlay = frame.copy()
    height, width = frame.shape[:2]
    
    if lines is not None:
        left_lines = []
        right_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # Calculate slope
            if x2 - x1 == 0:
                continue
            slope = (y2 - y1) / (x2 - x1)
            
            # Categorize as left or right lane
            if slope < -0.3:  # Left lane (negative slope) - relaxed threshold
                left_lines.append(line[0])
            elif slope > 0.3:  # Right lane (positive slope)
                right_lines.append(line[0])
        
        # Fit curves to lanes
        left_curve = fit_lane_curve(left_lines, height, width, is_left=True)
        right_curve = fit_lane_curve(right_lines, height, width, is_left=False)
        
        # Draw curved lanes
        draw_curved_lane(overlay, left_curve, height, width, (0, 255, 255))  # Yellow
        draw_curved_lane(overlay, right_curve, height, width, (0, 255, 255))  # Yellow
        
        # Calculate steering based on lane positions
        steer = 0.0
        if left_curve and right_curve:
            # Sample at bottom of image
            y_sample = height - 50
            left_x = left_curve(y_sample)
            right_x = right_curve(y_sample)
            
            lane_center = (left_x + right_x) / 2
            frame_center = width / 2
            
            deviation = (lane_center - frame_center) / (width / 2)
            steer = -deviation * 0.8  # Increased sensitivity
            
            # Draw center path (green)
            y_points = np.linspace(height//2, height-1, 30)
            center_points = []
            for y in y_points:
                try:
                    center_x = (left_curve(y) + right_curve(y)) / 2
                    if 0 <= center_x < width:
                        center_points.append([int(center_x), int(y)])
                except:
                    pass
            
            if len(center_points) > 1:
                center_points = np.array(center_points, dtype=np.int32)
                cv2.polylines(overlay, [center_points], False, (0, 255, 0), 4, cv2.LINE_AA)
        
        elif left_curve:
            # Only left lane visible - steer right
            steer = 0.3
        elif right_curve:
            # Only right lane visible - steer left
            steer = -0.3
        
        # Blend overlay with original frame
        result = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
        return result, steer
    
    return overlay, 0.0

def main():
    print("="*70)
    print("  🎮 ENHANCED STEERING WHEEL DEMO")
    print("="*70)
    print("\n  Features:")
    print("  • Smooth curved lane detection")
    print("  • Virtual steering wheel animation")
    print("  • Real-time motor PWM visualization")
    print("  • Color-coded steering intensity")
    print("\n  Yellow curves: Detected lanes")
    print("  Green curve: Predicted path")
    print("  Virtual wheel: Steering position")
    print("\n  Press 'q' to quit")
    print("="*70 + "\n")
    
    # Setup messaging for steering commands
    pm = messaging.PubMaster(['carControl'])
    
    # Steering history for smoothing
    steer_history = SteeringHistory(size=8)
    
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
    
    print("🎥 Starting enhanced view...")
    print("   (Window will open with virtual steering wheel)\n")
    
    frame_count = 0
    start_time = time.time()
    
    cv2.namedWindow('Openpilot - Virtual Steering Demo', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Openpilot - Virtual Steering Demo', 1280, 720)
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("⚠️  Failed to read frame")
                continue
            
            frame_count += 1
            
            # Detect and draw curved lanes
            lines, edges = detect_lanes_improved(frame)
            output, steer_raw = draw_lanes_with_curves(frame, lines)
            
            # Smooth steering
            steer_history.add(steer_raw)
            steer = steer_history.get_smooth()
            
            # Calculate PWM (capped at 200 for safety)
            pwm = int(np.clip(steer * 150, -200, 200))
            
            # Draw virtual steering wheel
            draw_steering_wheel(output, steer, pwm)
            
            # Add overlay info
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            
            # Status box (semi-transparent background)
            cv2.rectangle(output, (5, 5), (350, 200), (0, 0, 0), -1)
            cv2.rectangle(output, (5, 5), (350, 200), (255, 255, 255), 2)
            
            # Status text
            cv2.putText(output, f"FPS: {fps:.1f}", (15, 35), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(output, f"Frame: {frame_count}", (15, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Steering info with color coding
            steer_color = (0, 255, 255) if abs(steer) < 0.2 else (0, 165, 255)
            cv2.putText(output, f"Steer: {steer:+.3f}", (15, 105), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, steer_color, 2)
            
            pwm_color = (0, 255, 0) if abs(pwm) < 50 else (0, 165, 255) if abs(pwm) < 100 else (0, 0, 255)
            cv2.putText(output, f"PWM: {pwm:+4d}", (15, 140), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, pwm_color, 2)
            
            # Direction indicator
            if pwm > 15:
                direction = "TURN RIGHT >>"
                dir_color = (0, 165, 255)
            elif pwm < -15:
                direction = "<< TURN LEFT"
                dir_color = (0, 165, 255)
            else:
                direction = "STRAIGHT"
                dir_color = (0, 255, 0)
            
            cv2.putText(output, direction, (15, 175), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, dir_color, 2)
            
            # Publish steering command
            msg = messaging.new_message('carControl')
            msg.carControl.enabled = True
            msg.carControl.actuators.torque = float(steer)
            pm.send('carControl', msg)
            
            # Display
            cv2.imshow('Openpilot - Virtual Steering Demo', output)
            
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
