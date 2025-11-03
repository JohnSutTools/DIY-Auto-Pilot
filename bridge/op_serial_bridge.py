#!/usr/bin/env python3
"""
Openpilot Serial Bridge
Subscribes to openpilot control messages and forwards steering commands to ESP32
"""

import argparse
import logging
import sys
import time
from typing import Optional

import serial
import yaml

# Openpilot imports
try:
    import cereal.messaging as messaging
except ImportError:
    print("ERROR: cereal not found. Install openpilot or cereal library.")
    sys.exit(1)


class OpenpilotSerialBridge:
    def __init__(self, config_path: str, debug: bool = False):
        """Initialize the bridge with configuration"""
        self.config = self._load_config(config_path)
        self.debug = debug
        
        # Setup logging
        level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s [%(levelname)s] %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize serial connection
        self.serial_port = self._init_serial()
        
        # Initialize openpilot messaging
        op_host = self.config.get('openpilot_host', None)
        if op_host:
            self.sm = messaging.SubMaster(['carControl', 'controlsState'], addr=op_host)
            self.logger.info(f"Connecting to remote openpilot: {op_host}")
        else:
            self.sm = messaging.SubMaster(['carControl', 'controlsState'])
            self.logger.info("Connecting to local openpilot")
        
        self.logger.info(f"Bridge initialized: {self.config['serial_port']} @ {self.config['baud_rate']}")
        self.logger.info(f"PWM scale: {self.config['pwm_scale']}, cap: {self.config['pwm_cap']}")
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Set defaults
            config.setdefault('baud_rate', 115200)
            config.setdefault('pwm_scale', 150)
            config.setdefault('pwm_cap', 255)
            config.setdefault('stream_hz', 20)
            config.setdefault('serial_port', '/dev/ttyUSB0')
            
            return config
        except Exception as e:
            print(f"ERROR loading config: {e}")
            sys.exit(1)
    
    def _init_serial(self) -> serial.Serial:
        """Initialize serial connection to ESP32"""
        try:
            ser = serial.Serial(
                port=self.config['serial_port'],
                baudrate=self.config['baud_rate'],
                timeout=0.1
            )
            time.sleep(2)  # Wait for ESP32 to initialize
            
            # Read startup message
            if ser.in_waiting:
                startup_msg = ser.readline().decode('utf-8', errors='ignore').strip()
                self.logger.info(f"ESP32: {startup_msg}")
            
            return ser
        except serial.SerialException as e:
            self.logger.error(f"Failed to open serial port: {e}")
            sys.exit(1)
    
    def _send_command(self, pwm_value: int):
        """Send PWM command to ESP32"""
        # Clamp to safety limits
        pwm_value = max(-self.config['pwm_cap'], min(self.config['pwm_cap'], pwm_value))
        
        # Format command
        command = f"S:{pwm_value:+d}\n"
        
        try:
            self.serial_port.write(command.encode('utf-8'))
            
            if self.debug:
                self.logger.debug(f"Sent: {command.strip()}")
                
            # Check for ESP32 errors
            if self.serial_port.in_waiting:
                response = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                if response:
                    self.logger.warning(f"ESP32: {response}")
                    
        except serial.SerialException as e:
            self.logger.error(f"Serial write failed: {e}")
            self._emergency_stop()
    
    def _emergency_stop(self):
        """Send emergency stop command"""
        try:
            self.serial_port.write(b"STOP\n")
            self.logger.warning("Emergency STOP sent")
        except Exception as e:
            self.logger.error(f"Failed to send STOP: {e}")
    
    def _get_steer_command(self) -> Optional[float]:
        """Extract steering command from openpilot messages"""
        self.sm.update(0)  # Non-blocking update
        
        # Priority 1: carControl.actuators.steer
        if self.sm.updated['carControl']:
            cc = self.sm['carControl']
            if hasattr(cc, 'actuators') and hasattr(cc.actuators, 'steer'):
                return float(cc.actuators.steer)
        
        # Priority 2: controlsState.steer (fallback)
        if self.sm.updated['controlsState']:
            cs = self.sm['controlsState']
            if hasattr(cs, 'steer'):
                return float(cs.steer)
        
        return None
    
    def run(self):
        """Main bridge loop"""
        self.logger.info("Bridge running. Press Ctrl+C to stop.")
        
        loop_period = 1.0 / self.config['stream_hz']
        last_steer = 0.0
        
        try:
            while True:
                loop_start = time.time()
                
                # Get steering command from openpilot
                steer = self._get_steer_command()
                
                if steer is not None:
                    # Scale to PWM
                    pwm_value = int(steer * self.config['pwm_scale'])
                    
                    # Send to ESP32
                    self._send_command(pwm_value)
                    
                    if self.debug and abs(steer - last_steer) > 0.01:
                        self.logger.debug(f"Steer: {steer:+.3f} -> PWM: {pwm_value:+d}")
                    
                    last_steer = steer
                else:
                    # No command - send neutral but don't stop (openpilot might be starting up)
                    if self.debug:
                        self.logger.debug("No steer command available")
                
                # Maintain update rate
                elapsed = time.time() - loop_start
                sleep_time = max(0, loop_period - elapsed)
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            self.logger.info("\nShutting down...")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
        finally:
            self._emergency_stop()
            self.serial_port.close()
            self.logger.info("Bridge stopped")


def main():
    parser = argparse.ArgumentParser(description='Openpilot Serial Bridge')
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    
    args = parser.parse_args()
    
    bridge = OpenpilotSerialBridge(args.config, debug=args.debug)
    bridge.run()


if __name__ == '__main__':
    main()
