#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/user/openpilot')

from opendbc.car.car_helpers import interfaces
from openpilot.common.params import Params

# Use MOCK car interface - it has proper geometry for dashcam mode
interface = interfaces['MOCK']
CP = interface.get_non_essential_params('MOCK')

print(f"MOCK CarParams:")
print(f"  fingerprint: {CP.carFingerprint}")
print(f"  dashcamOnly: {CP.dashcamOnly}")
print(f"  wheelbase: {CP.wheelbase}")
print(f"  steerRatio: {CP.steerRatio}")
print(f"  mass: {CP.mass}")
print(f"  centerToFront: {CP.centerToFront}")

# Save it
params = Params()
cp_bytes = CP.to_bytes()
params.put('CarParams', cp_bytes)
params.put('CarParamsCache', cp_bytes)
params.put('CarParamsPersistent', cp_bytes)

print(f"\n✓ Saved MOCK CarParams ({len(cp_bytes)} bytes)")
