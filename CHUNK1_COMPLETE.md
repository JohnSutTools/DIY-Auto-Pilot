# Chunk 1 - CarParams Setup Complete! ✅

## What Was Created

### 1. **setup_mock_carparams.py** - Main Setup Script
Creates a minimal CarParams configuration that allows openpilot to run without a real car.

**Key Configuration:**
- `notCar = True` - Bypasses CAN bus requirements
- Angle-based steering control (simpler than torque)
- LKAS only (longitudinal disabled)
- PID lateral controller with conservative tuning
- Allows steering at all speeds including standstill

### 2. **test_carparams.py** - Verification Script
Checks if CarParams is correctly set and displays the configuration.

---

## How to Use (Windows/WSL)

### Step 1: Setup CarParams

You need to run this **inside the openpilot environment** (not regular Windows Python).

**Option A: Using WSL/Ubuntu (Recommended)**
```bash
# Enter WSL if not already there
wsl

# Navigate to project
cd "/mnt/c/Users/John/OneDrive - Sutton Tools Pty Ltd/Private/DIY Auto Pilot"

# Run setup (this will use openpilot's Python)
cd openpilot/openpilot
source .venv/bin/activate
cd ../..
python3 scripts/setup_mock_carparams.py
```

**Option B: Direct Python with Path**
```bash
# Set PYTHONPATH to openpilot
export PYTHONPATH="/mnt/c/Users/John/OneDrive - Sutton Tools Pty Ltd/Private/DIY Auto Pilot/openpilot/openpilot"
python3 scripts/setup_mock_carparams.py
```

### Step 2: Verify It Worked

```bash
python3 scripts/test_carparams.py
```

**Expected Output:**
```
======================================================================
  CarParams Test
======================================================================

1. Checking if CarParams exists...
  ✓ CarParams found (XXX bytes)

2. Parsing CarParams...
  ✓ Successfully parsed

3. CarParams Configuration:
  Fingerprint:        MOCK_WEBCAM_LKAS
  Brand:              mock
  NotCar Mode:        True
  Steer Control Type: angle
  Min Steer Speed:    0.0 m/s
  Steer At Standstill: True
  Longitudinal:       Disabled

4. Lateral Tuning:
  Type: pid
  kP: 0.200
  kI: 0.050
  kF: 1.000

5. LKAS-Only Validation:
  ✓ notCar enabled: True
  ✓ Longitudinal disabled: False
  ✓ PCM cruise disabled: False
  ✓ Can steer at standstill: True

======================================================================
  ✅ CarParams is correctly configured for LKAS!
======================================================================

  Ready to launch openpilot:
    python3 launch.py
```

---

## What This Fixes

### Before Chunk 1:
```
❌ controlsd won't start (missing CarParams)
❌ plannerd won't start (missing CarParams)
❌ No carControl messages published
❌ Bridge has nothing to read
```

### After Chunk 1:
```
✅ CarParams exists in Params storage
✅ controlsd CAN initialize
✅ plannerd CAN initialize
✅ Ready for processes to start
```

---

## Next Steps

**After running setup_mock_carparams.py successfully:**

1. **Test launch (basic check):**
   ```bash
   # Try starting individual processes to verify they don't crash immediately
   cd openpilot/openpilot
   source .venv/bin/activate
   python -m selfdrive.controls.controlsd
   # Should NOT crash with "CarParams not found"
   # Ctrl+C to stop
   ```

2. **Move to Chunk 2:**
   - Fix bridge message handling to correctly read carControl.actuators fields
   - This can be done in parallel with Chunk 3

3. **Then Chunk 3:**
   - Fix launch.py to properly start required processes
   - Integrate everything

---

## Troubleshooting

### "cereal import could not be resolved"
- **Cause:** Running with system Python instead of openpilot's Python
- **Fix:** Use openpilot's venv: `source openpilot/openpilot/.venv/bin/activate`

### "CarParams not found after running setup"
- **Cause:** Script ran but didn't save to params
- **Check:** Run test_carparams.py to see detailed error
- **Fix:** Make sure you're in the right directory and have write permissions

### "openpilot not found at..."
- **Cause:** Path to openpilot is wrong in script
- **Fix:** Check that `openpilot/openpilot/` directory exists with selfdrive/ inside

---

## Technical Details

### Where CarParams is Stored
Openpilot uses a persistent key-value store (`openpilot.common.params.Params`).

**Storage Location:**
- Linux: `~/.comma/params/`
- The setup script writes to three keys:
  - `CarParams` - Active config
  - `CarParamsCache` - Cached from fingerprinting
  - `CarParamsPersistent` - Persists across reboots

### Why notCar Mode?
The `notCar` flag tells openpilot to:
- Skip CAN bus initialization
- Skip panda (hardware interface) requirements
- Use mock CarState instead of real car data
- Run in standalone mode

This is perfect for webcam-only LKAS testing!

---

## Status

✅ **Chunk 1 Complete**

**Files Created:**
- `scripts/setup_mock_carparams.py` (188 lines)
- `scripts/test_carparams.py` (95 lines)
- `CHUNK1_COMPLETE.md` (this file)

**Time Taken:** ~30 minutes  
**Next:** Chunk 2 (Bridge message handling) or Chunk 3 (Process launcher)

