# Openpilot LKAS Integration - Gap Analysis & Implementation Plan

**Date:** 2025-11-04  
**Status:** Current implementation is a mock/simulation - not connected to real openpilot

---

## Executive Summary

**Current State:** The project has scaffolding and demo code, but is **NOT** using real openpilot LKAS. The bridge and launcher are set up to work with openpilot, but critical pieces are missing.

**Root Issue:** Missing CarParams initialization - openpilot's entire control stack depends on CarParams being set, which requires either:
1. A real car (CAN bus connection via panda)
2. Mock/notCar mode setup

**Gap:** ~60% implementation complete. Need 3-4 major work chunks to get real LKAS running.

---

## Understanding Real Openpilot LKAS Architecture

### The Control Flow (What SHOULD Happen)

```
1. CAMERA CAPTURE
   webcamerad (USE_WEBCAM=1) → roadCameraState messages
   ↓

2. VISION MODEL
   modeld → modelV2 messages (lane lines, path prediction)
   ↓

3. PLANNING
   plannerd → longitudinalPlan (speed planning)
            → driverAssistance (lane departure warnings)
   ↓

4. CONTROL (THE KEY STEP)
   controlsd → carControl messages
            ├─ carControl.actuators.steer (-1.0 to +1.0)
            ├─ carControl.actuators.steeringAngleDeg
            └─ carControl.latActive (bool - is lateral control active)
            
   controlsd → controlsState messages  
            ├─ controlsState.lateralControlState.*
            └─ controlsState.curvature
   ↓

5. YOUR BRIDGE (Existing)
   op_serial_bridge.py → subscribes to carControl + controlsState
                      → extracts steer command
                      → sends to ESP32
```

### Critical Dependencies

**For controlsd to run and publish carControl messages:**

1. **CarParams MUST exist** - stored in Params("CarParams")
   - Defines car capabilities, steering limits, control type
   - Normally created by `card.py` after fingerprinting real car CAN messages
   - **Without this, controlsd won't start**

2. **Required Message Inputs to controlsd:**
   - `modelV2` (from modeld)
   - `carState` (from card.py - car interface)
   - `longitudinalPlan` (from plannerd)
   - `selfdriveState` (from selfdrived.py - state machine)

3. **Process Dependencies:**
   ```
   card.py ────────> CarParams (creates/caches)
      ↓                  ↓
   carState         selfdrived
      ↓                  ↓
   plannerd ──────> controlsd ──────> carControl (THIS IS WHAT YOU NEED)
      ↑
   modelV2 (from modeld)
   ```

---

## Current Implementation Analysis

### What EXISTS and Works ✅

1. **Bridge Structure** (`bridge/op_serial_bridge.py`)
   - ✅ Subscribes to `carControl` and `controlsState` via cereal.messaging
   - ✅ Serial communication to ESP32 (S:<pwm> protocol)
   - ✅ PWM scaling and safety limits
   - ✅ Mock mode for testing without hardware

2. **Launcher** (`launch.py`)
   - ✅ Finds openpilot installation
   - ✅ Sets PYTHONPATH correctly
   - ✅ Process management and monitoring
   - ✅ Uses openpilot's venv Python

3. **ESP32 Firmware** (`firmware/steering_motor/`)
   - ✅ Ready to receive S:<pwm> commands
   - ✅ BTS7960 PWM control

4. **Openpilot Clone**
   - ✅ Full openpilot codebase present at `openpilot/openpilot/`

### What's BROKEN/MISSING ❌

1. **CarParams Not Created** ❌❌❌ **CRITICAL BLOCKER**
   - controlsd requires CarParams to initialize
   - plannerd requires CarParams 
   - card.py expects CAN messages from panda (hardware dongle)
   - **Current code tries to launch openpilot with launch_openpilot.sh but this expects a car**

2. **Process Launcher Wrong** ❌
   - `launch.py` calls `launch_openpilot.sh` - this is the FULL openpilot system
   - Needs manager.py + correct process filtering
   - Missing: selective process startup (only webcam + LKAS processes)

3. **Bridge Message Handling Incomplete** ⚠️
   - Subscribes to right messages BUT...
   - `carControl.actuators.torque` might not exist (depends on car control type)
   - Should use `carControl.actuators.steer` or `steeringAngleDeg`
   - Needs validation against actual capnp schema

4. **No Mock/NotCar Mode Setup** ❌
   - Openpilot has `notCar` mode for testing without a vehicle
   - Needs CarParams with `notCar=True` flag
   - Would bypass car interface requirements

5. **Missing Processes** ❌
   - No selfdrived.py startup (state machine)
   - No card.py mock/bypass
   - No proper process dependency ordering

