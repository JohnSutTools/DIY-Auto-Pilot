#!/usr/bin/env python3
"""
Simulation mode for testing without hardware
Simulates ESP32 and motor responses
"""

import argparse
import time
import logging
from typing import Optional

try:
    import cereal.messaging as messaging
except ImportError:
    print("ERROR: cereal not found. Run setup_system.sh first.")
    exit(1)


class VirtualESP32:
    """Simulates ESP32 motor controller"""
    
    def __init__(self):
        self.current_pwm = 0
        self.last_command_time = time.time()
        self.logger = logging.getLogger("VirtualESP32")
        
    def send_command(self, pwm_value: int):
        """Simulate receiving a PWM command"""
        self.current_pwm = pwm_value
        self.last_command_time = time.time()
        
        # Simulate motor response
        if pwm_value > 0:
            direction = "RIGHT (clockwise)"
        elif pwm_value < 0:
            direction = "LEFT (counter-clockwise)"
        else:
            direction = "NEUTRAL"
        
        self.logger.info(f"🔧 Motor: PWM={pwm_value:+4d} Direction: {direction}")
        
    def check_watchdog(self):
        """Check if watchdog would trigger"""
        elapsed = time.time() - self.last_command_time
        if elapsed > 0.5 and self.current_pwm != 0:
            self.logger.warning("⚠️  Watchdog would trigger - STOP")
            self.current_pwm = 0
            return True
        return False


class SimulatedBridge:
    """Bridge with virtual ESP32"""
    
    def __init__(self, config: dict):
        self.config = config
        self.virtual_esp32 = VirtualESP32()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(name)s] %(message)s'
        )
        self.logger = logging.getLogger("SimBridge")
        
        # Initialize openpilot messaging
        self.sm = messaging.SubMaster(['carControl', 'controlsState'])
        
        self.logger.info("🎮 Simulation mode - Virtual ESP32 ready")
        self.logger.info(f"📊 PWM scale: {config['pwm_scale']}, cap: {config['pwm_cap']}")
        
    def _get_steer_command(self) -> Optional[float]:
        """Extract steering command from openpilot messages"""
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
    
    def run(self):
        """Main simulation loop"""
        self.logger.info("🚀 Simulation running - waiting for openpilot messages...")
        self.logger.info("💡 Tip: Use openpilot replay to send test data")
        
        loop_period = 1.0 / self.config['stream_hz']
        last_steer = 0.0
        message_count = 0
        
        try:
            while True:
                loop_start = time.time()
                
                # Get steering command
                steer = self._get_steer_command()
                
                if steer is not None:
                    message_count += 1
                    
                    # Scale to PWM
                    pwm_value = int(steer * self.config['pwm_scale'])
                    pwm_value = max(-self.config['pwm_cap'], 
                                   min(self.config['pwm_cap'], pwm_value))
                    
                    # Send to virtual motor
                    if abs(steer - last_steer) > 0.01 or message_count % 20 == 0:
                        self.logger.info(f"📡 Steer command: {steer:+.3f} → PWM: {pwm_value:+4d}")
                        self.virtual_esp32.send_command(pwm_value)
                    else:
                        self.virtual_esp32.send_command(pwm_value)
                    
                    last_steer = steer
                else:
                    # No command
                    if message_count == 0:
                        self.logger.debug("⏳ Waiting for openpilot messages...")
                
                # Check watchdog
                self.virtual_esp32.check_watchdog()
                
                # Maintain update rate
                elapsed = time.time() - loop_start
                sleep_time = max(0, loop_period - elapsed)
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            self.logger.info("\n🛑 Simulation stopped")
            self.logger.info(f"📊 Total messages processed: {message_count}")


def load_config(config_path: str) -> dict:
    """Load configuration"""
    import yaml
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    config.setdefault('pwm_scale', 150)
    config.setdefault('pwm_cap', 255)
    config.setdefault('stream_hz', 20)
    
    return config


def main():
    parser = argparse.ArgumentParser(
        description='Simulate steering bridge without hardware'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='bridge/config.yaml',
        help='Configuration file'
    )
    
    args = parser.parse_args()
    
    # Load config
    config = load_config(args.config)
    
    # Run simulation
    bridge = SimulatedBridge(config)
    bridge.run()


if __name__ == '__main__':
    main()
