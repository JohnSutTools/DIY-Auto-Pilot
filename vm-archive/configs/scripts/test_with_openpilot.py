#!/usr/bin/env python3
"""
Quick test with openpilot replay data
Monitors openpilot messages and sends to ESP32
"""

import argparse
import sys
import time
import subprocess
import os

def check_openpilot():
    """Check if openpilot is available"""
    try:
        import cereal.messaging
        return True
    except ImportError:
        return False

def find_openpilot():
    """Try to find openpilot installation"""
    possible_paths = [
        os.path.expanduser("~/openpilot"),
        os.path.expanduser("~/comma/openpilot"),
        "/data/openpilot",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def main():
    parser = argparse.ArgumentParser(
        description='Test bridge with openpilot replay data'
    )
    parser.add_argument(
        '--route',
        type=str,
        help='Openpilot route to replay (format: <route>|<segment>)'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='bridge/config.yaml',
        help='Bridge config file'
    )
    
    args = parser.parse_args()
    
    # Check openpilot
    if not check_openpilot():
        print("\n❌ ERROR: openpilot (cereal) not found\n")
        
        op_path = find_openpilot()
        if op_path:
            print(f"Found openpilot at: {op_path}")
            print("\nAdd to PYTHONPATH:")
            print(f"  export PYTHONPATH=\"${{PYTHONPATH}}:{op_path}\"")
        else:
            print("Openpilot not found. Install it:")
            print("  git clone https://github.com/commaai/openpilot.git ~/openpilot")
            print("  cd ~/openpilot && scons -j$(nproc)")
        
        print("\nSee docs/INTEGRATION.md for details")
        sys.exit(1)
    
    print("✓ Openpilot found")
    
    # Check bridge
    if not os.path.exists('bridge/op_serial_bridge.py'):
        print("❌ ERROR: Run this script from project root")
        sys.exit(1)
    
    print("✓ Bridge found")
    
    # Check config
    if not os.path.exists(args.config):
        print(f"❌ ERROR: Config not found: {args.config}")
        sys.exit(1)
    
    print(f"✓ Config found: {args.config}")
    
    if args.route:
        print(f"\n📼 Replay mode: {args.route}")
        print("\nStart replay in another terminal:")
        print(f"  cd ~/openpilot")
        print(f"  tools/replay/replay '{args.route}'")
        print("\nPress Enter when replay is running...")
        input()
    else:
        print("\n⚠️  No route specified - will listen for any openpilot messages")
        print("   Use --route '<route>|<segment>' to replay specific data")
    
    # Run bridge
    print("\nStarting bridge...\n")
    print("="*60)
    
    try:
        subprocess.run([
            sys.executable,
            'bridge/op_serial_bridge.py',
            '--config', args.config,
            '--debug'
        ])
    except KeyboardInterrupt:
        print("\n\nBridge stopped")

if __name__ == '__main__':
    main()
