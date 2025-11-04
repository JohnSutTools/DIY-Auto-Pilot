#!/usr/bin/env python3
"""
Diagnostic script to check paths and setup
"""

import os
import sys
from pathlib import Path

print("="*60)
print("Path Diagnostic")
print("="*60)

# Current working directory
print(f"\n1. Current directory: {os.getcwd()}")

# Script location
script_path = Path(__file__).resolve()
print(f"\n2. This script location: {script_path}")
print(f"   Parent directory: {script_path.parent}")

# Project structure (go up one more level since we're in scripts/)
project_root = script_path.parent.parent
print(f"\n3. Project root: {project_root}")

# Check key files
files_to_check = [
    "launch.py",
    "bridge/op_serial_bridge.py",
    "bridge/config.yaml",
    "bridge/requirements.txt",
    "firmware/steering_motor/steering_motor.ino",
]

print("\n4. File existence check:")
for file in files_to_check:
    full_path = project_root / file
    exists = "✓" if full_path.exists() else "✗"
    print(f"   {exists} {file}")
    if full_path.exists():
        print(f"      → {full_path}")

# Check openpilot
print("\n5. Openpilot search:")
possible_openpilot = [
    Path.home() / "openpilot",
    Path("/data/openpilot"),
    project_root.parent / "openpilot",
]

for path in possible_openpilot:
    if path.exists():
        print(f"   ✓ Found: {path}")
        if (path / "launch_openpilot.sh").exists():
            print(f"      → Has launch_openpilot.sh")
    else:
        print(f"   ✗ Not found: {path}")

# Python path
print(f"\n6. Python executable: {sys.executable}")
print(f"   Python version: {sys.version.split()[0]}")

# Environment
print(f"\n7. Key environment variables:")
print(f"   HOME: {os.environ.get('HOME', 'Not set')}")
print(f"   USER: {os.environ.get('USER', 'Not set')}")
print(f"   PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")

# User info
import pwd
user_info = pwd.getpwuid(os.getuid())
print(f"\n8. User info:")
print(f"   Username: {user_info.pw_name}")
print(f"   Home directory: {user_info.pw_dir}")

print("\n" + "="*60)
print("Recommended actions:")
print("="*60)

# Recommendations
if not (project_root / "bridge" / "op_serial_bridge.py").exists():
    print("\n⚠️  Bridge script not found!")
    print("   Make sure you're in the correct directory:")
    print("   cd ~/steering-actuator")

openpilot_found = any(p.exists() for p in possible_openpilot)
if not openpilot_found:
    print("\n⚠️  Openpilot not found!")
    print("   Run setup script:")
    print("   ./scripts/setup_system.sh")

if (project_root / "bridge" / "op_serial_bridge.py").exists() and openpilot_found:
    print("\n✓ All key components found!")
    print("  Ready to run system")

print()
