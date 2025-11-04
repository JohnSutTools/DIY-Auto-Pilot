#!/usr/bin/env python3
"""
Openpilot LKAS Launcher - Chunk 3

Launches the minimal set of openpilot processes needed for webcam-based LKAS:
  1. webcamerad - Capture frames from USB webcam
  2. modeld - Lane detection and path planning model
  3. plannerd - Path planning
  4. controlsd - Lateral control (steering commands)
  5. bridge - Our serial bridge to ESP32

This is a standalone launcher that doesn't require the full openpilot manager.
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

# Add openpilot to path
OPENPILOT_PATH = Path.home() / "openpilot"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(OPENPILOT_PATH))

# Import openpilot modules (only available on Linux with openpilot installed)
try:
    from cereal import messaging
    from openpilot.common.params import Params
except ImportError as e:
    print(f"Warning: Could not import openpilot modules: {e}")
    print("This script must be run on a system with openpilot installed")
    messaging = None
    Params = None

# Process definitions
class Process:
    def __init__(
    self,
    name: str,
    module: str,
    args: Optional[List[str]] = None,
    env: Optional[Dict[str, str]] = None,
    cwd: Optional[Path] = None,
    ):
        self.name = name
        self.module = module
        self.args = args or []
        self.env = env or {}
        self.proc: Optional[subprocess.Popen] = None
        self.enabled = True
        self.cwd = cwd
    
    def start(self):
        """Start the process"""
        if not self.enabled:
            print(f"⊘ {self.name} is disabled")
            return False
        
        # Use venv python if available, otherwise system python3
        python_exe = OPENPILOT_PATH / ".venv" / "bin" / "python3"
        if not python_exe.exists():
            python_exe = "python3"
        else:
            python_exe = str(python_exe)
        
        # Build command
        if self.module.startswith("/"):
            # Absolute path (for bridge)
            cmd = [python_exe, self.module] + self.args
        else:
            # Python module
            cmd = [python_exe, "-m", self.module] + self.args
        
        # Setup environment
        env = os.environ.copy()
        env.update(self.env)
        
        # Add openpilot to PYTHONPATH
        env["PYTHONPATH"] = str(OPENPILOT_PATH) + ":" + env.get("PYTHONPATH", "")
        
        # Set PWD to match cwd if cwd is specified (fixes kj/filesystem warning)
        if self.cwd:
            env["PWD"] = str(self.cwd)
        
        print(f"▶ Starting {self.name}...")
        try:
            self.proc = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                cwd=str(self.cwd) if self.cwd else None,
            )
            time.sleep(0.5)  # Give it a moment to start
            
            # Check if it's still running
            if self.proc.poll() is not None:
                stdout, stderr = self.proc.communicate()
                print(f"✗ {self.name} failed to start!")
                if stdout:
                    print(f"  stdout: {stdout[:500]}")
                if stderr:
                    print(f"  stderr: {stderr[:500]}")
                return False
            
            print(f"✓ {self.name} started (PID: {self.proc.pid})")
            return True
            
        except Exception as e:
            print(f"✗ Failed to start {self.name}: {e}")
            return False
    
    def stop(self):
        """Stop the process"""
        if self.proc is None:
            return
        
        print(f"◼ Stopping {self.name}...")
        try:
            self.proc.terminate()
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print(f"  Force killing {self.name}...")
            self.proc.kill()
            self.proc.wait()
        
        self.proc = None
    
    def is_running(self) -> bool:
        """Check if process is still running"""
        if self.proc is None:
            return False
        return self.proc.poll() is None


class LKASLauncher:
    def __init__(
        self,
        bridge_path: Path,
        config_path: Path,
        with_ui: bool = True,
        include_webcam: bool = True,
        bridge_only: bool = False,
    ):
        self.bridge_path = bridge_path
        self.config_path = config_path
        self.with_ui = with_ui
        self.include_webcam = include_webcam
        self.bridge_only = bridge_only
        self.processes: List[Process] = []
        self.running = False
        
        # Define processes in dependency order
        self.define_processes()
    
    def define_processes(self):
        """Define all processes needed for LKAS"""
        
        # 1. Webcamerad - Camera capture (USB webcam)
        if self.include_webcam:
            # Auto-detect first available video device
            video_num = "0"
            try:
                for i in range(10):
                    if Path(f"/dev/video{i}").exists():
                        video_num = str(i)
                        break
            except Exception:
                video_num = "0"
            
            self.processes.append(Process(
                name="webcamerad",
                module="tools.webcam.camerad",
                env={"ROAD_CAM": video_num},
                cwd=OPENPILOT_PATH,
            ))
        
        # 2. Modeld - Lane detection model
        self.processes.append(Process(
            name="modeld",
            module="selfdrive.modeld.modeld",
            cwd=OPENPILOT_PATH,
        ))
        
        # 3. Paramsd - Parameter daemon (provides liveParameters)
        self.processes.append(Process(
            name="paramsd",
            module="selfdrive.locationd.paramsd",
            cwd=OPENPILOT_PATH,
        ))
        
        # 4. Locationd - Location/calibration (provides livePose, liveCalibration)
        self.processes.append(Process(
            name="locationd",
            module="selfdrive.locationd.locationd",
            cwd=OPENPILOT_PATH,
        ))
        
        # 5. Calibrationd - Camera calibration
        self.processes.append(Process(
            name="calibrationd",
            module="selfdrive.locationd.calibrationd",
            cwd=OPENPILOT_PATH,
        ))
        
        # 6. Card - Car interface (provides carState, carOutput)
        self.processes.append(Process(
            name="card",
            module="selfdrive.car.card",
            cwd=OPENPILOT_PATH,
        ))
        
        # 7. Selfdrived - State machine and event handling
        self.processes.append(Process(
            name="selfdrived",
            module="selfdrive.selfdrived.selfdrived",
            cwd=OPENPILOT_PATH,
        ))
        
        # 8. UI - Visual display (optional, for POC/debugging)
        if self.with_ui:
            self.processes.append(Process(
                name="ui",
                module="selfdrive.ui.ui",
                env={"DISPLAY": os.environ.get("DISPLAY", ":0")},
                cwd=OPENPILOT_PATH,
            ))
        
        # 9. Minimal Plannerd - Simplified for LKAS-only (no longitudinal control)
        minimal_plannerd_path = Path(__file__).parent / "minimal_plannerd.py"
        self.processes.append(Process(
            name="plannerd",
            module=str(minimal_plannerd_path),
            cwd=PROJECT_ROOT,
        ))
        
        # 10. Controlsd - Lateral control
        self.processes.append(Process(
            name="controlsd",
            module="selfdrive.controls.controlsd",
            cwd=OPENPILOT_PATH,
        ))
        
        # 11. Bridge - Our serial bridge to ESP32
        self.processes.append(Process(
            name="bridge",
            module=str(self.bridge_path),
            args=["--config", str(self.config_path), "--debug"],
            cwd=PROJECT_ROOT,
        ))
        
        # Bridge-only mode disables all other processes
        if self.bridge_only:
            for proc in self.processes:
                if proc.name != "bridge":
                    proc.enabled = False
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        print("=" * 70)
        print("OPENPILOT LKAS LAUNCHER - CHUNK 3")
        print("=" * 70)
        print("\nChecking prerequisites...")
        
        # Check openpilot exists
        if not OPENPILOT_PATH.exists():
            print(f"✗ Openpilot not found at {OPENPILOT_PATH}")
            return False
        print(f"✓ Openpilot found at {OPENPILOT_PATH}")
        
        # Check CarParams exists
        params = Params()
        if not params.get("CarParams"):
            print("✗ CarParams not found. Run scripts/setup_mock_carparams.py first")
            return False
        print("✓ CarParams configured")
        
        # Check bridge exists
        if not self.bridge_path.exists():
            print(f"✗ Bridge not found at {self.bridge_path}")
            return False
        print(f"✓ Bridge found")
        
        # Check config exists
        if not self.config_path.exists():
            print(f"✗ Config not found at {self.config_path}")
            return False
        print(f"✓ Config found")
        
        # Check webcam
        if self.include_webcam:
            webcam_devices = [Path(f"/dev/video{i}") for i in range(10)]
            webcam_found = [w for w in webcam_devices if w.exists()]
            if webcam_found:
                print(f"✓ Webcam detected: {', '.join(str(w) for w in webcam_found)}")
            else:
                print("⚠ Warning: No webcam found")
                print("  System will start but won't receive camera frames")
        else:
            print("✓ Webcam managed externally (skipping internal webcamerad)")
        
        print("\n✓ All prerequisites met!")
        return True
    
    def start_all(self) -> bool:
        """Start all processes in order"""
        print("\n" + "=" * 70)
        print("STARTING PROCESSES")
        print("=" * 70 + "\n")
        
        for proc in self.processes:
            if not proc.start():
                print(f"\n✗ Failed to start {proc.name}, aborting launch")
                self.stop_all()
                return False
            
            # Wait a bit between processes to avoid resource contention
            time.sleep(1)
        
        self.running = True
        print("\n" + "=" * 70)
        print("✓ ALL PROCESSES STARTED")
        print("=" * 70)
        print("\nProcess flow:")
        print("  webcam → webcamerad → modeld → plannerd → controlsd → bridge → ESP32")
        
        if self.with_ui:
            print("\n📺 UI ENABLED:")
            print("  - You should see a window with the camera feed")
            print("  - Lane lines will be drawn in GREEN")
            print("  - Red line shows the desired path")
            print("  - Steering angle/torque displayed on screen")
            print("  - This is perfect for your POC!")
        
        print("\n🚗 POC SETUP:")
        print("  1. Mount laptop with webcam on windshield")
        print("  2. Sit in passenger seat")
        print("  3. Driver drives normally")
        print("  4. Watch UI to see lane detection and steering commands")
        print("  5. Compare virtual steering with real driving")
        
        print("\nPress Ctrl+C to stop all processes")
        print("=" * 70 + "\n")
        
        return True
    
    def stop_all(self):
        """Stop all processes in reverse order"""
        if not self.processes:
            return
        
        print("\n" + "=" * 70)
        print("STOPPING ALL PROCESSES")
        print("=" * 70 + "\n")
        
        # Stop in reverse order
        for proc in reversed(self.processes):
            proc.stop()
        
        self.running = False
        print("\n✓ All processes stopped")
    
    def monitor(self):
        """Monitor processes and restart if they crash"""
        print("Monitoring processes (checking every 2 seconds)...\n")
        
        try:
            while self.running:
                time.sleep(2)
                
                # Check each process
                for proc in self.processes:
                    if proc.enabled and not proc.is_running():
                        print(f"\n⚠ {proc.name} crashed! Checking output...")
                        if proc.proc:
                            try:
                                stdout, stderr = proc.proc.communicate(timeout=1)
                                if stderr:
                                    print(f"  stderr: {stderr[:500]}")
                                if stdout:
                                    print(f"  stdout: {stdout[:500]}")
                            except:
                                print("  (could not retrieve output)")
                        print("Stopping all processes...")
                        self.stop_all()
                        return False
                
        except KeyboardInterrupt:
            print("\n\nReceived Ctrl+C, shutting down...")
            self.stop_all()
            return True
    
    def run(self):
        """Main entry point"""
        # Check prerequisites
        if not self.check_prerequisites():
            return 1
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, lambda s, f: None)  # Handle in monitor loop
        signal.signal(signal.SIGTERM, lambda s, f: self.stop_all())
        
        # Start all processes
        if not self.start_all():
            return 1
        
        # Monitor and wait
        success = self.monitor()
        
        return 0 if success else 1


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Openpilot LKAS Launcher")
    parser.add_argument("--no-ui", action="store_true", help="Run without UI (headless mode)")
    parser.add_argument("--bridge-only", action="store_true", help="Run only the bridge (assumes openpilot already running)")
    parser.add_argument("--external-webcam", action="store_true", help="Skip launching webcamerad (start it manually)")
    args = parser.parse_args()
    
    # Paths
    project_root = Path(__file__).parent.parent
    bridge_path = project_root / "bridge" / "op_serial_bridge.py"
    config_path = project_root / "bridge" / "config.yaml"
    
    # Create launcher
    with_ui = not args.no_ui
    launcher = LKASLauncher(
        bridge_path,
        config_path,
        with_ui=with_ui,
        include_webcam=not args.external_webcam,
        bridge_only=args.bridge_only,
    )
    
    # Run
    exit_code = launcher.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
