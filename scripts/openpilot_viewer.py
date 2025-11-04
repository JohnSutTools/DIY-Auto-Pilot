#!/usr/bin/env python3
"""
Openpilot Lane Detection Viewer
Displays webcam feed with lane overlays from openpilot modelV2 output
"""

import cv2
import numpy as np
import cereal.messaging as messaging
import time
import math

class OpenpilotViewer:
    def __init__(self):
        """Initialize viewer with cereal subscribers"""
        # Subscribe to both model output and camera frames
        self.sm = messaging.SubMaster(['modelV2', 'roadCameraState', 'roadEncodeIdx'])
        
        # Display settings (720p)
        self.width = 1280
        self.height = 720
        self.display_width = 1280
        self.display_height = 720
        
        # Camera frame
        self.last_camera_frame = None
        
        # Colors (BGR format for OpenCV)
        self.lane_color = (0, 255, 255)      # Yellow for lanes
        self.path_color = (0, 255, 0)        # Green for path
        self.text_color = (255, 255, 255)    # White for text
        self.bg_color = (0, 0, 0)            # Black background
        
        # Stats
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.fps = 0.0
        
        print("\n" + "="*70)
        print("  🎥 OPENPILOT LANE DETECTION VIEWER")
        print("="*70)
        print("\n  Waiting for openpilot vision data...")
        print("  Make sure camerad and modeld are running!")
        print("\n  Controls:")
        print("    Q or ESC - Quit")
        print("    Space - Pause/Resume")
        print("\n" + "="*70 + "\n")
    
    def model_to_image_coords(self, x, y, z=0):
        """Convert model coordinates (meters) to image pixel coordinates
        Model uses road plane coordinates, we need to project to camera image.
        x = forward distance, y = lateral offset, z = height
        """
        # Camera calibration approximation for forward-facing dashcam
        # These values work reasonably for typical dashcam mounting
        focal_length = 910  # pixels (approximate for 720p)
        camera_height = 1.22  # meters (typical car camera height)
        
        # Simple perspective projection
        if x > 0.1:  # Avoid division by zero
            # Project onto image plane
            # Lateral position
            pixel_x = int(self.display_width / 2 + (y * focal_length) / x)
            # Vertical position (road surface to image)
            pixel_y = int(self.display_height / 2 + (focal_length * (z - camera_height)) / x + self.display_height * 0.1)
            
            return (pixel_x, pixel_y)
        else:
            return (self.display_width // 2, self.display_height)  # Bottom center for close points
    
    def draw_lane_line(self, frame, points, color, thickness=3):
        """Draw a lane line from model points"""
        if len(points) < 2:
            return
        
        # Convert model points to image coordinates
        image_points = []
        for x, y in points:
            px, py = self.model_to_image_coords(x, y)
            # Only draw points that are visible in the frame
            if 0 <= px < self.display_width and 0 <= py < self.display_height:
                image_points.append((px, py))
        
        # Draw line segments
        if len(image_points) >= 2:
            for i in range(len(image_points) - 1):
                cv2.line(frame, image_points[i], image_points[i+1], color, thickness)
    
    def draw_path(self, frame, points):
        """Draw the planned path"""
        if len(points) < 2:
            return
        
        # Convert and draw path
        image_points = []
        for x, y in points:
            px, py = self.model_to_image_coords(x, y)
            if 0 <= px < self.display_width and 0 <= py < self.display_height:
                image_points.append((px, py))
        
        # Draw thicker path line
        if len(image_points) >= 2:
            for i in range(len(image_points) - 1):
                cv2.line(frame, image_points[i], image_points[i+1], self.path_color, 5)
    
    def draw_overlay(self, frame, modelV2):
        """Draw lane lines and path on frame"""
        try:
            # Get lane lines
            lane_lines = modelV2.laneLines
            lane_line_probs = modelV2.laneLineProbs
            
            # Draw each lane line (left to right)
            for i, (line, prob) in enumerate(zip(lane_lines, lane_line_probs)):
                if prob > 0.3:  # Only draw if confident
                    # Extract points
                    points = []
                    for j in range(len(line.x)):
                        x = line.x[j]  # Forward distance
                        y = line.y[j]  # Lateral offset
                        points.append((x, y))
                    
                    # Draw lane line
                    self.draw_lane_line(frame, points, self.lane_color)
            
            # Draw the planned path (center of lane)
            position = modelV2.position
            path_points = []
            for j in range(len(position.x)):
                x = position.x[j]
                y = position.y[j]
                path_points.append((x, y))
            
            self.draw_path(frame, path_points)
            
            # Calculate steering angle from path
            if len(path_points) >= 10:
                # Use point ~10m ahead (index around 10-15)
                lookahead_idx = min(15, len(path_points) - 1)
                x_ahead = position.x[lookahead_idx]
                y_ahead = position.y[lookahead_idx]
                
                if x_ahead > 0:
                    steer_rad = math.atan2(y_ahead, x_ahead)
                    steer_deg = math.degrees(steer_rad)
                    
                    # Draw steering indicator
                    direction = "LEFT" if steer_deg < -1 else "RIGHT" if steer_deg > 1 else "STRAIGHT"
                    steer_text = f"Steer: {steer_deg:+.1f}° {direction}"
                    cv2.putText(frame, steer_text, (20, 80), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.0, self.text_color, 2)
            
            # Count confident lane lines
            num_lanes = sum(1 for prob in lane_line_probs if prob > 0.3)
            lane_text = f"Lanes detected: {num_lanes}"
            cv2.putText(frame, lane_text, (20, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.text_color, 2)
            
        except Exception as e:
            cv2.putText(frame, f"Error: {str(e)[:50]}", (20, 160),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
    
    def get_camera_frame(self):
        """Get the latest camera frame from openpilot"""
        # Try to read from shared memory or messaging
        # For now, capture directly from webcam as fallback
        if not hasattr(self, 'cap'):
            # Initialize webcam capture
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None
    
    def run(self):
        """Main viewer loop"""
        cv2.namedWindow('Openpilot Lane Detection', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Openpilot Lane Detection', self.display_width, self.display_height)
        
        paused = False
        last_frame = None
        
        while True:
            # Update subscribers
            self.sm.update(100)  # 100ms timeout
            
            if not paused:
                # Get camera frame
                frame = self.get_camera_frame()
                
                if frame is None:
                    # No camera - create blank frame
                    frame = np.zeros((self.display_height, self.display_width, 3), dtype=np.uint8)
                    cv2.putText(frame, "No camera feed", 
                               (self.display_width // 2 - 150, self.display_height // 2),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
                else:
                    # Resize if needed
                    if frame.shape[1] != self.display_width or frame.shape[0] != self.display_height:
                        frame = cv2.resize(frame, (self.display_width, self.display_height))
                
                # Draw lane overlays if we have model data
                if self.sm.updated['modelV2']:
                    modelV2 = self.sm['modelV2']
                    self.draw_overlay(frame, modelV2)
                    self.frame_count += 1
                
                last_frame = frame.copy()
            else:
                # Paused - show last frame
                if last_frame is not None:
                    frame = last_frame.copy()
                    cv2.putText(frame, "PAUSED", (self.display_width // 2 - 100, 50),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 165, 255), 3)
                else:
                    frame = np.zeros((self.display_height, self.display_width, 3), dtype=np.uint8)
            
            # Calculate FPS
            current_time = time.time()
            if current_time - self.last_fps_time >= 1.0:
                self.fps = self.frame_count / (current_time - self.last_fps_time)
                self.frame_count = 0
                self.last_fps_time = current_time
            
            # Draw status
            cv2.putText(frame, f"FPS: {self.fps:.1f}", (20, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, self.text_color, 2)
            
            # Show frame
            cv2.imshow('Openpilot Lane Detection', frame)
            
            # Handle keyboard input
            key = cv2.waitKey(30) & 0xFF
            if key == ord('q') or key == 27:  # Q or ESC
                break
            elif key == ord(' '):  # Space
                paused = not paused
                print(f"{'Paused' if paused else 'Resumed'}")
        
        # Cleanup
        if hasattr(self, 'cap'):
            self.cap.release()
        cv2.destroyAllWindows()
        print("\n✅ Viewer closed\n")

def main():
    viewer = OpenpilotViewer()
    viewer.run()

if __name__ == '__main__':
    main()
