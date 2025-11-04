#!/usr/bin/env python3
"""
Complete Openpilot LKAS System with Visual UI
Starts: camerad -> modeld -> UI (visual) + bridge (ESP32)
"""

import subprocess
import time
import signal
import sys
import os
from pathlib import Path

class OpenpilotLKASSystem:
    def __init__(self, show_ui=True):
        self.processes = []
        self.show_ui = show_ui
        self.openpilot_path = Path.home() / "openpilot"
        self.venv_python = self.openpilot_path / ".venv" / "bin" / "python3"
        
    def start_process(self, name, cmd, env=None, show_output=False):
        """Start a process and track it"""
        print(f"Starting {name}...")
        
        if show_output:
            # Show output in real-time
            proc = subprocess.Popen(
                cmd,
                env=env,
                stdout=None,  # Inherit stdout
                stderr=None,   # Inherit stderr
            )
        else:
            # Capture output
            proc = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
        
        self.processes.append((name, proc))
        time.sleep(2)  # Give it time to start
        
        # Check if it's still running
        if proc.poll() is not None:
            print(f"❌ {name} failed to start!")
            if not show_output:
                output, _ = proc.communicate()
                print(output)
            return False
        
        print(f"✓ {name} started (PID: {proc.pid})")
        return True
    
    def launch(self):
        """Launch all components"""
        print("\n" + "="*70)
        print("  🚗 OPENPILOT LKAS SYSTEM - DEMO MODE WITH VISUAL UI")
        print("="*70)
        print("\n  Starting components:")
        print("  1. Camera daemon (camerad) - 720p webcam capture")
        print("  2. Vision model (modeld --demo) - neural network lane detection")
        if self.show_ui:
            print("  3. Visual UI (X11 display) - lane overlay visualization")
        print("  4. Steering bridge (ESP32) - PWM motor commands")
        print("\n  Note: Using demo mode (no CarParams/plannerd/controlsd needed)")
        print("        Bridge reads steering directly from modelV2 output")
        print("\n" + "="*70 + "\n")
        
        env = os.environ.copy()
        env['PYTHONPATH'] = str(self.openpilot_path)
        env['DISPLAY'] = ':0'  # X Server display
        
        # 1. Start camerad (webcam capture)
        if not self.start_process(
            "camerad",
            [str(self.venv_python),
             str(self.openpilot_path / "tools" / "webcam" / "camerad.py")],
            env={**env, 'ROAD_CAM': '0'}
        ):
            return False
        
        # 2. Start modeld in DEMO mode (no CarParams needed!)
        if not self.start_process(
            "modeld",
            [str(self.venv_python),
             str(self.openpilot_path / "selfdrive" / "modeld" / "modeld.py"),
             "--demo"],  # Demo mode bypasses CarParams requirement
            env=env
        ):
            return False
        
        print("\n⏳ Waiting for vision system to initialize (5 seconds)...\n")
        time.sleep(5)
        
        # 3. Start viewer if requested (OpenCV lane visualization)
        if self.show_ui:
            viewer_script = Path(__file__).parent / "webcam_lkas_viewer.py"
            if not self.start_process(
                "lane viewer",
                [str(self.venv_python), str(viewer_script)],
                env=env,
                show_output=False  # Don't show output, it has its own window
            ):
                print("⚠️  Viewer failed to start, continuing without it...")
            else:
                print("   ✓ Lane detection viewer starting (opens in separate window)\n")
                time.sleep(3)
        
        # 4. Start bridge (steering commands to ESP32)
        # Show output in real-time so we can see steering values
        bridge_script = Path(__file__).parent / "openpilot_bridge.py"
        if not self.start_process(
            "bridge",
            [str(self.venv_python), str(bridge_script)],
            env=env,
            show_output=True  # Show steering output
        ):
            return False
        
        print("\n" + "="*70)
        print("  ✅ ALL SYSTEMS OPERATIONAL - DEMO MODE")
        print("="*70)
        print("\n  System is now:")
        print("  • Capturing webcam video at 720p (30 FPS)")
        print("  • Detecting lanes with openpilot neural network (modeld --demo)")
        if self.show_ui:
            print("  • Displaying visualization with lane overlays in X11 window")
        print("  • Computing steering from modelV2.position")
        print("  • Sending PWM commands to ESP32 (or simulating)")
        print("\n  📹 Point camera at real roads to see:")
        print("     - Lane detection overlays in UI window")
        print("     - Steering angle/PWM values in console")
        print("\n  Press Ctrl+C to stop all components")
        print("="*70 + "\n")
        
        return True
    
    def monitor(self):
        """Monitor running processes"""
        try:
            while True:
                # Check if any process died
                for name, proc in self.processes:
                    if proc.poll() is not None:
                        print(f"\n⚠️  {name} stopped unexpectedly!")
                        self.cleanup()
                        return
                
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n\n🛑 Shutdown requested...")
            self.cleanup()
    
    def cleanup(self):
        """Stop all processes gracefully"""
        print("\n\nStopping all components...")
        
        # Stop in reverse order
        for name, proc in reversed(self.processes):
            if proc.poll() is None:  # Still running
                print(f"  Stopping {name}...")
                proc.terminate()
                
                # Wait up to 3 seconds
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    print(f"  Force killing {name}...")
                    proc.kill()
        
        print("\n✅ All components stopped")
        print("\nSession complete!\n")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Openpilot LKAS System with Visual Display',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full system with UI
  python3 launch_openpilot_lkas.py --ui
  
  # Without UI (bridge output only)
  python3 launch_openpilot_lkas.py --no-ui
        """
    )
    parser.add_argument('--ui', dest='show_ui', action='store_true',
                       default=True,
                       help='Show visual UI in X11 window (default)')
    parser.add_argument('--no-ui', dest='show_ui', action='store_false',
                       help='Run without visual UI')
    
    args = parser.parse_args()
    
    # Check if DISPLAY is set
    if args.show_ui and 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':0'
        print("Set DISPLAY=:0 for X11 forwarding")
    
    system = OpenpilotLKASSystem(show_ui=args.show_ui)
    
    # Register signal handlers
    def signal_handler(sig, frame):
        system.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Launch system
    if system.launch():
        # Monitor until stopped
        system.monitor()
    else:
        print("\n❌ System failed to start!")
        system.cleanup()
        sys.exit(1)

if __name__ == '__main__':
    main()
