#!/usr/bin/env python3
"""
Test script for ESP32 serial communication
Sends test commands and verifies motor response
"""

import serial
import time
import sys
import argparse


def test_serial_connection(port: str, baud: int = 115200):
    """Test basic serial communication with ESP32"""
    print(f"Testing serial connection to {port} @ {baud} baud...")
    
    try:
        ser = serial.Serial(port, baud, timeout=2)
        time.sleep(2)  # Wait for ESP32 to initialize
        
        # Read startup message
        if ser.in_waiting:
            msg = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"✓ ESP32 connected: {msg}")
        else:
            print("⚠ No startup message received")
        
        return ser
    except serial.SerialException as e:
        print(f"✗ Failed to connect: {e}")
        sys.exit(1)


def test_stop_command(ser: serial.Serial):
    """Test emergency stop command"""
    print("\nTesting STOP command...")
    ser.write(b"STOP\n")
    time.sleep(0.1)
    
    # Check for response
    if ser.in_waiting:
        response = ser.readline().decode('utf-8', errors='ignore').strip()
        print(f"  Response: {response}")
    
    print("✓ STOP command sent")


def test_pwm_range(ser: serial.Serial):
    """Test PWM commands in both directions"""
    print("\nTesting PWM range...")
    
    test_values = [
        (50, "Low forward"),
        (100, "Medium forward"),
        (150, "High forward"),
        (0, "Neutral"),
        (-50, "Low reverse"),
        (-100, "Medium reverse"),
        (-150, "High reverse"),
        (0, "Back to neutral")
    ]
    
    for pwm, description in test_values:
        cmd = f"S:{pwm:+d}\n"
        print(f"  Sending: {cmd.strip()} ({description})")
        ser.write(cmd.encode('utf-8'))
        time.sleep(1.5)
        
        # Check for errors
        if ser.in_waiting:
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            if "ERROR" in response:
                print(f"  ⚠ {response}")
    
    # Final stop
    ser.write(b"STOP\n")
    print("✓ PWM range test complete")


def test_watchdog(ser: serial.Serial):
    """Test watchdog timeout"""
    print("\nTesting watchdog (500ms timeout)...")
    print("  Sending command, then waiting...")
    
    ser.write(b"S:+100\n")
    time.sleep(0.2)
    
    print("  Waiting for watchdog to trigger (600ms)...")
    time.sleep(0.6)
    
    print("✓ Watchdog should have stopped motor")
    print("  (Motor should now be stopped)")


def test_invalid_commands(ser: serial.Serial):
    """Test handling of invalid commands"""
    print("\nTesting invalid commands...")
    
    invalid_cmds = [
        b"INVALID\n",
        b"S:999999\n",
        b"S:abc\n",
        b"random garbage\n"
    ]
    
    for cmd in invalid_cmds:
        print(f"  Sending: {cmd.decode('utf-8', errors='ignore').strip()}")
        ser.write(cmd)
        time.sleep(0.2)
        
        # Should get error response
        if ser.in_waiting:
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"    Response: {response}")
    
    print("✓ Invalid command handling tested")


def interactive_mode(ser: serial.Serial):
    """Interactive command prompt"""
    print("\nInteractive mode - Enter commands (Ctrl+C to exit):")
    print("  S:<pwm>  - Set PWM (-255 to +255)")
    print("  STOP     - Emergency stop")
    print("  q        - Quit")
    
    try:
        while True:
            cmd = input("> ").strip()
            
            if cmd.lower() == 'q':
                break
            
            if not cmd:
                continue
            
            # Send command
            ser.write(f"{cmd}\n".encode('utf-8'))
            time.sleep(0.05)
            
            # Check for response
            if ser.in_waiting:
                response = ser.readline().decode('utf-8', errors='ignore').strip()
                print(f"  {response}")
    
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        ser.write(b"STOP\n")


def main():
    parser = argparse.ArgumentParser(description='Test ESP32 steering controller')
    parser.add_argument(
        '--port',
        type=str,
        default='/dev/ttyUSB0',
        help='Serial port (default: /dev/ttyUSB0)'
    )
    parser.add_argument(
        '--baud',
        type=int,
        default=115200,
        help='Baud rate (default: 115200)'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    parser.add_argument(
        '--skip-tests',
        action='store_true',
        help='Skip automated tests (for interactive only)'
    )
    
    args = parser.parse_args()
    
    # Connect
    ser = test_serial_connection(args.port, args.baud)
    
    try:
        if not args.skip_tests:
            # Run automated tests
            test_stop_command(ser)
            time.sleep(0.5)
            
            test_pwm_range(ser)
            time.sleep(0.5)
            
            test_watchdog(ser)
            time.sleep(0.5)
            
            test_invalid_commands(ser)
            time.sleep(0.5)
            
            print("\n" + "="*50)
            print("✓ All automated tests complete!")
            print("="*50)
        
        if args.interactive:
            interactive_mode(ser)
    
    finally:
        ser.write(b"STOP\n")
        ser.close()
        print("\nSerial connection closed")


if __name__ == '__main__':
    main()
