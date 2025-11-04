#!/usr/bin/env python3
"""
Standalone LKAS Viewer with VisionIPC
Shows webcam feed with openpilot lane detection overlay
Reads camera frames from openpilot's shared memory (VisionIPC)
"""

import cv2
import numpy as np
import cereal.messaging as messaging
from cereal.visionipc import VisionIpcClient, VisionStreamType
import time
import math

class LKASViewer:
    def __init__(self):
        """Initialize viewer with cereal subscribers"""
        # Subscribe to openpilot model output
        self.sm = messaging.SubMaster(['modelV2'])
        
        # Display settings (720p)
        self.display_width = 1280
        self.display_height = 720
        
        # Colors (BGR format for OpenCV)
        self.lane_color = (0, 255, 255)      # Yellow for lanes
        self.path_color = (0, 255, 0)        # Green for path
        self.text_color = (255, 255, 255)    # White for text
        
        # Stats
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.fps = 0.0
        
        # Connect to camerad's output via OpenCV
        # Note: We'll read the display frames, not interfere with camerad
        print("\n" + "="*70)
        print("  🎥 OPENPILOT LKAS VIEWER - STANDALONE MODE")
        print("="*70)
        print("\n  This viewer shows webcam + openpilot lane detection")
        print("  Make sure camerad and modeld are running separately!")
        print("\n  Controls:")
        print("    Q or ESC - Quit")
        print("    Space - Pause/Resume")
        print("\n" + "="*70 + "\n")
    
    def model_to_image_coords(self, x, y):
        """Convert model coordinates (meters) to image pixel coordinates"""
        # Camera calibration for typical dashcam at 720p
        focal_length = 910  # pixels
        camera_height = 1.22  # meters
        
        if x > 0.1:  # Avoid division by zero
            # Perspective projection
            pixel_x = int(self.display_width / 2 + (y * focal_length) / x)
            pixel_y = int(self.display_height / 2 + (focal_length * (-camera_height)) / x + self.display_height * 0.15)
            
            # Clamp to image bounds
            pixel_x = max(0, min(pixel_x, self.display_width - 1))
            pixel_y = max(0, min(pixel_y, self.display_height - 1))
            
            return (pixel_x, pixel_y)
        else:
            return (self.display_width // 2, self.display_height - 1)
    
    def draw_lane_line(self, frame, points, color, thickness=4):
        """Draw a lane line from model points"""
        if len(points) < 2:
            return
        
        # Convert model points to image coordinates
        image_points = []
        for x, y in points:
            px, py = self.model_to_image_coords(x, y)
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
            image_points.append((px, py))
        
        # Draw thicker path line with semi-transparency effect
        if len(image_points) >= 2:
            overlay = frame.copy()
            for i in range(len(image_points) - 1):
                cv2.line(overlay, image_points[i], image_points[i+1], self.path_color, 6)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    def draw_overlay(self, frame, modelV2):
        """Draw lane lines and path on frame"""
        try:
            # Get lane lines
            lane_lines = modelV2.laneLines
            lane_line_probs = modelV2.laneLineProbs
            
            # Draw each confident lane line
            for i, (line, prob) in enumerate(zip(lane_lines, lane_line_probs)):
                if prob > 0.3:  # Only draw if confident
                    points = [(line.x[j], line.y[j]) for j in range(len(line.x))]
                    self.draw_lane_line(frame, points, self.lane_color, thickness=3)
            
            # Draw the planned path
            position = modelV2.position
            path_points = [(position.x[j], position.y[j]) for j in range(len(position.x))]
            self.draw_path(frame, path_points)
            
            # Calculate and display steering
            if len(path_points) >= 10:
                lookahead_idx = min(15, len(path_points) - 1)
                x_ahead = position.x[lookahead_idx]
                y_ahead = position.y[lookahead_idx]
                
                if x_ahead > 0:
                    steer_rad = math.atan2(y_ahead, x_ahead)
                    steer_deg = math.degrees(steer_rad)
                    
                    direction = "⬅️ LEFT" if steer_deg < -2 else "➡️ RIGHT" if steer_deg > 2 else "⬆️ STRAIGHT"
                    
                    # Draw steering info with background
                    cv2.rectangle(frame, (10, 50), (400, 160), (0, 0, 0), -1)
                    cv2.rectangle(frame, (10, 50), (400, 160), self.text_color, 2)
                    
                    cv2.putText(frame, f"Steering: {steer_deg:+.1f}°", (20, 85), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.9, self.text_color, 2)
                    cv2.putText(frame, direction, (20, 125), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
            
            # Count confident lane lines
            num_lanes = sum(1 for prob in lane_line_probs if prob > 0.3)
            
            # Draw status info
            cv2.rectangle(frame, (10, 170), (280, 240), (0, 0, 0), -1)
            cv2.rectangle(frame, (10, 170), (280, 240), self.text_color, 2)
            cv2.putText(frame, f"Lanes: {num_lanes}", (20, 205), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, f"FPS: {self.fps:.1f}", (20, 230), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.text_color, 2)
            
        except Exception as e:
            cv2.putText(frame, f"Error: {str(e)[:40]}", (20, 270),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    
    def run(self, video_source=0):
        """Main viewer loop - reads from openpilot's shared memory via VisionIPC"""
        # Connect to openpilot's camera stream via VisionIPC
        # This is how the official UI does it - reads from shared memory
        print("Connecting to openpilot camera stream...")
        vipc_client = VisionIpcClient("camerad", VisionStreamType.VISION_STREAM_ROAD, True)
        
        if not vipc_client.connect(False):
            print("❌ Could not connect to VisionIPC")
            print("   Make sure camerad is running!")
            return
        
        print(f"✓ Connected to VisionIPC")
        print(f"✓ Camera: {vipc_client.width}x{vipc_client.height}")
        print("✓ Waiting for frames...\n")
        
        cv2.namedWindow('Openpilot LKAS', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Openpilot LKAS', self.display_width, self.display_height)
        
        paused = False
        last_frame = None
        
        while True:
            # Update model data
            self.sm.update(10)  # 10ms timeout
            
            if not paused:
                # Read camera frame from VisionIPC (shared memory)
                yuv_img = vipc_client.recv()
                
                if yuv_img is not None:
                    # Convert YUV to RGB
                    # Openpilot uses YUV (NV12) format
                    yuv_data = np.frombuffer(yuv_img.data, dtype=np.uint8).reshape((len(yuv_img.data) // vipc_client.stride, vipc_client.stride))
                    frame = cv2.cvtColor(yuv_data[:vipc_client.height * 3 // 2, :vipc_client.width], cv2.COLOR_YUV2RGB_NV12)
                    
                    # Resize to display size if needed
                    if frame.shape[1] != self.display_width or frame.shape[0] != self.display_height:
                        frame = cv2.resize(frame, (self.display_width, self.display_height))
                    
                    # Draw overlays if we have model data
                    if self.sm.updated['modelV2']:
                        modelV2 = self.sm['modelV2']
                        self.draw_overlay(frame, modelV2)
                        self.frame_count += 1
                    else:
                        # No model data yet
                        cv2.putText(frame, "Waiting for model data...", 
                                   (self.display_width // 2 - 180, 30),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
                    
                    last_frame = frame.copy()
                else:
                    frame = last_frame if last_frame is not None else np.zeros((self.display_height, self.display_width, 3), dtype=np.uint8)
            else:
                # Paused
                frame = last_frame if last_frame is not None else np.zeros((self.display_height, self.display_width, 3), dtype=np.uint8)
                cv2.putText(frame, "PAUSED", (self.display_width // 2 - 100, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 165, 255), 3)
            
            # Calculate FPS
            current_time = time.time()
            if current_time - self.last_fps_time >= 1.0:
                self.fps = self.frame_count / (current_time - self.last_fps_time)
                self.frame_count = 0
                self.last_fps_time = current_time
            
            # Show frame
            cv2.imshow('Openpilot LKAS', frame)
            
            # Handle keyboard
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
            elif key == ord(' '):
                paused = not paused
                print(f"{'⏸️  Paused' if paused else '▶️  Resumed'}")
        
        # Cleanup
        cv2.destroyAllWindows()
        print("\n✅ Viewer closed\n")

def main():
    viewer = LKASViewer()
    viewer.run()

if __name__ == '__main__':
    main()
