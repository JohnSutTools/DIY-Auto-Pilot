#!/usr/bin/env python3
"""
Update CarParams with proper vehicle geometry to fix ZeroDivisionError
"""
import sys
from pathlib import Path

# Add openpilot to path
openpilot_path = Path.home() / "openpilot"
sys.path.insert(0, str(openpilot_path))

from cereal import car
from openpilot.common.params import Params

# Create CarParams with proper vehicle geometry
CP = car.CarParams.new_message()
CP.carFingerprint = 'COMMA_BODY'
CP.notCar = True

# Safety configuration
CP.safetyConfigs = [car.CarParams.SafetyConfig.new_message()]
CP.safetyConfigs[0].safetyModel = car.CarParams.SafetyModel.noOutput

# Steering configuration for angle-based control
CP.steerControlType = car.CarParams.SteerControlType.angle
CP.minSteerSpeed = 0.0

# Lateral control tuning
CP.lateralTuning.init('pid')
CP.lateralTuning.pid.kpBP = [0.]
CP.lateralTuning.pid.kpV = [0.2]
CP.lateralTuning.pid.kiBP = [0.]
CP.lateralTuning.pid.kiV = [0.05]
CP.lateralTuning.pid.kf = 1.0

# CRITICAL: Vehicle geometry (prevents ZeroDivisionError)
# Using typical sedan dimensions
CP.wheelbase = 2.7  # meters (typical sedan)
CP.steerRatio = 15.0  # typical steering ratio
CP.centerToFront = CP.wheelbase * 0.45  # 45% weight distribution

# Tire stiffness (prevent division by zero)
CP.lateralParams.torqueBP = [0.]
CP.lateralParams.torqueV = [0.]

CP.mass = 1500  # kg (typical sedan)

# Save to params
params = Params()
cp_bytes = CP.to_bytes()
params.put('CarParams', cp_bytes)
params.put('CarParamsCache', cp_bytes)
params.put('CarParamsPersistent', cp_bytes)

print(f'✓ CarParams updated with vehicle geometry: {len(cp_bytes)} bytes')
print(f'  Fingerprint: {CP.carFingerprint}')
print(f'  Wheelbase: {CP.wheelbase}m')
print(f'  SteerRatio: {CP.steerRatio}')
print(f'  Mass: {CP.mass}kg')
