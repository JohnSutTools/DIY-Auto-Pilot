# Ubuntu Simulation - Quick Reference

## TL;DR - Three Commands to Test Everything

```bash
# 1. Setup (one time, 15-30 min)
./scripts/setup_system.sh

# 2. Run simulation test
chmod +x scripts/test_simulation.sh
./scripts/test_simulation.sh

# 3. Choose option 2 (full replay test)
# Watch the magic happen!
```

---

## What Gets Tested

✅ **Openpilot** - Vision processing, lane detection, control  
✅ **Bridge** - Message subscription, PWM scaling  
✅ **Virtual Motor** - Command reception, direction control  
✅ **Integration** - Complete data flow, timing, stability  

---

## Testing Modes

### Mode 1: Manual Messages
You send fake steering commands to test bridge response.

```bash
# Terminal 1
python3 scripts/simulate.py

# Terminal 2
cd ~/openpilot
python3 -c "
import cereal.messaging as messaging
pm = messaging.PubMaster(['carControl'])
msg = messaging.new_message('carControl')
msg.carControl.actuators.steer = 0.5
pm.send('carControl', msg)
"
```

### Mode 2: Replay Test (Recommended)
Uses real openpilot recorded data - most realistic test.

```bash
./scripts/test_simulation.sh
# Select option 2
```

Output you'll see:
```
[openpilot] Frame 1234/5000
[bridge] 📡 Steer: +0.234 → PWM: +35
[bridge] 🔧 Motor: PWM= +35 Direction: RIGHT
[bridge] 📡 Steer: -0.123 → PWM: -18
[bridge] 🔧 Motor: PWM= -18 Direction: LEFT
```

### Mode 3: Custom Route
Test with specific openpilot routes from comma.ai.

---

## Success Criteria

After simulation test passes:

- ✅ No Python errors or crashes
- ✅ Bridge receives steering commands continuously
- ✅ PWM scaling works correctly (steer × pwm_scale)
- ✅ Direction changes match input (positive = right, negative = left)
- ✅ Watchdog logic works (stops after 500ms timeout)
- ✅ Clean shutdown with Ctrl+C

---

## Troubleshooting

### "cereal module not found"
```bash
export PYTHONPATH="${PYTHONPATH}:$HOME/openpilot"
```

### "No steering commands"
Check replay is running:
```bash
# Should see frames incrementing
cd ~/openpilot
tools/replay/replay '<route>|0'
```

### "Route not found"
Download first:
```bash
cd ~/openpilot
tools/replay/route_downloader.py '<route-name>'
```

---

## Next Steps After Simulation

1. ✅ Simulation passes → Test with real ESP32
2. ✅ ESP32 responds → Add motor (bench test)
3. ✅ Motor works → Test in parked car
4. ✅ Parked test good → Low-speed lot test
5. ✅ All tests pass → Supervised road test

---

## Full Documentation

See [`docs/TESTING.md`](../docs/TESTING.md) for complete testing guide with:
- Detailed step-by-step instructions
- 5 levels of testing
- Troubleshooting for every issue
- Hardware integration steps
- Vehicle testing procedures
