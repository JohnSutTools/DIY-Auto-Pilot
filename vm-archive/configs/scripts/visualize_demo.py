#!/usr/bin/env python3
"""
Visual Steering Demo - See It Work Without Hardware!

This standalone demo shows what the system will look like when connected
to openpilot. Runs a built-in animation showing realistic steering patterns.

Perfect for:
- Understanding the visualization before setup
- Demo without openpilot installed
- Quick visual test

No dependencies on openpilot or cereal!
"""

import sys
import time
import math

# Check and install pygame if needed
try:
    import pygame
except ImportError:
    print("Installing pygame...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame", "--user"])
    import pygame


class DemoVisualizer:
    """Self-contained demo visualization"""
    
    def __init__(self):
        pygame.init()
        
        # Window setup
        self.width = 1000
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Openpilot Steering Visualizer - DEMO MODE")
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (200, 200, 200)
        self.GREEN = (0, 200, 0)
        self.ORANGE = (255, 140, 0)
        self.RED = (220, 50, 50)
        self.BLUE = (50, 150, 255)
        self.DARK_GRAY = (40, 40, 40)
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Steering state
        self.steer_angle = 0.0  # Current steering angle in degrees
        self.target_steer = 0.0  # Target steering command (-1 to +1)
        self.pwm_value = 0  # PWM value (-255 to +255)
        
        # Configuration (matching config.yaml defaults)
        self.pwm_scale = 150
        self.pwm_cap = 255
        
        # History for graph
        self.history_length = 200
        self.steer_history = [0.0] * self.history_length
        
        # Demo scenario state
        self.demo_time = 0.0
        self.message_count = 0
        
        # Clock
        self.clock = pygame.time.Clock()
        self.fps = 60
        
    def update_demo_scenario(self, dt: float):
        """Generate realistic steering pattern"""
        self.demo_time += dt
        self.message_count += 1
        
        # Simulate various driving scenarios
        t = self.demo_time
        
        # Combine different patterns for realistic feel
        
        # Base lane keeping (gentle oscillation)
        lane_keeping = 0.15 * math.sin(t * 0.5)
        
        # Occasional corrections (sharper movements)
        if int(t * 2) % 7 == 0:
            correction = 0.4 * math.sin(t * 3)
        else:
            correction = 0.0
        
        # Curves (slower, sustained steering)
        curve_pattern = int(t / 5) % 3
        if curve_pattern == 1:
            curve = 0.3
        elif curve_pattern == 2:
            curve = -0.25
        else:
            curve = 0.0
        
        # Combine all patterns
        self.target_steer = lane_keeping + correction + curve
        
        # Clamp to valid range
        self.target_steer = max(-1.0, min(1.0, self.target_steer))
        
        # Convert to PWM (matching bridge logic)
        self.pwm_value = int(self.target_steer * self.pwm_scale)
        self.pwm_value = max(-self.pwm_cap, min(self.pwm_cap, self.pwm_value))
        
        # Update steering angle (simulate motor response)
        target_angle = self.target_steer * 540  # Max ±540 degrees (1.5 rotations)
        self.steer_angle += (target_angle - self.steer_angle) * 0.1  # Smooth motion
        
        # Update history
        self.steer_history.pop(0)
        self.steer_history.append(self.target_steer)
        
    def draw_steering_wheel(self):
        """Draw animated steering wheel"""
        center_x = 250
        center_y = 200
        radius = 120
        
        # Outer circle (wheel rim)
        pygame.draw.circle(self.screen, self.LIGHT_GRAY, (center_x, center_y), radius, 8)
        
        # Center hub
        pygame.draw.circle(self.screen, self.DARK_GRAY, (center_x, center_y), 30)
        
        # Spokes (rotate with wheel)
        angle_rad = math.radians(self.steer_angle)
        for i in range(4):
            spoke_angle = angle_rad + (i * math.pi / 2)
            end_x = center_x + int((radius - 10) * math.cos(spoke_angle))
            end_y = center_y + int((radius - 10) * math.sin(spoke_angle))
            pygame.draw.line(self.screen, self.GRAY, (center_x, center_y), 
                           (end_x, end_y), 4)
        
        # Top marker (red dot to show orientation)
        marker_angle = angle_rad - (math.pi / 2)  # Top of wheel
        marker_x = center_x + int((radius - 20) * math.cos(marker_angle))
        marker_y = center_y + int((radius - 20) * math.sin(marker_angle))
        pygame.draw.circle(self.screen, self.RED, (marker_x, marker_y), 8)
        
        # Angle text
        angle_text = self.font_medium.render(f"{self.steer_angle:.1f}°", True, self.WHITE)
        self.screen.blit(angle_text, (center_x - 50, center_y + radius + 30))
        
    def draw_pwm_bar(self):
        """Draw PWM command visualization"""
        bar_x = 550
        bar_y = 150
        bar_width = 400
        bar_height = 40
        
        # Background
        pygame.draw.rect(self.screen, self.DARK_GRAY, 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Center line
        center_x = bar_x + bar_width // 2
        pygame.draw.line(self.screen, self.WHITE, 
                        (center_x, bar_y), (center_x, bar_y + bar_height), 2)
        
        # PWM bar
        pwm_fraction = self.pwm_value / self.pwm_cap
        fill_width = int(abs(pwm_fraction) * (bar_width // 2))
        
        if self.pwm_value > 0:
            # Positive (clockwise) - fill right
            fill_rect = (center_x, bar_y, fill_width, bar_height)
            color = self.GREEN
            direction = "→ CLOCKWISE"
        elif self.pwm_value < 0:
            # Negative (counter-clockwise) - fill left
            fill_rect = (center_x - fill_width, bar_y, fill_width, bar_height)
            color = self.ORANGE
            direction = "← COUNTER-CW"
        else:
            fill_rect = None
            color = self.WHITE
            direction = "○ NEUTRAL"
        
        if fill_rect:
            pygame.draw.rect(self.screen, color, fill_rect)
        
        # Labels
        title = self.font_medium.render("Motor Command", True, self.WHITE)
        self.screen.blit(title, (bar_x, bar_y - 40))
        
        pwm_text = self.font_large.render(f"PWM: {self.pwm_value:+d}", True, color)
        self.screen.blit(pwm_text, (bar_x, bar_y + bar_height + 10))
        
        dir_text = self.font_small.render(direction, True, color)
        self.screen.blit(dir_text, (bar_x, bar_y + bar_height + 60))
        
    def draw_command_info(self):
        """Draw openpilot command info"""
        info_x = 550
        info_y = 350
        
        # Title
        title = self.font_medium.render("Openpilot Command", True, self.WHITE)
        self.screen.blit(title, (info_x, info_y))
        
        # Steer value (color coded)
        if self.target_steer > 0.05:
            color = self.GREEN
        elif self.target_steer < -0.05:
            color = self.ORANGE
        else:
            color = self.WHITE
        
        steer_text = self.font_large.render(f"Steer: {self.target_steer:+.3f}", True, color)
        self.screen.blit(steer_text, (info_x, info_y + 40))
        
        # Config info
        config_text = self.font_small.render(
            f"Scale: {self.pwm_scale}  |  Cap: {self.pwm_cap}", 
            True, self.GRAY
        )
        self.screen.blit(config_text, (info_x, info_y + 90))
        
    def draw_history_graph(self):
        """Draw steering command history graph"""
        graph_x = 50
        graph_y = 450
        graph_width = 900
        graph_height = 150
        
        # Background
        pygame.draw.rect(self.screen, self.DARK_GRAY, 
                        (graph_x, graph_y, graph_width, graph_height))
        
        # Center line
        center_y = graph_y + graph_height // 2
        pygame.draw.line(self.screen, self.GRAY, 
                        (graph_x, center_y), (graph_x + graph_width, center_y), 1)
        
        # Title
        title = self.font_medium.render("Steering History", True, self.WHITE)
        self.screen.blit(title, (graph_x, graph_y - 40))
        
        # Plot data
        if len(self.steer_history) > 1:
            points = []
            for i, value in enumerate(self.steer_history):
                x = graph_x + int((i / len(self.steer_history)) * graph_width)
                y = center_y - int(value * (graph_height // 2))
                points.append((x, y))
            
            pygame.draw.lines(self.screen, self.BLUE, False, points, 2)
        
        # Scale labels
        label_plus = self.font_small.render("+1.0", True, self.GRAY)
        label_zero = self.font_small.render("0.0", True, self.GRAY)
        label_minus = self.font_small.render("-1.0", True, self.GRAY)
        
        self.screen.blit(label_plus, (graph_x - 40, graph_y))
        self.screen.blit(label_zero, (graph_x - 40, center_y - 10))
        self.screen.blit(label_minus, (graph_x - 40, graph_y + graph_height - 20))
        
    def draw_status(self):
        """Draw status bar"""
        status_y = self.height - 40
        
        # Demo mode indicator
        demo_text = self.font_medium.render("DEMO MODE", True, self.ORANGE)
        self.screen.blit(demo_text, (20, 20))
        
        # Message count
        msg_text = self.font_small.render(f"Messages: {self.message_count}", True, self.GRAY)
        self.screen.blit(msg_text, (50, status_y))
        
        # Update rate
        rate = 20  # Demo runs at 20 Hz
        rate_text = self.font_small.render(f"Rate: {rate} Hz", True, self.GRAY)
        self.screen.blit(rate_text, (250, status_y))
        
        # Connection status
        status_circle = pygame.draw.circle(self.screen, self.GREEN, (450, status_y + 10), 8)
        status_text = self.font_small.render("DEMO ACTIVE", True, self.GREEN)
        self.screen.blit(status_text, (470, status_y))
        
        # Instructions
        help_text = self.font_small.render("Press Q or ESC to quit", True, self.GRAY)
        self.screen.blit(help_text, (self.width - 250, status_y))
        
    def run(self):
        """Main demo loop"""
        print("=" * 60)
        print("Steering Visualizer - DEMO MODE")
        print("=" * 60)
        print()
        print("Showing realistic steering patterns")
        print("Press Q or ESC to quit")
        print("=" * 60)
        
        running = True
        last_update = time.time()
        
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        running = False
            
            # Update demo (20 Hz)
            current_time = time.time()
            dt = current_time - last_update
            if dt >= 0.05:  # 20 Hz
                self.update_demo_scenario(dt)
                last_update = current_time
            
            # Draw everything
            self.screen.fill(self.BLACK)
            
            self.draw_steering_wheel()
            self.draw_pwm_bar()
            self.draw_command_info()
            self.draw_history_graph()
            self.draw_status()
            
            pygame.display.flip()
            self.clock.tick(self.fps)
        
        pygame.quit()
        print("\nDemo finished. Thanks for watching!")


def main():
    """Run the demo"""
    try:
        demo = DemoVisualizer()
        demo.run()
    except KeyboardInterrupt:
        print("\nDemo stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
