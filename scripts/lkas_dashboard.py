#!/usr/bin/env python3
"""
LKAS Dashboard - Real-time visual display of lane detection status
Shows what openpilot is seeing without needing camera access
"""

import cereal.messaging as messaging
import time
import math
import os
import sys

class LKASDashboard:
    def __init__(self):
        self.sm = messaging.SubMaster(['modelV2'])
        
    def draw_ascii_steering(self, steer_deg):
        """Draw ASCII art steering wheel"""
        width = 40
        center = width // 2
        
        # Map steering angle to position (-30° to +30° range)
        max_angle = 30
        steer_clamped = max(-max_angle, min(max_angle, steer_deg))
        pos = int(center + (steer_clamped / max_angle) * (width // 2 - 5))
        
        # Create bar
        bar = [' '] * width
        bar[center] = '|'  # Center mark
        
        # Steering indicator
        if abs(steer_deg) < 1:
            bar[pos] = '◆'  # Straight
        elif steer_deg < 0:
            bar[pos] = '◀'  # Left
        else:
            bar[pos] = '▶'  # Right
        
        return ''.join(bar)
    
    def draw_lane_view(self, modelV2):
        """Draw ASCII representation of lane detection"""
        width = 60
        height = 15
        
        # Create canvas
        canvas = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Draw horizon
        horizon = height // 3
        for x in range(width):
            canvas[horizon][x] = '·'
        
        # Draw lanes if available
        try:
            lane_lines = modelV2.laneLines
            lane_probs = modelV2.laneLineProbs
            
            for i, (line, prob) in enumerate(zip(lane_lines, lane_probs)):
                if prob > 0.3:
                    # Sample a few points
                    for j in range(0, min(len(line.y), 10), 2):
                        y_meters = line.y[j]
                        x_meters = line.x[j]
                        
                        if x_meters > 0.1:
                            # Convert to screen coordinates
                            screen_x = int(width // 2 + (y_meters * 8))
                            screen_y = int(height - 1 - (x_meters * 0.3))
                            
                            if 0 <= screen_x < width and 0 <= screen_y < height:
                                canvas[screen_y][screen_x] = '║'
            
            # Draw path
            position = modelV2.position
            for j in range(0, min(len(position.y), 10), 2):
                y_meters = position.y[j]
                x_meters = position.x[j]
                
                if x_meters > 0.1:
                    screen_x = int(width // 2 + (y_meters * 8))
                    screen_y = int(height - 1 - (x_meters * 0.3))
                    
                    if 0 <= screen_x < width and 0 <= screen_y < height:
                        canvas[screen_y][screen_x] = '●'
        except:
            pass
        
        # Draw car at bottom center
        car_x = width // 2
        canvas[-1][car_x-1:car_x+2] = ['╔', '▲', '╗']
        
        # Convert to string
        return '\n'.join([''.join(row) for row in canvas])
    
    def run(self):
        """Main dashboard loop"""
        print("\n" + "="*70)
        print("  🎮 OPENPILOT LKAS DASHBOARD - LIVE STATUS")
        print("="*70)
        print("\n  Press Ctrl+C to exit\n")
        
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                self.sm.update(100)
                
                if self.sm.updated['modelV2']:
                    frame_count += 1
                    modelV2 = self.sm['modelV2']
                    
                    # Clear screen (works on most terminals)
                    os.system('clear' if os.name == 'posix' else 'cls')
                    
                    # Calculate steering
                    position = modelV2.position
                    steer_deg = 0
                    if len(position.x) > 15 and position.x[15] > 0:
                        steer_rad = math.atan2(position.y[15], position.x[15])
                        steer_deg = math.degrees(steer_rad)
                    
                    # Count lanes
                    num_lanes = sum(1 for prob in modelV2.laneLineProbs if prob > 0.3)
                    
                    # Calculate FPS
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    
                    # Draw dashboard
                    print("\n" + "="*70)
                    print("  🚗 OPENPILOT LKAS - LIVE DETECTION")
                    print("="*70)
                    print()
                    
                    # Lane view
                    print(self.draw_lane_view(modelV2))
                    print()
                    
                    # Steering display
                    direction = "⬅️  LEFT" if steer_deg < -2 else "➡️  RIGHT" if steer_deg > 2 else "⬆️  STRAIGHT"
                    print(f"  Steering: {steer_deg:+6.1f}°  {direction}")
                    print(f"  {self.draw_ascii_steering(steer_deg)}")
                    print()
                    
                    # Stats
                    print(f"  Lane Lines: {num_lanes}/4  │  FPS: {fps:.1f}  │  Frames: {frame_count}")
                    print()
                    print("  Point camera at road to see lane detection change!")
                    print("  Press Ctrl+C to exit")
                    print("="*70)
                    
                else:
                    # No data yet
                    if frame_count == 0:
                        print("\r  ⏳ Waiting for openpilot data...", end='', flush=True)
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\n  ✅ Dashboard closed\n")

def main():
    dashboard = LKASDashboard()
    dashboard.run()

if __name__ == '__main__':
    main()
