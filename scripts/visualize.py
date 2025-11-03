#!/usr/bin/env python3
"""
Visual Steering Simulator - See the system work without hardware!
Shows steering wheel, PWM commands, and openpilot data in real-time
"""

import sys
import time
import math
from typing import Optional

try:
    import pygame
except ImportError:
    print("Installing pygame for visualization...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
    import pygame

try:
    import cereal.messaging as messaging
except ImportError:
    print("ERROR: cereal not found. Run setup_system.sh first.")
    sys.exit(1)

import yaml


class SteeringVisualizer:
    """Visual representation of the steering system"""
    
    def __init__(self, config_path: str):
        # Load config
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.config.setdefault('pwm_scale', 150)
        self.config.setdefault('pwm_cap', 255)
        self.config.setdefault('stream_hz', 20)
        
        # Initialize pygame
        pygame.init()
        self.width = 1200
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Openpilot Steering Visualizer")
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (200, 200, 200)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 100, 255)
        self.YELLOW = (255, 255, 0)
        self.ORANGE = (255, 165, 0)
        
        # Font
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # State
        self.current_steer = 0.0
        self.current_pwm = 0
        self.steering_angle = 0.0
        self.message_count = 0
        self.last_update = time.time()
        
        # History for graph
        self.steer_history = []
        self.max_history = 200
        
        # Openpilot messaging
        self.sm = messaging.SubMaster(['carControl', 'controlsState'])
        
    def get_steer_command(self) -> Optional[float]:
        """Get steering command from openpilot"""
        self.sm.update(0)
        
        if self.sm.updated['carControl']:
            cc = self.sm['carControl']
            if hasattr(cc, 'actuators') and hasattr(cc.actuators, 'steer'):
                return float(cc.actuators.steer)
        
        if self.sm.updated['controlsState']:
            cs = self.sm['controlsState']
            if hasattr(cs, 'steer'):
                return float(cs.steer)
        
        return None
    
    def draw_steering_wheel(self):
        """Draw the steering wheel with current angle"""
        center_x = 300
        center_y = 300
        radius = 150
        
        # Wheel background
        pygame.draw.circle(self.screen, self.LIGHT_GRAY, (center_x, center_y), radius + 10)
        pygame.draw.circle(self.screen, self.BLACK, (center_x, center_y), radius, 3)
        
        # Calculate rotation (steering_angle is in degrees)
        angle_rad = math.radians(self.steering_angle)
        
        # Draw spokes
        for i in range(4):
            spoke_angle = angle_rad + (i * math.pi / 2)
            end_x = center_x + int(radius * math.cos(spoke_angle))
            end_y = center_y + int(radius * math.sin(spoke_angle))
            pygame.draw.line(self.screen, self.GRAY, (center_x, center_y), (end_x, end_y), 5)
        
        # Draw indicator at top (shows rotation)
        indicator_angle = angle_rad - math.pi/2  # Top position
        indicator_x = center_x + int((radius - 20) * math.cos(indicator_angle))
        indicator_y = center_y + int((radius - 20) * math.sin(indicator_angle))
        pygame.draw.circle(self.screen, self.RED, (indicator_x, indicator_y), 12)
        
        # Center hub
        pygame.draw.circle(self.screen, self.BLUE, (center_x, center_y), 30)
        
        # Label
        label = self.font_medium.render("Steering Wheel", True, self.WHITE)
        self.screen.blit(label, (center_x - 90, center_y + radius + 30))
        
        # Angle text
        angle_text = self.font_small.render(f"{self.steering_angle:.1f}°", True, self.WHITE)
        self.screen.blit(angle_text, (center_x - 30, center_y + radius + 60))
    
    def draw_motor_indicator(self):
        """Draw motor direction and PWM indicator"""
        x = 650
        y = 150
        
        # Title
        title = self.font_medium.render("Motor Command", True, self.WHITE)
        self.screen.blit(title, (x, y - 50))
        
        # PWM bar
        bar_width = 400
        bar_height = 50
        bar_x = x
        bar_y = y
        
        # Background
        pygame.draw.rect(self.screen, self.GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        # PWM value as percentage of cap
        pwm_percent = abs(self.current_pwm) / self.config['pwm_cap']
        fill_width = int(bar_width * pwm_percent)
        
        # Fill color based on direction
        fill_color = self.GREEN if self.current_pwm > 0 else self.ORANGE if self.current_pwm < 0 else self.GRAY
        
        if self.current_pwm > 0:
            # Right turn (clockwise)
            fill_x = bar_x + bar_width // 2
            pygame.draw.rect(self.screen, fill_color, (fill_x, bar_y, fill_width, bar_height))
        elif self.current_pwm < 0:
            # Left turn (counter-clockwise)
            fill_x = bar_x + bar_width // 2 - fill_width
            pygame.draw.rect(self.screen, fill_color, (fill_x, bar_y, fill_width, bar_height))
        
        # Center line
        pygame.draw.line(self.screen, self.WHITE, 
                        (bar_x + bar_width // 2, bar_y), 
                        (bar_x + bar_width // 2, bar_y + bar_height), 3)
        
        # Border
        pygame.draw.rect(self.screen, self.WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Labels
        left_label = self.font_small.render("LEFT", True, self.WHITE)
        right_label = self.font_small.render("RIGHT", True, self.WHITE)
        self.screen.blit(left_label, (bar_x, bar_y + bar_height + 10))
        self.screen.blit(right_label, (bar_x + bar_width - 60, bar_y + bar_height + 10))
        
        # PWM value
        pwm_text = self.font_large.render(f"PWM: {self.current_pwm:+4d}", True, self.WHITE)
        self.screen.blit(pwm_text, (x + 100, y + 80))
        
        # Direction text
        if self.current_pwm > 0:
            direction = "→ CLOCKWISE"
            color = self.GREEN
        elif self.current_pwm < 0:
            direction = "← COUNTER-CLOCKWISE"
            color = self.ORANGE
        else:
            direction = "● NEUTRAL"
            color = self.GRAY
        
        dir_text = self.font_medium.render(direction, True, color)
        self.screen.blit(dir_text, (x + 50, y + 130))
    
    def draw_steer_command(self):
        """Draw current steer command value"""
        x = 650
        y = 350
        
        # Title
        title = self.font_medium.render("Openpilot Command", True, self.WHITE)
        self.screen.blit(title, (x, y - 50))
        
        # Steer value with color
        steer_color = self.GREEN if self.current_steer > 0 else self.ORANGE if self.current_steer < 0 else self.WHITE
        steer_text = self.font_large.render(f"Steer: {self.current_steer:+.3f}", True, steer_color)
        self.screen.blit(steer_text, (x, y))
        
        # Scale info
        scale_text = self.font_small.render(f"Scale: {self.config['pwm_scale']}  Cap: {self.config['pwm_cap']}", True, self.GRAY)
        self.screen.blit(scale_text, (x, y + 60))
    
    def draw_history_graph(self):
        """Draw steering command history"""
        x = 50
        y = 500
        width = 1100
        height = 200
        
        # Title
        title = self.font_medium.render("Steering History", True, self.WHITE)
        self.screen.blit(title, (x, y - 40))
        
        # Background
        pygame.draw.rect(self.screen, (20, 20, 20), (x, y, width, height))
        pygame.draw.rect(self.screen, self.WHITE, (x, y, width, height), 2)
        
        # Center line
        center_y = y + height // 2
        pygame.draw.line(self.screen, self.GRAY, (x, center_y), (x + width, center_y), 1)
        
        # Draw history
        if len(self.steer_history) > 1:
            points = []
            for i, steer in enumerate(self.steer_history):
                px = x + int(i * width / self.max_history)
                py = center_y - int(steer * height / 2)
                points.append((px, py))
            
            if len(points) > 1:
                pygame.draw.lines(self.screen, self.BLUE, False, points, 2)
        
        # Labels
        max_label = self.font_small.render("+1.0", True, self.GRAY)
        min_label = self.font_small.render("-1.0", True, self.GRAY)
        zero_label = self.font_small.render("0.0", True, self.GRAY)
        self.screen.blit(max_label, (x - 45, y))
        self.screen.blit(min_label, (x - 45, y + height - 20))
        self.screen.blit(zero_label, (x - 45, center_y - 10))
    
    def draw_stats(self):
        """Draw statistics"""
        x = 50
        y = 50
        
        # Message count
        count_text = self.font_small.render(f"Messages: {self.message_count}", True, self.WHITE)
        self.screen.blit(count_text, (x, y))
        
        # Update rate
        rate_text = self.font_small.render(f"Rate: {self.config['stream_hz']} Hz", True, self.WHITE)
        self.screen.blit(rate_text, (x, y + 30))
        
        # Status
        status = "● RECEIVING" if self.message_count > 0 else "○ WAITING"
        status_color = self.GREEN if self.message_count > 0 else self.YELLOW
        status_text = self.font_small.render(status, True, status_color)
        self.screen.blit(status_text, (x, y + 60))
        
        # Instructions
        inst_text = self.font_small.render("Press Q to quit | Run replay in another terminal", True, self.GRAY)
        self.screen.blit(inst_text, (x, self.height - 40))
    
    def update(self):
        """Update steering position based on PWM"""
        # Simulate motor movement
        # PWM translates to angular velocity
        max_speed = 5.0  # degrees per frame at max PWM
        speed = (self.current_pwm / self.config['pwm_cap']) * max_speed
        
        self.steering_angle += speed
        
        # Limit steering angle (typical car: ±540 degrees, 1.5 turns)
        self.steering_angle = max(-540, min(540, self.steering_angle))
    
    def run(self):
        """Main visualization loop"""
        clock = pygame.time.Clock()
        running = True
        
        print("\n" + "="*60)
        print("Steering Visualizer Running")
        print("="*60)
        print("\nWaiting for openpilot messages...")
        print("\nIn another terminal, run:")
        print("  cd ~/openpilot")
        print("  tools/replay/replay '<route>|<segment>'")
        print("\nOr use test_simulation.sh")
        print("="*60 + "\n")
        
        loop_period = 1.0 / self.config['stream_hz']
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
            
            # Get steering command
            steer = self.get_steer_command()
            
            if steer is not None:
                self.current_steer = steer
                self.current_pwm = int(steer * self.config['pwm_scale'])
                self.current_pwm = max(-self.config['pwm_cap'], 
                                      min(self.config['pwm_cap'], self.current_pwm))
                self.message_count += 1
                
                # Add to history
                self.steer_history.append(steer)
                if len(self.steer_history) > self.max_history:
                    self.steer_history.pop(0)
            
            # Update steering position
            self.update()
            
            # Draw everything
            self.screen.fill(self.BLACK)
            self.draw_steering_wheel()
            self.draw_motor_indicator()
            self.draw_steer_command()
            self.draw_history_graph()
            self.draw_stats()
            
            pygame.display.flip()
            clock.tick(self.config['stream_hz'])
        
        pygame.quit()
        print(f"\nVisualization stopped. Total messages: {self.message_count}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Visual steering simulator - see the system work!'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='bridge/config.yaml',
        help='Configuration file'
    )
    
    args = parser.parse_args()
    
    try:
        visualizer = SteeringVisualizer(args.config)
        visualizer.run()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