---

## Implementation Plan - Chunked Approach

### **CHUNK 1: CarParams Bootstrap (HIGHEST PRIORITY)**
**Goal:** Create minimal CarParams so controlsd can start  
**Effort:** 2-3 hours  
**Files to Create/Modify:**
- `scripts/setup_mock_carparams.py` (NEW)
- `launch.py` (MODIFY)

**What to Do:**
```python
# Create a minimal CarParams for webcam-only LKAS
from cereal import car
from openpilot.common.params import Params

CP = car.CarParams.new_message()
CP.carFingerprint = "MOCK_WEBCAM_LKAS"
CP.brand = "mock"
CP.notCar = True  # CRITICAL FLAG

# Steering params (conservative for safety)
CP.steerControlType = car.CarParams.SteerControlType.angle
CP.steerMaxBP = [0.]
CP.steerMaxV = [1.0]  # Max steer command
CP.minSteerSpeed = 0.0  # Allow steering at standstill

# Lateral tuning (PID for simplicity)
CP.lateralTuning.init('pid')
CP.lateralTuning.pid.kpBP = [0.]
CP.lateralTuning.pid.kpV = [0.1]
CP.lateralTuning.pid.kiBP = [0.]
CP.lateralTuning.pid.kiV = [0.01]

# Disable longitudinal (LKAS only!)
CP.openpilotLongitudinalControl = False
CP.pcmCruise = False

# Save to params
params = Params()
params.put("CarParams", CP.to_bytes())
params.put("CarParamsPersistent", CP.to_bytes())
```

**Success Criteria:**
- `params.get("CarParams")` returns valid data
- controlsd can initialize without crashing

---

### **CHUNK 2: Fix Bridge Message Handling**
**Goal:** Correctly extract steering from real openpilot messages  
**Effort:** 1-2 hours  
**Files to Modify:**
- `bridge/op_serial_bridge.py`

**What's Wrong:**
```python
# CURRENT CODE (line 168):
if hasattr(cc.actuators, 'torque'):
    return float(cc.actuators.torque)
```

**Problem:** `actuators.torque` is for torque-based steering (direct motor torque). For angle-based control, use `steeringAngleDeg` or the `steer` field might not exist in this form.

**What to Fix:**
```python
def _get_steer_command(self) -> Optional[float]:
    """Extract steering command from openpilot messages"""
    self.sm.update(0)
    
    # Priority 1: carControl.actuators (the actuator command)
    if self.sm.updated['carControl']:
        cc = self.sm['carControl']
        if hasattr(cc, 'latActive') and cc.latActive:  # Only if lateral control is active
            if hasattr(cc.actuators, 'steeringAngleDeg'):
                # Angle-based control - normalize to -1..+1
                # Assume max steering angle is ~180 degrees
                return float(cc.actuators.steeringAngleDeg) / 180.0
            elif hasattr(cc.actuators, 'steer'):
                # Some configs use 'steer' directly (normalized already)
                return float(cc.actuators.steer)
            elif hasattr(cc.actuators, 'torque'):
                # Torque-based (fallback)
                return float(cc.actuators.torque)
    
    # Priority 2: controlsState (desired curvature can derive steering)
    if self.sm.updated['controlsState']:
        cs = self.sm['controlsState']
        # curvature can be converted to steering angle
        # This is a fallback path
        if hasattr(cs, 'desiredCurvature'):
            # Simple linear approximation (tune based on testing)
            return float(cs.desiredCurvature) * 10.0  # Scale factor TBD
    
    return None
```

**Success Criteria:**
- Bridge receives non-zero steer commands when openpilot is active
- Values are in expected range (-1.0 to +1.0)

---

### **CHUNK 3: Proper Process Launcher**
**Goal:** Start only required openpilot processes for LKAS  
**Effort:** 3-4 hours  
**Files to Modify:**
- `launch.py` (major rewrite)
- Create `scripts/minimal_lkas_manager.py` (NEW)

**What to Launch:**
```
Required Processes for LKAS:
1. webcamerad (camera capture)
2. modeld (vision model)
3. selfdrived (state machine)
4. plannerd (lateral planning)
5. controlsd (control loop - publishes carControl)

Optional but Recommended:
6. calibrationd (camera calibration)
7. locationd (position estimation)
8. paramsd (vehicle parameters)

NOT Needed:
- card.py (replaced by mock CarParams)
- pandad (no panda hardware)
- radard (no radar)
- ui, soundd (no display needed)
```

**Implementation Approach:**

