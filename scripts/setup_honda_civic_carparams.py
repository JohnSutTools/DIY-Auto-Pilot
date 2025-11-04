#!/usr/bin/env python3
"""
Setup Honda Civic CarParams for Webcam-Only LKAS Mode

Uses real Honda Civic parameters for better openpilot compatibility
while still running in dashcam-only mode (no CAN connection).
"""

import sys
from pathlib import Path

# Add openpilot to path
openpilot_path = Path.home() / "openpilot"
if not openpilot_path.exists():
    openpilot_path = Path(__file__).parent.parent / "openpilot" / "openpilot"
    
if not openpilot_path.exists():
    print(f"ERROR: openpilot not found at {openpilot_path}")
    sys.exit(1)

sys.path.insert(0, str(openpilot_path))

from cereal import car
from openpilot.common.params import Params

def create_honda_civic_carparams():
    """
    Create CarParams using Honda Civic configuration.
    This provides realistic vehicle parameters while running in dashcam mode.
    """
    
    print("Creating Honda Civic CarParams for Webcam LKAS...")
    
    # Import from opendbc
    from opendbc.car.honda.values import CAR
    from opendbc.car.honda.interface import CarInterface
    from opendbc.car.interfaces import get_interface_attr
    
    # Use Honda Civic (2016-2018 model)
    fingerprint = CAR.HONDA_CIVIC
    
    # Get CarParams from Honda interface
    CP = CarInterface.get_non_essential_params(str(fingerprint))
    
    # Enable dashcam mode (no CAN connection required)
    CP.dashcamOnly = True
    
    # Print configuration
    print(f"\n✓ CarParams created:")
    print(f"  Car: {CP.carFingerprint}")
    print(f"  Brand: {CP.brand}")
    print(f"  Dashcam Only: {CP.dashcamOnly}")
    print(f"  Wheelbase: {CP.wheelbase} m")
    print(f"  Steering Ratio: {CP.steerRatio}")
    print(f"  Mass: {CP.mass} kg")
    print(f"  Lateral Control: {CP.lateralTuning.which()}")
    
    return CP

def save_carparams(CP):
    """Save CarParams to openpilot's persistent storage"""
    params = Params()
    
    # Serialize and save
    params.put("CarParams", CP.to_bytes())
    
    # Verify
    saved_bytes = params.get("CarParams")
    if saved_bytes:
        print(f"\n✓ CarParams saved successfully ({len(saved_bytes)} bytes)")
        return True
    else:
        print("\n✗ Failed to save CarParams")
        return False

def main():
    try:
        # Create CarParams
        CP = create_honda_civic_carparams()
        
        # Save to params
        if save_carparams(CP):
            print("\n" + "="*70)
            print("SUCCESS: Honda Civic CarParams configured")
            print("="*70)
            print("\nYou can now run the LKAS launcher:")
            print("  python3 scripts/launch_lkas.py")
            return 0
        else:
            return 1
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
