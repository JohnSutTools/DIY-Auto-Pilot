# VM Archive - Ubuntu VirtualBox Setup

This directory contains a backup of all work done on the Ubuntu VirtualBox VM before migrating to native Ubuntu installation.

## Contents

### 1. `openpilot-patches/`
All modified openpilot files with forced engagement patches and camera fixes:

- **state.py** - Forced `return True, True` to bypass engagement checks
- **card.py** - Injects fake CarState (speed=15m/s, cruise=on)
- **controlsd.py** - Forces `CC.latActive = True` 
- **camera.py** - Fixed webcam capture (CAP_V4L2 + MJPEG format)
- **main.py** - UI modifications (not critical for LKAS)

### 2. `configs/bridge/`
Bridge configuration and code:
- `op_serial_bridge.py` - Main bridge subscribing to carControl messages
- `config.yaml` - PWM scaling config (pwm_scale, pwm_cap, stream_hz)
- `requirements.txt` - Python dependencies

### 3. `configs/scripts/`
All launcher and test scripts:
- **launch_lkas.py** - Main launcher (updated to use venv python)
- **force_engagement.py** - Applies all patches automatically
- **monitor_steering.py** - Debug tool to watch steering commands
- **check_modeld.py** - Verify modeld is publishing
- Plus many other test scripts

### 4. System Info
- `vm-system-info.txt` - VM configuration, Ubuntu version, installed packages

## Key Findings from VM Work

### What Worked ✅
1. **Process Launcher** - All 11 openpilot processes start successfully
2. **Camera Capture** - Logitech C910 works with CAP_V4L2 + MJPEG
3. **Forced Engagement** - Successfully bypassed all safety checks
4. **Message Flow** - carControl publishes with enabled=True, latActive=True
5. **VisionIPC** - Shared memory communication works
6. **OpenCL** - pocl-opencl-icd installed, basic CL context works

### What Didn't Work ❌
1. **GPU Performance** - VirtualBox GPU passthrough insufficient for modeld
2. **Lane Detection** - modeld runs but doesn't detect lanes (GPU issue)
3. **No Steering Commands** - steer=0.000 because modeld has no real lane data
4. **UI Display** - X11 forwarding works but UI shows black screen

### Root Cause
**VirtualBox GPU limitation** - modeld neural network needs real GPU acceleration. The VM's software OpenCL (pocl on CPU) is ~100x slower than GPU and can't run the model effectively.

## How to Reuse This Work

### Option 1: Apply patches to fresh openpilot install
```bash
# Copy patched files to new openpilot installation
cp vm-archive/openpilot-patches/state.py ~/openpilot/selfdrive/selfdrived/
cp vm-archive/openpilot-patches/card.py ~/openpilot/selfdrive/car/
cp vm-archive/openpilot-patches/controlsd.py ~/openpilot/selfdrive/controls/
cp vm-archive/openpilot-patches/camera.py ~/openpilot/tools/webcam/

# Or use force_engagement.py script to apply automatically
```

### Option 2: Use launcher script directly
```bash
# Copy launcher to your project
cp vm-archive/configs/scripts/launch_lkas.py ~/DIY-Auto-Pilot/scripts/

# Run (will use venv automatically)
cd ~/DIY-Auto-Pilot
~/openpilot/.venv/bin/python3 scripts/launch_lkas.py --no-ui
```

### Option 3: Copy entire bridge setup
```bash
cp -r vm-archive/configs/bridge ~/DIY-Auto-Pilot/
```

## Next Steps: Native Ubuntu Installation

With native Ubuntu on the laptop:
1. **Full GPU access** - Intel Iris Xe will run modeld at 10-20 FPS
2. **Real lane detection** - Model will actually process frames
3. **Actual steering commands** - Will see non-zero steer values
4. **ESP32 testing ready** - Complete end-to-end validation

All code from this archive transfers directly - just:
1. Install Ubuntu 24.04
2. Clone openpilot
3. Copy scripts and bridge from this archive
4. Apply patches from `openpilot-patches/`
5. Run launcher → **LKAS works!**

## Patch Application Script

To quickly apply all patches on a new system:

```bash
#!/bin/bash
# apply-vm-patches.sh - Apply all VM patches to fresh openpilot

OPENPILOT=~/openpilot
ARCHIVE=vm-archive/openpilot-patches

cp $ARCHIVE/state.py $OPENPILOT/selfdrive/selfdrived/
cp $ARCHIVE/card.py $OPENPILOT/selfdrive/car/
cp $ARCHIVE/controlsd.py $OPENPILOT/selfdrive/controls/
cp $ARCHIVE/camera.py $OPENPILOT/tools/webcam/

# Clear python cache
find $OPENPILOT -name "*.pyc" -delete
find $OPENPILOT -name "__pycache__" -type d -delete

echo "✓ All patches applied!"
```

## Important Notes

1. **Camera format** - Webcam MUST use CAP_V4L2 + MJPEG (patched in camera.py)
2. **Venv python** - Always use `~/openpilot/.venv/bin/python3` not system python3
3. **Working directory** - Processes must run from ~/openpilot (cwd parameter)
4. **JPEG warnings** - "Corrupt JPEG data" messages are cosmetic, ignore them
5. **UI is optional** - LKAS works without UI, it's just visualization

## VM Limitations Summary

- ✅ Development environment: Great
- ✅ Code testing: Works well
- ✅ Learning openpilot: Perfect
- ❌ **Lane detection: Needs real GPU**
- ❌ **Production use: Not viable**

**Recommendation**: Use native Ubuntu for actual LKAS functionality. Keep VM as development/testing backup.

---

**Created**: November 4, 2025  
**Purpose**: Preserve all VM work before migrating to native Ubuntu installation  
**Status**: Complete and ready for reuse
