#!/usr/bin/env python3
"""
Openpilot LKAS Bridge - Real Implementation
Connects openpilot's vision system to ESP32 steering actuator

Flow: Webcam -> camerad -> modeld -> lateralPlan -> Serial Bridge -> ESP32
"""

import sys
import time
from pathlib import Path

# Add openpilot to path
openpilot_path = Path.home() / "openpilot"
sys.path.insert(0, str(openpilot_path))

import cereal.messaging as messaging
import serial
import yaml

class OpenpilotSteeringBridge:
    def __init__(self, config_path, serial_port='/dev/ttyUSB0', baud_rate=115200):
        """Initialize bridge between openpilot and ESP32"""
        
        # Load configuration
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.pwm_scale = self.config.get('pwm_scale', 150)
        self.pwm_cap = self.config.get('pwm_cap', 200)
        
        # Setup serial connection to ESP32
        try:
            self.ser = serial.Serial(serial_port, baud_rate, timeout=0.1)
            print(f"✓ Connected to ESP32 on {serial_port}")
        except Exception as e:
            print(f"⚠️  Serial port not available: {e}")
            print("   Running in SIMULATION mode (no hardware)")
            self.ser = None
        
        # Subscribe to openpilot messages
        # carControl contains the actuator commands
        # controlsState contains the steering state
        # modelV2 contains the vision model output
        # drivingModelData contains additional model info
        self.sm = messaging.SubMaster(['carControl', 'controlsState', 'modelV2'])
        
        print("✓ Subscribed to openpilot messages")
        
        self.frame_count = 0
        self.start_time = time.time()
        
    def steering_to_pwm(self, steer_angle):
        """Convert steering angle to PWM value"""
        # steer_angle is in radians, typically -0.5 to +0.5 for realistic steering
        # Convert to degrees for easier understanding
        steer_deg = steer_angle * 57.3  # rad to deg
        
        # Scale to PWM (-pwm_cap to +pwm_cap)
        pwm_value = int(steer_angle * self.pwm_scale)
        pwm_value = max(-self.pwm_cap, min(self.pwm_cap, pwm_value))
        
        return pwm_value, steer_deg
    
    def send_to_esp32(self, pwm_value):
        """Send PWM command to ESP32"""
        if self.ser and self.ser.is_open:
            try:
                command = f"S:{pwm_value:+d}\n"
                self.ser.write(command.encode())
                
                # Read response if available
                if self.ser.in_waiting:
                    response = self.ser.readline().decode().strip()
                    if response:
                        return response
            except Exception as e:
                print(f"Serial error: {e}")
                return None
        return None
    
    def run(self):
        """Main loop - read openpilot steering and send to ESP32"""
        
        print("\n" + "="*70)
        print("  🚗 OPENPILOT LKAS BRIDGE - ACTIVE")
        print("="*70)
        print("\n  Waiting for openpilot vision system...")
        print("  Make sure camerad.py and modeld.py are running!")
        print("\n  Press Ctrl+C to stop")
        print("="*70 + "\n")
        
        last_steer = 0.0
        last_pwm = 0
        no_data_count = 0
        
        try:
            while True:
                # Update messages (non-blocking)
                self.sm.update(100)  # 100ms timeout
                
                self.frame_count += 1
                
                # Primary: modelV2 - get steering directly from lane model output
                if self.sm.updated['modelV2']:
                    model = self.sm['modelV2']
                    
                    # Get desired path heading (psi) from model
                    # This represents where the car should steer
                    if hasattr(model.position, 'y') and len(model.position.y) > 0:
                        # Calculate steering from path deviation
                        # Look ahead ~10m (index 5-10 in trajectory)
                        lookahead_idx = min(5, len(model.position.y) - 1)
                        lateral_offset = model.position.y[lookahead_idx]  # meters
                        lookahead_dist = model.position.x[lookahead_idx]  # meters
                        
                        # Simple proportional steering: angle = atan(offset / distance)
                        import math
                        if lookahead_dist > 0.1:
                            last_steer = math.atan2(lateral_offset, lookahead_dist)
                            no_data_count = 0
                
                # Fallback 1: carControl (if control loop is running)
                elif self.sm.updated['carControl']:
                    car_control = self.sm['carControl']
                    
                    if car_control.enabled and hasattr(car_control.actuators, 'steer'):
                        last_steer = car_control.actuators.steer
                        no_data_count = 0
                
                # Fallback 2: controlsState
                elif self.sm.updated['controlsState']:
                    controls = self.sm['controlsState']
                    
                    if hasattr(controls, 'steeringAngleDeg'):
                        last_steer = controls.steeringAngleDeg * 0.0174533
                        no_data_count = 0
                
                else:
                    no_data_count += 1
                    if no_data_count > 50:  # 5 seconds without data
                        print("⚠️  No openpilot data - is modeld running?")
                        no_data_count = 0
                
                # Convert to PWM
                pwm_value, steer_deg = self.steering_to_pwm(last_steer)
                
                # Send to ESP32
                response = self.send_to_esp32(pwm_value)
                
                # Display status every 10 frames
                if self.frame_count % 10 == 0:
                    elapsed = time.time() - self.start_time
                    hz = self.frame_count / elapsed if elapsed > 0 else 0
                    
                    direction = "RIGHT" if pwm_value > 10 else "LEFT" if pwm_value < -10 else "STRAIGHT"
                    
                    print(f"[{self.frame_count:5d}] "
                          f"Steer: {steer_deg:+6.1f}° "
                          f"PWM: {pwm_value:+4d} "
                          f"Dir: {direction:8s} "
                          f"Hz: {hz:.1f} "
                          f"{'✓' if response else '○'}")
                
                # Check modelV2 for vision debug info
                if self.sm.updated['modelV2'] and self.frame_count % 30 == 0:
                    model = self.sm['modelV2']
                    if hasattr(model, 'laneLines') and len(model.laneLines) > 0:
                        print(f"   🛣️  Vision: {len(model.laneLines)} lane lines detected")
                    if hasattr(model.position, 'y') and len(model.position.y) > 5:
                        print(f"   📍 Path deviation: {model.position.y[5]:.2f}m at {model.position.x[5]:.1f}m ahead")
                
                # Throttle to ~20Hz
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Stopped by user")
        
        finally:
            # Send stop command
            if self.ser:
                self.send_to_esp32(0)
                self.ser.write(b"STOP\n")
                self.ser.close()
            
            elapsed = time.time() - self.start_time
            print("\n" + "="*70)
            print("  ✅ BRIDGE SESSION COMPLETE")
            print("="*70)
            print(f"\n  Frames processed: {self.frame_count}")
            print(f"  Session duration: {elapsed:.1f}s")
            print(f"  Average rate: {self.frame_count/elapsed:.1f} Hz")
            print("="*70 + "\n")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Openpilot LKAS Bridge to ESP32')
    parser.add_argument('--config', default='../bridge/config.yaml',
                       help='Path to config file')
    parser.add_argument('--port', default='/dev/ttyUSB0',
                       help='Serial port for ESP32')
    parser.add_argument('--baud', type=int, default=115200,
                       help='Serial baud rate')
    
    args = parser.parse_args()
    
    # Resolve config path
    config_path = Path(__file__).parent / args.config
    if not config_path.exists():
        config_path = Path.home() / "steering-actuator" / "bridge" / "config.yaml"
    
    bridge = OpenpilotSteeringBridge(config_path, args.port, args.baud)
    bridge.run()

if __name__ == '__main__':
    main()
