#!/usr/bin/env python3
"""
Complete Openpilot + Webcam + Visualization System
- Captures from real webcam
- Publishes to openpilot messaging
- Generates steering commands
- Creates visual output frames
- Runs bridge to send PWM commands
"""

import os
import sys
import time
import threading
import subprocess
from pathlib import Path

# Configuration
OPENPILOT_PATH = Path.home() / "openpilot"
PROJECT_ROOT = Path.home() / "steering-actuator"
OUTPUT_DIR = Path.home() / "openpilot_frames"

def start_webcam_publisher():
    """Start webcam capture and publish frames"""
    print("📷 Starting webcam publisher...")
    
    # This will use openpilot's webcam camerad
    cmd = [
        "python3",
        str(OPENPILOT_PATH / "tools" / "webcam" / "camerad.py")
    ]
    
    env = os.environ.copy()
    env['ROAD_CAM'] = '0'
    env['PYTHONPATH'] = str(OPENPILOT_PATH)
    
    proc = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    return proc

def start_modeld():
    """Start openpilot's vision model"""
    print("🧠 Starting vision model (modeld)...")
    
    cmd = [str(OPENPILOT_PATH / "selfdrive" / "modeld" / "modeld")]
    
    env = os.environ.copy()
    env['PYTHONPATH'] = str(OPENPILOT_PATH)
    
    proc = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    return proc

def start_bridge():
    """Start steering bridge"""
    print("🔌 Starting steering bridge...")
    
    cmd = [
        str(OPENPILOT_PATH / ".venv" / "bin" / "python"),
        str(PROJECT_ROOT / "bridge" / "op_serial_bridge.py"),
        "--debug"
    ]
    
    env = os.environ.copy()
    env['PYTHONPATH'] = str(OPENPILOT_PATH)
    
    proc = subprocess.Popen(
        cmd,
        env=env,
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    return proc

def monitor_output(proc, name):
    """Monitor process output"""
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        print(f"[{name}] {line.rstrip()}")

def main():
    print("\n" + "="*70)
    print("  🚗 COMPLETE OPENPILOT SYSTEM WITH WEBCAM")
    print("="*70)
    print("\n  Starting all components:")
    print("    1. Webcam capture (camerad)")
    print("    2. Vision model (modeld)")
    print("    3. Steering bridge")
    print("\n" + "="*70 + "\n")
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    processes = []
    
    try:
        # Start webcam
        cam_proc = start_webcam_publisher()
        processes.append(("Camera", cam_proc))
        time.sleep(2)
        
        # Start model
        model_proc = start_modeld()
        processes.append(("Model", model_proc))
        time.sleep(3)
        
        # Start bridge
        bridge_proc = start_bridge()
        processes.append(("Bridge", bridge_proc))
        
        print("\n" + "="*70)
        print("  ✅ ALL SYSTEMS RUNNING")
        print("="*70)
        print("\n  Monitoring output... Press Ctrl+C to stop\n")
        
        # Monitor all processes
        threads = []
        for name, proc in processes:
            t = threading.Thread(target=monitor_output, args=(proc, name), daemon=True)
            t.start()
            threads.append(t)
        
        # Keep running
        while True:
            # Check if any process died
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"\n⚠️  {name} exited with code {proc.returncode}")
                    raise Exception(f"{name} crashed")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Cleanup
        print("\nStopping all processes...")
        for name, proc in reversed(processes):
            if proc.poll() is None:
                print(f"  Stopping {name}...")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
        
        print("\n✓ All processes stopped\n")

if __name__ == '__main__':
    if not OPENPILOT_PATH.exists():
        print(f"ERROR: openpilot not found at {OPENPILOT_PATH}")
        sys.exit(1)
    
    if not PROJECT_ROOT.exists():
        print(f"ERROR: Project not found at {PROJECT_ROOT}")
        sys.exit(1)
    
    main()
