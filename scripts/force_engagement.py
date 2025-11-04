#!/usr/bin/env python3
"""
Force openpilot to engage and output steering commands
Bypasses all safety checks for testing with webcam only
"""

import sys
import os

# Add openpilot to path
OPENPILOT_PATH = os.path.expanduser("~/openpilot")
sys.path.insert(0, OPENPILOT_PATH)

def patch_state_machine():
    """Patch StateMachine to always return enabled=True, active=True"""
    state_file = os.path.join(OPENPILOT_PATH, "selfdrive/selfdrived/state.py")
    
    with open(state_file, 'r') as f:
        content = f.read()
    
    # Find the return statement and replace it
    original = "    return enabled, active"
    patched = "    # FORCE ENGAGEMENT FOR TESTING\n    return True, True  # Original: enabled, active"
    
    if patched in content:
        print("✓ State machine already patched")
        return True
    
    if original in content:
        content = content.replace(original, patched)
        
        with open(state_file, 'w') as f:
            f.write(content)
        
        print("✓ Patched state machine to force enabled=True, active=True")
        return True
    else:
        print("✗ Could not find return statement to patch")
        return False


def patch_card():
    """Patch card to provide fake car state"""
    card_file = os.path.join(OPENPILOT_PATH, "selfdrive/car/card.py")
    
    with open(card_file, 'r') as f:
        lines = f.readlines()
    
    # Find the line that creates carState
    patch_marker = "# FAKE CAR STATE FOR TESTING"
    
    if any(patch_marker in line for line in lines):
        print("✓ card.py already patched")
        return True
    
    # Find where CS (CarState) is assigned and inject fake values before pm.send
    for i, line in enumerate(lines):
        if 'cs_send.carState = CS' in line:
            # Insert fake values right after this assignment
            indent = len(line) - len(line.lstrip())
            fake_values = f"""{' ' * indent}{patch_marker}
{' ' * indent}CS.vEgo = 15.0  # 15 m/s = ~33 mph (safe engagement speed)
{' ' * indent}CS.cruiseState.enabled = True
{' ' * indent}CS.cruiseState.available = True
{' ' * indent}CS.cruiseState.speed = 15.0
{' ' * indent}CS.standstill = False
{' ' * indent}CS.steerFaultTemporary = False
{' ' * indent}CS.steerFaultPermanent = False
"""
            lines.insert(i + 1, fake_values)
            
            with open(card_file, 'w') as f:
                f.writelines(lines)
            
            print("✓ Patched card.py to provide fake car state (speed=15m/s, cruise=on)")
            return True
    
    print("✗ Could not find CS assignment in card.py")
    return False


def patch_calibrationd():
    """Patch calibrationd to provide valid calibration immediately"""
    calib_file = os.path.join(OPENPILOT_PATH, "selfdrive/locationd/calibrationd.py")
    
    with open(calib_file, 'r') as f:
        lines = f.readlines()
    
    patch_marker = "# FORCE VALID CALIBRATION"
    
    if any(patch_marker in line for line in lines):
        print("✓ calibrationd already patched")
        return True
    
    # Find the reset() method and force valid_blocks to minimum valid value
    for i, line in enumerate(lines):
        if 'self.reset(rpy_init, valid_blocks,' in line:
            # Replace valid_blocks with forced value
            indent = len(line) - len(line.lstrip())
            lines.insert(i, f"{' ' * indent}{patch_marker}\n")
            lines.insert(i + 1, f"{' ' * indent}valid_blocks = max(valid_blocks, 20)  # Force minimum valid\n")
            
            with open(calib_file, 'w') as f:
                f.writelines(lines)
            
            print("✓ Patched calibrationd to force valid calibration")
            return True
    
    print("⚠ calibrationd patch not critical, skipping")
    return True  # Not critical


def main():
    print("="*70)
    print("FORCING OPENPILOT ENGAGEMENT")
    print("="*70)
    print("\nThis will bypass safety checks for testing!")
    print("Use ONLY for bench testing with webcam\n")
    
    success = True
    
    # Patch all three critical components
    success &= patch_state_machine()
    success &= patch_card()
    success &= patch_calibrationd()
    
    if success:
        print("\n" + "="*70)
        print("✅ ALL PATCHES APPLIED")
        print("="*70)
        print("\nNow run:")
        print("  cd ~/openpilot && scons -j4  # Rebuild")
        print("  cd ~/DIY-Auto-Pilot/scripts && python3 launch_lkas.py")
        print("\nYou should see steering commands flowing to the bridge!")
        print("="*70)
        return 0
    else:
        print("\n✗ Some patches failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
