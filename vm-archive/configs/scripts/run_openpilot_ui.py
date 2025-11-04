#!/usr/bin/env python3
"""
Launch openpilot UI with webcam
Shows the actual lane detection visualization
"""

import os
import sys
import subprocess
import time
from pathlib import Path

OPENPILOT_PATH = Path.home() / "openpilot"
PROJECT_ROOT = Path.home() / "steering-actuator"

def check_x_server():
    """Check if X server is available"""
    display = os.environ.get('DISPLAY')
    if not display:
        print("❌ ERROR: DISPLAY not set")
        print("\nTo fix:")
        print("1. Install VcXsrv on Windows")
        print("2. Start XLaunch with 'Disable access control' checked")
        print("3. In WSL, run:")
        print("   export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0")
        print("\nSee docs/WEBCAM_WITH_UI.md for full instructions")
        return False
    
    # Test X connection
    try:
        result = subprocess.run(['xdpyinfo'], capture_output=True, timeout=2)
        if result.returncode == 0:
            print(f"✓ X Server connected: {display}")
            return True
        else:
            print(f"❌ Cannot connect to X server at {display}")
            return False
    except FileNotFoundError:
        print("⚠️  xdpyinfo not installed. Installing x11-utils...")
        subprocess.run(['sudo', 'apt', 'install', '-y', 'x11-utils'], check=True)
        return check_x_server()
    except Exception as e:
        print(f"❌ X Server test failed: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("  🚗 OPENPILOT UI WITH WEBCAM")
    print("="*70)
    print("\n  This will show the FULL openpilot interface with:")
    print("    • Live camera feed")
    print("    • Lane detection overlays")
    print("    • Path prediction")
    print("    • Steering visualization")
    print("\n" + "="*70 + "\n")
    
    # Check X server
    print("Checking X Server...")
    if not check_x_server():
        print("\n💡 TIP: Run headless mode instead:")
        print("   python3 scripts/run_full_system.py")
        sys.exit(1)
    
    # Check camera
    print("\nChecking camera...")
    if not Path('/dev/video0').exists():
        print("❌ Camera not found at /dev/video0")
        print("\nAttach camera:")
        print("  usbipd attach --wsl --busid 3-4")
        sys.exit(1)
    print("✓ Camera found")
    
    print("\n" + "="*70)
    print("  🚀 STARTING OPENPILOT")
    print("="*70 + "\n")
    
    # Set environment
    env = os.environ.copy()
    env['USE_WEBCAM'] = '1'
    env['ROAD_CAM'] = '0'
    env['PYTHONPATH'] = str(OPENPILOT_PATH)
    env['BASEDIR'] = str(OPENPILOT_PATH)
    
    # Start openpilot with UI
    try:
        print("Starting openpilot UI...")
        print("(This may take 30-60 seconds to initialize)\n")
        
        # Use the replay UI which works without panda
        ui_cmd = [
            str(OPENPILOT_PATH / ".venv" / "bin" / "python"),
            str(OPENPILOT_PATH / "tools" / "replay" / "ui.py"),
            "localhost"  # Connect to local messaging
        ]
        
        proc = subprocess.Popen(
            ui_cmd,
            env=env,
            cwd=str(OPENPILOT_PATH)
        )
        
        print("✓ UI started")
        print("\n" + "="*70)
        print("  Look for the openpilot window on your screen!")
        print("="*70)
        print("\n  Press Ctrl+C here to stop\n")
        
        proc.wait()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        proc.terminate()
        proc.wait()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTry headless mode instead:")
        print("  python3 scripts/run_full_system.py")

if __name__ == '__main__':
    if not OPENPILOT_PATH.exists():
        print(f"ERROR: openpilot not found at {OPENPILOT_PATH}")
        print("Run: ./scripts/setup_system.sh")
        sys.exit(1)
    
    main()
