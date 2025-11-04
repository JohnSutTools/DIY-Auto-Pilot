# Quick Test Commands for WSL

## One-Line Test Command

Open WSL and paste this complete command:

```bash
cd "/mnt/c/Users/John/OneDrive - Sutton Tools Pty Ltd/Private/DIY Auto Pilot" && chmod +x scripts/test_chunk1.sh && bash scripts/test_chunk1.sh
```

---

## Step-by-Step (if one-liner doesn't work)

```bash
# 1. Open WSL
wsl

# 2. Go to project
cd "/mnt/c/Users/John/OneDrive - Sutton Tools Pty Ltd/Private/DIY Auto Pilot"

# 3. Make script executable
chmod +x scripts/test_chunk1.sh

# 4. Run tests
bash scripts/test_chunk1.sh
```

---

## If Openpilot Not Built Yet

```bash
# Navigate to openpilot
cd "/mnt/c/Users/John/OneDrive - Sutton Tools Pty Ltd/Private/DIY Auto Pilot/openpilot/openpilot"

# Build openpilot (10-30 minutes, one time only)
scons -j4

# Then run tests
cd ../..
bash scripts/test_chunk1.sh
```

---

## Quick Status Check (before running full tests)

```bash
# Check if openpilot is ready
cd "/mnt/c/Users/John/OneDrive - Sutton Tools Pty Ltd/Private/DIY Auto Pilot/openpilot/openpilot"

# This should show Python environment info
source .venv/bin/activate && python3 --version

# This should NOT error
python3 -c "from cereal import car; print('✓ cereal works')"

# If both work, you're ready for tests!
```

---

## After Tests Pass

Once you see "✅ All tests PASSED!", report back and we'll move to Chunk 2 (bridge message fix).
