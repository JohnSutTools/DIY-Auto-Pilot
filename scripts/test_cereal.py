#!/usr/bin/env python3
"""
Test script to verify openpilot/cereal is accessible
Run this BEFORE launch.py to diagnose issues
"""

import sys
import os
from pathlib import Path

print("="*60)
print("Openpilot Environment Test")
print("="*60)

# Find openpilot
possible_paths = [
    Path.home() / "openpilot",
    Path("/data/openpilot"),
]

openpilot_path = None
for path in possible_paths:
    if path.exists():
        openpilot_path = path
        break

if not openpilot_path:
    print("\n❌ ERROR: openpilot not found!")
    print("   Expected locations:")
    for path in possible_paths:
        print(f"   - {path}")
    print("\n   Run: ./scripts/setup_system.sh")
    sys.exit(1)

print(f"\n✓ Found openpilot at: {openpilot_path}")

# Set PYTHONPATH
os.environ['PYTHONPATH'] = str(openpilot_path)
sys.path.insert(0, str(openpilot_path))

print(f"✓ PYTHONPATH set to: {openpilot_path}")

# Test cereal import
print("\n" + "="*60)
print("Testing cereal import...")
print("="*60)

try:
    import cereal
    print("✓ cereal package found")
except ImportError as e:
    print(f"❌ Failed to import cereal: {e}")
    sys.exit(1)

try:
    import cereal.messaging
    print("✓ cereal.messaging found")
except ImportError as e:
    print(f"❌ Failed to import cereal.messaging: {e}")
    print("\n   This usually means openpilot wasn't built properly.")
    print("   Run: cd ~/openpilot && scons -j$(nproc)")
    sys.exit(1)

try:
    messaging = cereal.messaging
    print("✓ cereal.messaging loaded successfully")
except Exception as e:
    print(f"❌ Error loading cereal.messaging: {e}")
    sys.exit(1)

# Test creating a subscriber (without actually connecting)
print("\n" + "="*60)
print("Testing cereal functionality...")
print("="*60)

try:
    # This should work even without openpilot running
    sm = messaging.SubMaster(['carControl'])
    print("✓ Created SubMaster for 'carControl'")
except Exception as e:
    print(f"❌ Failed to create SubMaster: {e}")
    sys.exit(1)

# All tests passed
print("\n" + "="*60)
print("✅ ALL TESTS PASSED!")
print("="*60)
print("\nYour environment is correctly configured.")
print("You can now run: python3 launch.py")
print()
