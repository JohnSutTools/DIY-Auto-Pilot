#!/usr/bin/env python3
"""
Unified launcher for openpilot + steering actuator bridge
Starts everything as a single integrated system
"""

import os
import sys
import signal
import subprocess
import time
import argparse
from pathlib import Path

class OpenpilotSteeringSystem:
    def __init__(self, config_path: str, openpilot_path: str = None):
        self.config_path = config_path
        self.processes = []
        
        # Find openpilot
        if openpilot_path:
            self.openpilot_path = Path(openpilot_path)
        else:
            self.openpilot_path = self._find_openpilot()
        
        if not self.openpilot_path or not self.openpilot_path.exists():
            print("ERROR: openpilot not found!")
            print("\nRun setup first:")
            print("  ./scripts/setup_system.sh")
            sys.exit(1)
        
        print(f"✓ Using openpilot at: {self.openpilot_path}")
        
        # Setup environment for all processes
        # Start fresh to avoid Windows/WSL path pollution
        self.env = {}
        
        # Copy essential environment variables
        essential_vars = ['PATH', 'HOME', 'USER', 'SHELL', 'TERM', 'LANG', 'LC_ALL']
        for var in essential_vars:
            if var in os.environ:
                self.env[var] = os.environ[var]
        
        # Add openpilot to PYTHONPATH - THIS IS CRITICAL
        self.env['PYTHONPATH'] = str(self.openpilot_path)
        
        print(f"✓ PYTHONPATH set to: {self.env['PYTHONPATH']}")
        
    def _find_openpilot(self) -> Path:
        """Find openpilot installation"""
        possible_paths = [
            Path.home() / "openpilot",
            Path(__file__).parent.parent / "openpilot",
            Path("/data/openpilot"),
        ]
        
        for path in possible_paths:
            if path.exists() and (path / "launch_openpilot.sh").exists():
                return path
        
        return None
    
    def start_openpilot(self):
        """Start openpilot with webcam support"""
        print("\n🚗 Starting openpilot...")
        
        # Use our configured environment
        env = self.env.copy()
        
        # Enable webcam mode (for USB camera)
        env['USE_WEBCAM'] = '1'
        
        # LKAS only mode (disable longitudinal control)
        env['DISABLE_LONGITUDINAL'] = '1'
        
        # Start openpilot
        op_cmd = [str(self.openpilot_path / "launch_openpilot.sh")]
        
        proc = subprocess.Popen(
            op_cmd,
            cwd=str(self.openpilot_path),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        self.processes.append(("openpilot", proc))
        print("✓ Openpilot started")
        
        # Wait for openpilot to initialize
        print("  Waiting for openpilot to initialize (10s)...")
        time.sleep(10)
        
        return proc
    
    def start_bridge(self):
        """Start the steering bridge"""
        print("\n🔌 Starting steering bridge...")
        
        # Get the correct path relative to this script
        project_root = Path(__file__).parent
        bridge_path = project_root / "bridge" / "op_serial_bridge.py"
        
        if not bridge_path.exists():
            print(f"ERROR: Bridge script not found at {bridge_path}")
            sys.exit(1)
        
        print(f"  Using bridge at: {bridge_path}")
        
        # Use openpilot's venv Python to ensure cereal is available
        venv_python = self.openpilot_path / ".venv" / "bin" / "python"
        if not venv_python.exists():
            print(f"ERROR: Openpilot venv not found at {venv_python}")
            sys.exit(1)
        
        # CRITICAL: Use openpilot's Python and environment with PYTHONPATH set
        print(f"  Using Python: {venv_python}")
        print(f"  PYTHONPATH: {self.env.get('PYTHONPATH', 'NOT SET')}")
        
        proc = subprocess.Popen(
            [str(venv_python), str(bridge_path), "--config", self.config_path, "--debug"],
            env=self.env,  # Pass environment with PYTHONPATH to openpilot
            cwd=str(project_root),  # Set working directory
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        self.processes.append(("bridge", proc))
        print("✓ Bridge started")
        
        return proc
    
    def monitor_processes(self):
        """Monitor all processes and stream output"""
        print("\n" + "="*60)
        print("System running - Press Ctrl+C to stop")
        print("="*60 + "\n")
        
        try:
            while True:
                for name, proc in self.processes:
                    # Check if process is still running
                    if proc.poll() is not None:
                        print(f"\n⚠️  {name} exited with code {proc.returncode}")
                        self.shutdown()
                        sys.exit(1)
                    
                    # Read output (non-blocking)
                    if proc.stdout:
                        line = proc.stdout.readline()
                        if line:
                            print(f"[{name}] {line.rstrip()}")
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Shutdown requested...")
            self.shutdown()
    
    def shutdown(self):
        """Gracefully shutdown all processes"""
        print("\nStopping all processes...")
        
        for name, proc in reversed(self.processes):
            if proc.poll() is None:  # Still running
                print(f"  Stopping {name}...")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"  Force killing {name}...")
                    proc.kill()
        
        print("✓ All processes stopped")
    
    def run(self):
        """Run the complete system"""
        print("\n" + "="*60)
        print("Openpilot Steering Actuator System")
        print("="*60)
        
        # Start openpilot
        self.start_openpilot()
        
        # Start bridge
        self.start_bridge()
        
        # Monitor
        self.monitor_processes()


def main():
    parser = argparse.ArgumentParser(
        description='Launch complete openpilot steering system'
    )
    
    # Get project root directory
    project_root = Path(__file__).parent
    default_config = project_root / "bridge" / "config.yaml"
    
    parser.add_argument(
        '--config',
        type=str,
        default=str(default_config),
        help='Bridge configuration file'
    )
    parser.add_argument(
        '--openpilot-path',
        type=str,
        help='Path to openpilot installation (auto-detected if not specified)'
    )
    
    args = parser.parse_args()
    
    # Check config exists
    if not os.path.exists(args.config):
        print(f"ERROR: Config file not found: {args.config}")
        print(f"Expected at: {args.config}")
        print(f"\nProject root: {project_root}")
        sys.exit(1)
    
    # Create and run system
    system = OpenpilotSteeringSystem(args.config, args.openpilot_path)
    system.run()


if __name__ == '__main__':
    main()
