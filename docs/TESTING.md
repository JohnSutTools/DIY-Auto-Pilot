# Testing in Ubuntu - Complete Simulation Guide

This guide walks you through testing your entire system in Ubuntu **without any hardware** using openpilot's replay functionality.

## Testing Levels

```
Level 1: Unit Tests (no openpilot needed)
Level 2: Bridge Simulation (openpilot + virtual motor)
Level 3: Full System Test (openpilot + bridge + virtual motor)
Level 4: Hardware Test (add real ESP32)
Level 5: Vehicle Test (full system in car)
```

---

## Prerequisites

```bash
# Ensure setup is complete
cd ~/steering-actuator
./scripts/setup_system.sh
```

---

## Level 1: Unit Tests (No Openpilot)

### Test 1.1: Configuration Loading

```bash
# Test config parsing
python3 -c "
import yaml
with open('bridge/config.yaml') as f:
    config = yaml.safe_load(f)
print('✓ Config loaded:', config)
"
```

### Test 1.2: Serial Protocol Validation

```bash
# Test command formatting
python3 -c "
def format_command(pwm):
    return f'S:{pwm:+d}\n'

print('Commands:')
print('  ', format_command(100))
print('  ', format_command(-50))
print('  ', 'STOP\n')
"
```

Expected output:
```
Commands:
   S:+100
   S:-50
   STOP
```

---

## Level 2: Bridge Simulation (Virtual Motor)

### Step 1: Start Simulated Bridge

```bash
# Terminal 1: Run simulated bridge
cd ~/steering-actuator
python3 scripts/simulate.py --config bridge/config.yaml
```

You should see:
```
🎮 Simulation mode - Virtual ESP32 ready
📊 PWM scale: 150, cap: 255
🚀 Simulation running - waiting for openpilot messages...
⏳ Waiting for openpilot messages...
```

### Step 2: Send Test Messages

```bash
# Terminal 2: Send fake steering commands
cd ~/openpilot
python3 << 'EOF'
import cereal.messaging as messaging
import time

pm = messaging.PubMaster(['carControl'])

print("Sending test steering commands...")
for i in range(10):
    # Create message
    msg = messaging.new_message('carControl')
    msg.carControl.enabled = True
    msg.carControl.actuators.steer = 0.5 if i % 2 == 0 else -0.5
    
    pm.send('carControl', msg)
    print(f"Sent steer: {msg.carControl.actuators.steer:+.1f}")
    time.sleep(0.5)
EOF
```

In Terminal 1, you should see:
```
📡 Steer command: +0.500 → PWM: +75
🔧 Motor: PWM= +75 Direction: RIGHT (clockwise)
📡 Steer command: -0.500 → PWM: -75
🔧 Motor: PWM= -75 Direction: LEFT (counter-clockwise)
...
```

---

## Level 3: Full Openpilot Replay Test

This is the **most important test** - it uses real openpilot data.

### Step 1: Get Openpilot Test Data

```bash
# Download a sample route
cd ~/openpilot

# Option A: Use built-in demo route
tools/replay/route_downloader.py '4cf7a6ad03080c90|2021-09-29--13-46-36'

# Option B: List available demo routes
ls tools/replay/test_routes/
```

### Step 2: Run Full System Simulation

```bash
# Terminal 1: Replay openpilot route
cd ~/openpilot
tools/replay/replay '4cf7a6ad03080c90|2021-09-29--13-46-36|0'
```

```bash
# Terminal 2: Run simulated bridge
cd ~/steering-actuator
python3 scripts/simulate.py --config bridge/config.yaml
```

### Expected Output

**Terminal 1 (Replay):**
```
Loading route: 4cf7a6ad03080c90|2021-09-29--13-46-36|0
Playing route at 1.0x speed
Frame: 1234/5000
Publishing: carControl, controlsState, ...
```

**Terminal 2 (Bridge):**
```
📡 Steer command: +0.123 → PWM: +18
🔧 Motor: PWM= +18 Direction: RIGHT (clockwise)
📡 Steer command: +0.089 → PWM: +13
🔧 Motor: PWM= +13 Direction: RIGHT (clockwise)
📡 Steer command: -0.045 → PWM:  -7
🔧 Motor: PWM=  -7 Direction: LEFT (counter-clockwise)
...
```

**✓ Success Criteria:**
- Bridge receives steering commands continuously
- PWM values scale correctly (steer * pwm_scale)
- Direction changes match steering input
- No errors or crashes

---

## Level 4: Test with Real ESP32

Now add real hardware to the mix.

### Step 1: Connect ESP32

```bash
# Flash firmware first
# (Use Arduino IDE to upload firmware/steering_motor/steering_motor.ino)

# Find device
ls /dev/ttyUSB*
# Example: /dev/ttyUSB0

# Update config
nano bridge/config.yaml
# Change serial_port to your device
```

### Step 2: Test ESP32 Standalone

```bash
python3 scripts/test_esp32.py --port /dev/ttyUSB0 --interactive
```

Verify all tests pass.

### Step 3: Run Full System with Real ESP32

```bash
# Terminal 1: Replay openpilot
cd ~/openpilot
tools/replay/replay '4cf7a6ad03080c90|2021-09-29--13-46-36|0'
```

