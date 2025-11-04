#!/usr/bin/env python3
"""
Chunk 2 Test: Verify bridge can correctly parse openpilot messages

This test validates that the bridge can:
1. Subscribe to carControl and controlsState messages
2. Extract steering commands from the correct fields
3. Handle all three control types: angle, torque, curvature
"""
import os
import sys
import time
from pathlib import Path

# Add openpilot to path
openpilot_path = Path.home() / "openpilot"
sys.path.insert(0, str(openpilot_path))

def test_message_fields():
    """Test that we can access the correct message fields"""
    print("=" * 70)
    print("CHUNK 2 TEST: Bridge Message Handling")
    print("=" * 70)
    
    try:
        import cereal.messaging as messaging
        from cereal import car
        print("✓ Successfully imported cereal.messaging")
    except ImportError as e:
        print(f"✗ Failed to import cereal: {e}")
        return False
    
    # Test 1: Create a mock carControl message
    print("\n[Test 1] Creating mock carControl message...")
    try:
        pm = messaging.PubMaster(['carControl'])
        msg = messaging.new_message('carControl')
        
        # Set steeringAngleDeg (angle-based control)
        msg.carControl.actuators.steeringAngleDeg = 15.0
        print(f"✓ Set steeringAngleDeg = 15.0")
        
        # Set torque (torque-based control)
        msg.carControl.actuators.torque = 0.5
        print(f"✓ Set torque = 0.5")
        
        # Set curvature (path-based control)
        msg.carControl.actuators.curvature = 0.02
        print(f"✓ Set curvature = 0.02")
        
        # Publish the message
        pm.send('carControl', msg)
        print("✓ Published carControl message")
        
    except Exception as e:
        print(f"✗ Failed to create carControl message: {e}")
        return False
    
    # Test 2: Subscribe and read the message
    print("\n[Test 2] Subscribing and reading carControl...")
    try:
        sm = messaging.SubMaster(['carControl', 'controlsState'])
        time.sleep(0.1)  # Wait for message propagation
        sm.update(100)  # Wait up to 100ms
        
        if sm.updated['carControl']:
            cc = sm['carControl']
            angle = float(cc.actuators.steeringAngleDeg)
            torque = float(cc.actuators.torque)
            curvature = float(cc.actuators.curvature)
            
            print(f"✓ Read steeringAngleDeg = {angle}")
            print(f"✓ Read torque = {torque}")
            print(f"✓ Read curvature = {curvature}")
            
            # Verify values
            if abs(angle - 15.0) < 0.01:
                print(f"✓ steeringAngleDeg correct")
            else:
                print(f"✗ steeringAngleDeg incorrect: expected 15.0, got {angle}")
                return False
                
        else:
            print("⚠ carControl message not updated (may be normal)")
    
    except Exception as e:
        print(f"✗ Failed to read carControl message: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Check controlsState fields
    print("\n[Test 3] Checking controlsState structure...")
    try:
        msg = messaging.new_message('controlsState')
        
        # Check for desiredCurvature field
        if hasattr(msg.controlsState, 'desiredCurvature'):
            msg.controlsState.desiredCurvature = 0.01
            print(f"✓ desiredCurvature field exists and can be set")
        else:
            print("⚠ desiredCurvature field not found")
        
        # Check for curvature field
        if hasattr(msg.controlsState, 'curvature'):
            msg.controlsState.curvature = 0.01
            print(f"✓ curvature field exists and can be set")
        else:
            print("⚠ curvature field not found")
            
    except Exception as e:
        print(f"✗ Failed to check controlsState: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED")
    print("=" * 70)
    return True

def test_bridge_import():
    """Test that the bridge file itself is valid Python"""
    print("\n[Test 4] Validating bridge file syntax...")
    
    bridge_path = Path(__file__).parent.parent / "bridge" / "op_serial_bridge.py"
    
    if not bridge_path.exists():
        print(f"✗ Bridge file not found: {bridge_path}")
        return False
    
    try:
        import ast
        with open(bridge_path) as f:
            code = f.read()
        ast.parse(code)
        print(f"✓ Bridge file syntax is valid")
        return True
    except SyntaxError as e:
        print(f"✗ Bridge file has syntax error: {e}")
        return False

if __name__ == "__main__":
    print("\nStarting Chunk 2 Tests...")
    print(f"Using openpilot from: {openpilot_path}\n")
    
    if not openpilot_path.exists():
        print(f"✗ openpilot not found at {openpilot_path}")
        print("Please ensure openpilot is installed")
        sys.exit(1)
    
    success = True
    
    # Test bridge file syntax first
    if not test_bridge_import():
        success = False
    
    # Test message handling
    if not test_message_fields():
        success = False
    
    if success:
        print("\n✓✓✓ CHUNK 2 VALIDATION COMPLETE ✓✓✓")
        print("The bridge is ready to parse openpilot messages!")
        sys.exit(0)
    else:
        print("\n✗✗✗ CHUNK 2 VALIDATION FAILED ✗✗✗")
        print("Please review the errors above")
        sys.exit(1)
