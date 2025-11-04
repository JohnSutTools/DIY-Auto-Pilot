#!/usr/bin/env python3
"""
Setup Mock CarParams for Webcam-Only LKAS Mode

This script creates a minimal CarParams configuration that allows openpilot's
control stack (controlsd, plannerd) to run without a real car connection.

Usage:
    python3 scripts/setup_mock_carparams.py
"""

import sys
from pathlib import Path

# Add openpilot to path
openpilot_path = Path(__file__).parent.parent / "openpilot" / "openpilot"
if not openpilot_path.exists():
    print(f"ERROR: openpilot not found at {openpilot_path}")
    print("Please run setup_system.sh first to install openpilot")
    sys.exit(1)

sys.path.insert(0, str(openpilot_path))

from cereal import car
from openpilot.common.params import Params

def create_mock_carparams():
    """
    Create a minimal CarParams for webcam-only LKAS testing.
    
    This configures openpilot to:
    - Run in notCar mode (no CAN bus required)
    - Use angle-based steering control (simpler than torque)
    - Disable longitudinal control (LKAS only)
    - Allow steering at all speeds (including standstill)
    """
    
    print("Creating Mock CarParams for Webcam LKAS...")
    
    CP = car.CarParams.new_message()
    
    # === BASIC IDENTIFICATION ===
    CP.carFingerprint = "MOCK_WEBCAM_LKAS"
    CP.brand = "mock"
    CP.notCar = True  # CRITICAL: Bypass car interface requirements
    
    print("  ✓ Set notCar mode")
    
    # === STEERING CONFIGURATION ===
    # Use angle-based control (easier to work with than torque)
    CP.steerControlType = car.CarParams.SteerControlType.angle
    
    # Max steering angle in degrees (conservative for safety)
    CP.steerMaxBP = [0.]  # Breakpoints (speed in m/s)
    CP.steerMaxV = [180.0]  # Max angle in degrees at each breakpoint
    
    # Allow steering at any speed (including standstill)
    CP.minSteerSpeed = 0.0
    
    # Steering rate limits (degrees per second)
    CP.steerLimitTimer = 1.0
    CP.steerActuatorDelay = 0.1  # Small delay for responsiveness
    
    # Steering at standstill (useful for testing)
    CP.steerAtStandstill = True
    
    print("  ✓ Configured angle-based steering")
    
    # === LATERAL TUNING (PID CONTROLLER) ===
    # PID is simpler than other controllers for initial testing
    CP.lateralTuning.init('pid')
    
    # Proportional gain (how aggressively to steer)
    CP.lateralTuning.pid.kpBP = [0.]  # Breakpoints (speed)
    CP.lateralTuning.pid.kpV = [0.2]  # Gain values (tune this for feel)
    
    # Integral gain (corrects steady-state error)
    CP.lateralTuning.pid.kiBP = [0.]
    CP.lateralTuning.pid.kiV = [0.05]
    
    # Derivative gain (dampens oscillation)
    CP.lateralTuning.pid.kdBP = [0.]
    CP.lateralTuning.pid.kdV = [0.0]
    
    # Feedforward term (predictive steering)
    CP.lateralTuning.pid.kf = 1.0
    
    print("  ✓ Set lateral PID tuning")
    
    # === LONGITUDINAL CONTROL ===
    # DISABLE longitudinal (LKAS only - no speed control)
    CP.openpilotLongitudinalControl = False
    CP.pcmCruise = False  # No cruise control
    
    # These prevent longitudinal control from running
    CP.enableGasInterceptor = False
    CP.enableBsm = False
    
    print("  ✓ Disabled longitudinal control (LKAS only)")
    
    # === SPEED LIMITS ===
    # Min/max speeds for engagement (set wide for testing)
    CP.minEnableSpeed = 0.0  # m/s (0 = can engage at standstill)
    CP.minSteerSpeed = 0.0   # m/s (0 = can steer at standstill)
    
    print("  ✓ Set speed limits")
    
    # === SAFETY CONFIGURATION ===
    # Passive mode - won't send commands to real car (we're using external actuator)
    CP.safetyModel = car.CarParams.SafetyModel.noOutput
    
    # These help with safety checks
    CP.stoppingControl = False
    CP.startAccel = 0.0
    CP.steerRateCost = 0.5
    
    print("  ✓ Set safety configuration")
    
    # === MASS & GEOMETRY (approximate values for calculations) ===
    CP.mass = 1500.0  # kg (approximate car mass)
    CP.wheelbase = 2.7  # meters (approximate)
    CP.steerRatio = 15.0  # Steering ratio (wheel degrees / tire degrees)
    CP.centerToFront = 1.2  # meters (approximate)
    
    print("  ✓ Set vehicle geometry")
    
    # === SAVE TO PARAMS ===
    params = Params()
    cp_bytes = CP.to_bytes()
    
    # Store in all three places (openpilot checks different ones)
    params.put("CarParams", cp_bytes)
    params.put("CarParamsCache", cp_bytes)
    params.put("CarParamsPersistent", cp_bytes)
    
    print("  ✓ Saved to Params storage")
    
    print("\n✅ Mock CarParams created successfully!")
    print("\nConfiguration Summary:")
    print(f"  - Brand: {CP.brand}")
    print(f"  - Fingerprint: {CP.carFingerprint}")
    print(f"  - NotCar Mode: {CP.notCar}")
    print(f"  - Steering Type: {'angle' if CP.steerControlType == car.CarParams.SteerControlType.angle else 'torque'}")
    print(f"  - Lateral Tuning: PID (kP={CP.lateralTuning.pid.kpV[0]:.3f})")
    print(f"  - Longitudinal: {'Enabled' if CP.openpilotLongitudinalControl else 'Disabled'}")
    print(f"  - Min Steer Speed: {CP.minSteerSpeed:.1f} m/s")
    
    return CP

def verify_carparams():
    """Verify CarParams was saved correctly"""
    print("\nVerifying CarParams...")
    params = Params()
    
    # Check all three param keys
    keys = ["CarParams", "CarParamsCache", "CarParamsPersistent"]
    all_present = True
    
    for key in keys:
        data = params.get(key)
        if data:
            print(f"  ✓ {key}: {len(data)} bytes")
        else:
            print(f"  ✗ {key}: MISSING")
            all_present = False
    
    if all_present:
        # Try to parse it back
        cp_bytes = params.get("CarParams")
        CP = car.CarParams.from_bytes(cp_bytes)
        print(f"\n  ✓ Parsed successfully: {CP.carFingerprint}")
        print(f"    notCar={CP.notCar}, brand={CP.brand}")
        return True
    else:
        print("\n  ✗ Verification FAILED - some params missing")
        return False

def main():
    print("=" * 70)
    print("  Mock CarParams Setup for Webcam LKAS")
    print("=" * 70)
    print()
    
    try:
        # Create CarParams
        CP = create_mock_carparams()
        
        # Verify it was saved
        if verify_carparams():
            print("\n" + "=" * 70)
            print("  SUCCESS! Openpilot can now start with this CarParams")
            print("=" * 70)
            print("\nNext steps:")
            print("  1. Launch openpilot: python3 launch.py")
            print("  2. The bridge will connect automatically")
            print("  3. Monitor for carControl messages")
            print()
            return 0
        else:
            print("\n❌ Verification failed")
            return 1
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