```bash
# Terminal 2: Run REAL bridge (not simulated)
cd ~/steering-actuator
python3 bridge/op_serial_bridge.py --debug --config bridge/config.yaml
```

**Expected Output:**
```
Bridge initialized: /dev/ttyUSB0 @ 115200
ESP32: ESP32-S3 Steering Controller Ready
Steer: +0.234 -> PWM: +35
Sent: S:+35
Steer: -0.123 -> PWM: -18
Sent: S:-18
```

**✓ Success Criteria:**
- ESP32 connects successfully
- Motor responds to steering commands
- No serial errors or timeouts
- Watchdog doesn't trigger

---

## Level 5: Test with Webcam (No Car)

Test openpilot's vision system with a webcam pointed at a road image.

### Step 1: Setup Test Environment

```bash
# Check webcam
v4l2-ctl --list-devices
# Should show /dev/video0 or similar

# Test webcam feed
ffplay /dev/video0
# Press Q to quit
```

### Step 2: Create Test Scenario

```bash
# Download or print an image of a road with lane lines
# Or use a video on your monitor
# Point webcam at the image
```

### Step 3: Run Full System

```bash
cd ~/steering-actuator
python3 launch.py
```

**Expected Output:**
```
========================================
Openpilot Steering Actuator System
========================================

🚗 Starting openpilot...
✓ Openpilot started

🔌 Starting steering bridge...
✓ Bridge started

========================================
System running - Press Ctrl+C to stop
========================================

[openpilot] Webcam initialized: /dev/video0
[openpilot] Lane detection: 2 lanes found
[openpilot] LKAS engaged
[bridge] Steer: +0.123 -> PWM: +18
[bridge] Motor responding
```

**✓ Success Criteria:**
- Webcam detected and initialized
- Lane detection activates
- Steering commands generated
- Motor responds to detected lanes
- System runs without errors

---

## Common Issues & Solutions

### Issue: "cereal module not found"

```bash
# Add openpilot to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$HOME/openpilot"

# Or add to ~/.bashrc permanently
echo 'export PYTHONPATH="${PYTHONPATH}:$HOME/openpilot"' >> ~/.bashrc
source ~/.bashrc
```

### Issue: "No steering commands received"

**Check 1:** Is replay running?
```bash
# In replay terminal, verify it's playing
# Should see "Frame: X/Y" incrementing
```

**Check 2:** Are messages being published?
```bash
cd ~/openpilot
python3 -c "
import cereal.messaging as messaging
sm = messaging.SubMaster(['carControl'])
import time
for i in range(10):
    sm.update()
    if sm.updated['carControl']:
        print(f'✓ Received carControl: {sm[\"carControl\"]}')
    time.sleep(0.5)
"
```

### Issue: "Replay route not found"

```bash
# Download route first
cd ~/openpilot
tools/replay/route_downloader.py '<route-name>'

# Or use a different route
# Browse routes at: https://comma.ai/explore
```

### Issue: "Webcam not detected"

```bash
# Check permissions
ls -l /dev/video*
sudo usermod -a -G video $USER
# Log out and back in

# Test camera
ffplay /dev/video0
# If works, openpilot should detect it
```

### Issue: "Motor doesn't respond to replay"

**Verify:**
1. Replay is sending carControl messages ✓
2. Bridge is receiving them ✓
3. Bridge is scaling correctly ✓
4. ESP32 is connected ✓
5. Motor has power ✓

```bash
# Debug bridge
python3 bridge/op_serial_bridge.py --debug --config bridge/config.yaml
# Should show every command sent
```

---

## Testing Checklist

Before moving to vehicle testing:

- [ ] Level 1: Unit tests pass
- [ ] Level 2: Simulated bridge receives messages
- [ ] Level 3: Replay works with simulation
- [ ] Level 4: Real ESP32 responds to replay
- [ ] Level 5: Webcam + full system works
- [ ] Configuration tuned (pwm_scale)
- [ ] No errors in any test
- [ ] System shutdown works cleanly (Ctrl+C)

---

## Next Steps

Once all simulation tests pass:

1. **Bench Test**: ESP32 + motor on workbench (no load)
2. **Mount Test**: Install in car, test with car off
3. **Parked Test**: Car on, parked, verify steering response
4. **Lot Test**: Empty parking lot, very low speed
5. **Road Test**: Quiet road with constant supervision

---

## Quick Test Script

Save this as `test_all.sh`:

```bash
#!/bin/bash
echo "Running all tests..."

echo "Test 1: Config loading..."
python3 -c "import yaml; yaml.safe_load(open('bridge/config.yaml'))" && echo "✓" || echo "✗"

echo "Test 2: Cereal import..."
python3 -c "import cereal.messaging" && echo "✓" || echo "✗"

echo "Test 3: Bridge import..."
python3 -c "import sys; sys.path.insert(0, 'bridge'); import op_serial_bridge" && echo "✓" || echo "✗"

echo "Test 4: Openpilot present..."
test -d ~/openpilot && echo "✓" || echo "✗"

echo "Test 5: Firmware present..."
test -f firmware/steering_motor/steering_motor.ino && echo "✓" || echo "✗"

echo "All basic tests complete!"
```

Run with: `chmod +x test_all.sh && ./test_all.sh`

---

**You're now ready to test the complete system in Ubuntu!** 🎉
