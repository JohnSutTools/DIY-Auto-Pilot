#!/usr/bin/env python3
"""
Test if CarParams is set correctly and openpilot processes can start

Usage:
    python3 scripts/test_carparams.py
"""

import sys
from pathlib import Path

# Add openpilot to path
openpilot_path = Path(__file__).parent.parent / "openpilot" / "openpilot"
sys.path.insert(0, str(openpilot_path))

from cereal import car
from openpilot.common.params import Params

def main():
    print("=" * 70)
    print("  CarParams Test")
    print("=" * 70)
    print()
    
    params = Params()
    
    # Check if CarParams exists
    print("1. Checking if CarParams exists...")
    cp_bytes = params.get("CarParams")
    
    if not cp_bytes:
        print("  ✗ CarParams NOT FOUND")
        print("\n  Run this first:")
        print("    python3 scripts/setup_mock_carparams.py")
        return 1
    
    print(f"  ✓ CarParams found ({len(cp_bytes)} bytes)")
    
    # Parse it
    print("\n2. Parsing CarParams...")
    try:
        CP = car.CarParams.from_bytes(cp_bytes)
        print("  ✓ Successfully parsed")
    except Exception as e:
        print(f"  ✗ Parse error: {e}")
        return 1
    
    # Display key fields
    print("\n3. CarParams Configuration:")
    print(f"  Fingerprint:        {CP.carFingerprint}")
    print(f"  Brand:              {CP.brand}")
    print(f"  NotCar Mode:        {CP.notCar}")
    print(f"  Steer Control Type: {CP.steerControlType}")
    print(f"  Min Steer Speed:    {CP.minSteerSpeed} m/s")
    print(f"  Steer At Standstill: {CP.steerAtStandstill}")
    print(f"  Longitudinal:       {'Enabled' if CP.openpilotLongitudinalControl else 'Disabled'}")
    
    # Check lateral tuning
    print("\n4. Lateral Tuning:")
    lat_type = CP.lateralTuning.which()
    print(f"  Type: {lat_type}")
    
    if lat_type == 'pid':
        pid = CP.lateralTuning.pid
        print(f"  kP: {pid.kpV[0]:.3f}")
        print(f"  kI: {pid.kiV[0]:.3f}")
        print(f"  kF: {pid.kf:.3f}")
    
    # Verify critical flags for LKAS-only operation
    print("\n5. LKAS-Only Validation:")
    checks = [
        ("notCar enabled", CP.notCar, True),
        ("Longitudinal disabled", CP.openpilotLongitudinalControl, False),
        ("PCM cruise disabled", CP.pcmCruise, False),
        ("Can steer at standstill", CP.steerAtStandstill, True),
    ]
    
    all_good = True
    for name, value, expected in checks:
        status = "✓" if value == expected else "✗"
        print(f"  {status} {name}: {value}")
        if value != expected:
            all_good = False
    
    print("\n" + "=" * 70)
    if all_good:
        print("  ✅ CarParams is correctly configured for LKAS!")
        print("=" * 70)
        print("\n  Ready to launch openpilot:")
        print("    python3 launch.py")
        return 0
    else:
        print("  ⚠️  CarParams has unexpected values")
        print("=" * 70)
        print("\n  Re-run setup:")
        print("    python3 scripts/setup_mock_carparams.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
