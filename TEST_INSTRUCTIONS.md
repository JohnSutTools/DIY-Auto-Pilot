# Testing Chunk 1 in WSL

## Quick Test Instructions

### Step 1: Open WSL Terminal

In PowerShell or Windows Terminal:
```powershell
wsl
```

### Step 2: Navigate to Project

```bash
cd "/mnt/c/Users/John/OneDrive - Sutton Tools Pty Ltd/Private/DIY Auto Pilot"
```

### Step 3: Make Test Script Executable

```bash
chmod +x scripts/test_chunk1.sh
```

### Step 4: Run Complete Test Suite

```bash
bash scripts/test_chunk1.sh
```

---

## What the Tests Check

The test suite runs 7 comprehensive tests:

1. **Directory Structure** - Verifies all files are in place
2. **Openpilot Installation** - Checks openpilot directories exist
3. **Python Environment** - Tests that cereal and Params can be imported
4. **CarParams Setup** - Runs setup_mock_carparams.py
5. **CarParams Verification** - Checks all three param keys are saved
6. **Test Script** - Runs test_carparams.py
7. **Controlsd Access** - Simulates how controlsd loads CarParams

---

## Expected Output

If everything works, you should see:

```
======================================================================
  Chunk 1 Test Suite - CarParams Setup
======================================================================

Test Environment:
  Script Dir:   /mnt/c/Users/John/.../scripts
  Project Root: /mnt/c/Users/John/.../DIY Auto Pilot
  User:         john
  OS:           Linux

======================================================================
Test 1: Directory Structure
======================================================================
✓ Openpilot directory exists
✓ setup_mock_carparams.py exists
✓ test_carparams.py exists

======================================================================
Test 2: Openpilot Installation
======================================================================
✓ selfdrive/ directory exists
✓ cereal/ directory exists
✓ Python venv exists

======================================================================
Test 3: Python Environment
======================================================================
✓ Can import cereal module
✓ Can import Params module

======================================================================
Test 4: CarParams Setup
======================================================================
Clearing existing CarParams (if any)...
Running setup_mock_carparams.py...

Creating Mock CarParams for Webcam LKAS...
  ✓ Set notCar mode
  ✓ Configured angle-based steering
  ✓ Set lateral PID tuning
  ✓ Disabled longitudinal control (LKAS only)
  ✓ Set speed limits
  ✓ Set safety configuration
  ✓ Set vehicle geometry
  ✓ Saved to Params storage

✅ Mock CarParams created successfully!
✓ setup_mock_carparams.py executed successfully

======================================================================
Test 5: CarParams Verification
======================================================================
✓ CarParams: 1234 bytes
✓ CarParamsCache: 1234 bytes
✓ CarParamsPersistent: 1234 bytes

✓ Parsed CarParams successfully
  - Fingerprint: MOCK_WEBCAM_LKAS
  - Brand: mock
  - notCar: True

✓ All critical fields validated
✓ CarParams verification completed

======================================================================
Test 6: Run test_carparams.py
======================================================================
[... test_carparams.py output ...]
✓ test_carparams.py executed successfully

======================================================================
Test 7: Controlsd CarParams Access
======================================================================
✓ CarParams accessible with block=False
✓ Successfully loaded with messaging.log_from_bytes
  - Car fingerprint: MOCK_WEBCAM_LKAS
  - Steering type: angle

✓ Simulated controlsd CarParams access successful
✓ Controlsd can access CarParams

======================================================================
  Test Results Summary
======================================================================

✅ All tests PASSED!

Chunk 1 is working correctly. Key achievements:
  ✓ CarParams created and saved
  ✓ notCar mode enabled
  ✓ LKAS-only configuration set
  ✓ Accessible by openpilot processes

======================================================================
  Ready for Chunk 2!
======================================================================

Next steps:
  1. Fix bridge message handling (Chunk 2)
  2. Update process launcher (Chunk 3)
  3. Full system test (Chunk 4)
```

---

## Troubleshooting

### "openpilot venv NOT found"

**Problem:** Openpilot hasn't been built yet.

**Solution:**
```bash
cd openpilot/openpilot
# Install dependencies first (if not done)
./install_ubuntu_dependencies.sh

# Build openpilot (takes 10-30 minutes)
scons -j4
```

### "Cannot import cereal module"

**Problem:** Cereal bindings not compiled.

**Solution:**
```bash
cd openpilot/openpilot
source .venv/bin/activate
pip install -e .
```

### "Permission denied" when running test

**Problem:** Script not executable.

**Solution:**
```bash
chmod +x scripts/test_chunk1.sh
```

### Test fails at Python imports

**Problem:** Running from wrong directory.

**Solution:** Make sure you're in the project root:
```bash
cd "/mnt/c/Users/John/OneDrive - Sutton Tools Pty Ltd/Private/DIY Auto Pilot"
pwd  # Should show the project root
bash scripts/test_chunk1.sh
```

---

## If Tests Fail

1. **Read the error output carefully** - It will show which test failed
2. **Check the specific error message** - Often gives the exact issue
3. **Run individual components**:
   ```bash
   # Test just the setup
   cd openpilot/openpilot
   source .venv/bin/activate
   cd ../..
   python3 scripts/setup_mock_carparams.py
   
   # Test just the verification
   python3 scripts/test_carparams.py
   ```

---

## Manual Verification (if automated tests fail)

If the automated test has issues, you can manually verify:

```bash
cd openpilot/openpilot
source .venv/bin/activate
cd ../..

# Check if CarParams exists
python3 << 'EOF'
from openpilot.common.params import Params
p = Params()
cp = p.get("CarParams")
print(f"CarParams exists: {cp is not None}")
if cp:
    print(f"Size: {len(cp)} bytes")
EOF
```

---

## Success Criteria

Tests pass when:
- ✅ All 7 tests show green checkmarks
- ✅ No error messages
- ✅ Final message says "All tests PASSED!"
- ✅ Shows "Ready for Chunk 2!"

If you see this, Chunk 1 is complete and working! 🎉