Option A: **Use manager.py with process filtering**
```python
# In launch.py
import os
os.environ['USE_WEBCAM'] = '1'
os.environ['BLOCK'] = 'card,pandad,radard,ui,soundd'  # Block unneeded processes

# Start manager
subprocess.Popen([
    str(openpilot_path / "system" / "manager" / "manager.py")
], env=env)
```

Option B: **Manual process startup** (more control)
```python
# Start each process individually
processes = [
    ("webcamerad", "tools.webcam.camerad"),
    ("modeld", "selfdrive.modeld.modeld"),
    ("selfdrived", "selfdrive.selfdrived.selfdrived"),
    ("plannerd", "selfdrive.controls.plannerd"),
    ("controlsd", "selfdrive.controls.controlsd"),
]

for name, module in processes:
    proc = subprocess.Popen(
        [python, "-m", module],
        cwd=openpilot_path,
        env=env
    )
    processes_list.append((name, proc))
```

**Success Criteria:**
- All required processes start without crashing
- `cereal.messaging` pipes work between processes
- controlsd publishes carControl messages

---

### **CHUNK 4: End-to-End Testing & Tuning**
**Goal:** Validate full pipeline and tune parameters  
**Effort:** 2-4 hours (iterative)  
**Tasks:**

1. **Message Flow Validation**
   ```bash
   # Monitor messages with cereal tools
   python -m tools.replay.replay --data-dir /tmp
   # Or use messaging tool to see live messages
   ```

2. **Bridge Testing**
   - Run bridge in debug mode
   - Verify steer commands are received
   - Check PWM scaling is correct
   - Test with webcam showing lane lines

3. **Parameter Tuning**
   - Adjust `pwm_scale` in config.yaml
   - Tune `pwm_cap` for safety limits
   - Verify motor response matches steering intent

4. **Safety Validation**
   - Test emergency stop
   - Verify watchdog timeout on ESP32
   - Confirm PWM limits enforced

**Success Criteria:**
- Webcam → openpilot → bridge → ESP32 → motor (complete flow works)
- Steering responds to lane detection
- Safe failure modes tested

---

## Quick Reference: Key Files & Their Roles

| File | Purpose | Status |
|------|---------|--------|
| `openpilot/selfdrive/controls/controlsd.py` | Main control loop, publishes carControl | Exists (needs CarParams) |
| `openpilot/selfdrive/controls/plannerd.py` | Lateral path planning | Exists (needs CarParams) |
| `openpilot/selfdrive/modeld/modeld.py` | Vision model (lane detection) | Exists |
| `openpilot/selfdrive/selfdrived/selfdrived.py` | State machine (enable/disable logic) | Exists |
| `openpilot/cereal/log.capnp` | Message definitions | Reference for correct field names |
| `bridge/op_serial_bridge.py` | Your bridge to ESP32 | Needs message handling fix |
| `launch.py` | System launcher | Needs process management rewrite |
| `scripts/setup_mock_carparams.py` | **TO CREATE** | Bootstrap CarParams |

---

## Priority Order for Implementation

1. **🔴 CHUNK 1 - CarParams** (BLOCKER - do this first!)
2. **🟡 CHUNK 2 - Bridge Messages** (can be done in parallel with #1)
3. **🟢 CHUNK 3 - Process Launcher** (depends on #1)
4. **🔵 CHUNK 4 - Testing** (final validation)

---

## Expected Outcome After All Chunks

```
[Webcam] → openpilot processes → carControl messages → bridge → ESP32 → Motor

✅ Real openpilot LKAS running
✅ No mock/fake models
✅ Actual lane detection driving steering
✅ Complete integration
```

---

## Questions & Answers

**Q: Why isn't the current code working?**  
A: It's trying to launch full openpilot which expects a car with CAN bus. Missing CarParams prevents controlsd from starting.

**Q: What's the fastest path to seeing it work?**  
A: Chunk 1 (CarParams) + Chunk 2 (message fix) + manually run processes. ~4-6 hours.

**Q: Can we skip CarParams?**  
A: No. It's the foundation of openpilot's architecture. Every process checks it.

**Q: Is the bridge code fundamentally wrong?**  
A: No, it's 80% correct. Just needs message field fixes (Chunk 2).

**Q: Why notCar mode?**  
A: Bypasses all car-specific interfaces (CAN, panda). Lets openpilot run standalone.

---

## Next Steps

1. Review this assessment
2. Choose: Do all 4 chunks sequentially, or pick quick-win subset?
3. Start with Chunk 1 (I can help write the CarParams setup script)
4. Test incrementally after each chunk

**Estimated Total Effort:** 8-13 hours for complete working system.

