#!/usr/bin/env python3
"""
Complete LKAS System with Openpilot's Official UI
Uses openpilot's built-in UI that already has VisionIPC support
"""

import subprocess
import time
import signal
import sys
import os
from pathlib import Path

class LKASSystemWithUI:
    def __init__(self):
        self.processes = []
        self.openpilot_path = Path.home() / "openpilot"
        self.venv_python = self.openpilot_path / ".venv" / "bin" / "python3"
        
    def start_process(self, name, cmd, env=None, show_output=False):
        """Start a process and track it"""
        print(f"Starting {name}...")
        
        if show_output:
            proc = subprocess.Popen(cmd, env=env)
        else:
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        self.processes.append((name, proc))
        time.sleep(2)
        
        if proc.poll() is not None:
            print(f"❌ {name} failed to start!")
            if not show_output:
                output, _ = proc.communicate()
                print(output.decode() if output else "")
            return False
        
        print(f"✓ {name} started (PID: {proc.pid})")
        return True
    
    def launch(self):
        """Launch complete LKAS system with visual UI"""
        print("\n" + "="*70)
        print("  🚗 OPENPILOT LKAS - COMPLETE SYSTEM WITH VISUAL UI")
        print("="*70)
        print("\n  Components:")
        print("  1. camerad - 720p webcam capture")
        print("  2. modeld - neural network lane detection")
        print("  3. Openpilot UI - visual display with lane overlays")
        print("  4. bridge - steering commands to ESP32")
        print("\n" + "="*70 + "\n")
        
        env = os.environ.copy()
        env['PYTHONPATH'] = str(self.openpilot_path)
        env['DISPLAY'] = ':0'
        
        # 1. Start camerad
        if not self.start_process(
            "camerad",
            [str(self.venv_python), str(self.openpilot_path / "tools" / "webcam" / "camerad.py")],
            env={**env, 'ROAD_CAM': '0'}
        ):
            return False
        
        # 2. Start modeld in demo mode
        if not self.start_process(
            "modeld",
            [str(self.venv_python), str(self.openpilot_path / "selfdrive" / "modeld" / "modeld.py"), "--demo"],
            env=env
        ):
            return False
        
        print("\n⏳ Waiting for vision system (5 seconds)...\n")
        time.sleep(5)
        
        # 3. Start openpilot's official UI (has VisionIPC built-in!)
        print("Starting Openpilot's official UI...")
        if not self.start_process(
            "openpilot UI",
            [str(self.venv_python), str(self.openpilot_path / "tools" / "replay" / "ui.py")],
            env=env,
            show_output=False
        ):
            print("⚠️  UI failed, continuing without it...")
        else:
            print("   ✓ UI window should appear in VcXsrv\n")
            time.sleep(2)
        
        # 4. Start bridge (steering output)
        bridge_script = Path(__file__).parent / "scripts" / "openpilot_bridge.py"
        if not self.start_process(
            "bridge",
            [str(self.venv_python), str(bridge_script)],
            env=env,
            show_output=True
        ):
            return False
        
        print("\n" + "="*70)
        print("  ✅ LKAS SYSTEM OPERATIONAL")
        print("="*70)
        print("\n  You should now see:")
        print("  • X11 window with camera feed + lane overlays")
        print("  • Steering values scrolling in this terminal")
        print("\n  📹 Point camera at real roads to test lane detection!")
        print("\n  Press Ctrl+C to stop")
        print("="*70 + "\n")
        
        return True
    
    def monitor(self):
        """Monitor running processes"""
        try:
            while True:
                for name, proc in self.processes:
                    if proc.poll() is not None:
                        print(f"\n⚠️  {name} stopped unexpectedly!")
                        self.cleanup()
                        return
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping system...")
            self.cleanup()
    
    def cleanup(self):
        """Stop all processes"""
        print("\nStopping all components...")
        for name, proc in reversed(self.processes):
            if proc.poll() is None:
                print(f"  Stopping {name}...")
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
        print("\n✅ All components stopped\n")

def main():
    system = LKASSystemWithUI()
    
    def signal_handler(sig, frame):
        system.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if system.launch():
        system.monitor()
    else:
        print("\n❌ System failed to start!")
        system.cleanup()
        sys.exit(1)

if __name__ == '__main__':
    main()
