# Visual Simulation - See It Work Without Hardware!

**No ESP32? No motor? No problem!**

This guide shows you how to see the complete system working with a beautiful graphical interface - no hardware required.

---

## What You'll See

```
┌─────────────────────────────────────────────────────┐
│  🎮 Openpilot Steering Visualizer                   │
├─────────────────────────────────────────────────────┤
│                                                      │
│   ╔═══════════╗        ┌─────────────────────┐    │
│   ║   🎡      ║        │  Motor Command      │    │
│   ║  Steering ║        │  ▓▓▓▓▓▓░░░░░░░░░░  │    │
│   ║   Wheel   ║        │  PWM: +75           │    │
│   ║           ║        │  → CLOCKWISE        │    │
│   ╚═══════════╝        └─────────────────────┘    │
│   Angle: 45.3°                                     │
│                        Openpilot Command           │
│                        Steer: +0.500               │
│                                                     │
│   ┌────────────────────────────────────────────┐  │
│   │  Steering History                           │  │
│   │  ╱╲    ╱╲                                   │  │
│   │ ╱  ╲  ╱  ╲                                  │  │
│   │────────────────────────────                 │  │
│   │      ╲╱    ╲╱                               │  │
│   └────────────────────────────────────────────┘  │
│                                                     │
│  Messages: 1234  |  Rate: 20 Hz  |  ● RECEIVING   │
└─────────────────────────────────────────────────────┘
```

**Real-time display showing:**
- 🎡 Animated steering wheel that rotates
- 📊 Motor PWM bar (left/right direction)
- 📈 Live steering command graph
- 📡 Openpilot data stream
- ✅ Connection status

---

## Quick Start

### Step 1: Setup (If Not Done Already)

**On WSL Ubuntu:**
```bash
cd ~/steering-actuator
./scripts/setup_system.sh
```

### Step 2: Install Visualization Dependencies

```bash
pip3 install pygame pyyaml
```

### Step 3: Start Visualizer

```bash
cd ~/steering-actuator
python3 scripts/visualize.py
```

**You'll see a graphical window open with the steering interface!**

### Step 4: Feed It Data (Choose One)

**Option A: Use Demo Route (Recommended)**

In another terminal:
```bash
cd ~/openpilot
tools/replay/replay '4cf7a6ad03080c90|2021-09-29--13-46-36|0'
```

**Option B: Use Test Script**

```bash
./scripts/test_simulation.sh
# Select option 2
```

**Option C: Send Manual Commands**

```bash
cd ~/openpilot
python3 << 'EOF'
import cereal.messaging as messaging
import time

pm = messaging.PubMaster(['carControl'])
print("Sending test commands...")

for i in range(100):
    msg = messaging.new_message('carControl')
    
    # Simulate lane keeping - gentle left-right oscillation
    steer = 0.3 * (1 if (i // 10) % 2 == 0 else -1)
    msg.carControl.actuators.steer = steer
    
    pm.send('carControl', msg)
    print(f"Sent steer: {steer:+.1f}")
    time.sleep(0.5)
EOF
```

---

## What You'll Experience

### Starting Up

```bash
$ python3 scripts/visualize.py

============================================================
Steering Visualizer Running
============================================================

Waiting for openpilot messages...

In another terminal, run:
  cd ~/openpilot
  tools/replay/replay '<route>|<segment>'

Or use test_simulation.sh
============================================================
```

A window opens showing:
- Gray steering wheel (neutral position)
- Empty PWM bar
- Flat graph line
- Status: "○ WAITING"

### When Data Arrives

The moment openpilot starts sending commands:

1. **Steering wheel animates** - Rotates smoothly left/right
2. **PWM bar fills** - Green (right) or Orange (left)
3. **Graph scrolls** - Shows command history
4. **Status updates** - "● RECEIVING" in green
5. **Numbers change** - Real-time PWM and steer values

### Watching Lane Keeping

As openpilot processes video and detects lanes:

```
Gentle curve right:
  Wheel slowly rotates clockwise →
  PWM bar fills green to the right
  Graph shows gradual positive slope
  Numbers: Steer: +0.234, PWM: +35

Correction left:
  Wheel rotates back counter-clockwise ←
  PWM bar fills orange to the left
  Graph dips below center
  Numbers: Steer: -0.156, PWM: -23

Straight road:
  Wheel returns to center
  PWM bar empties
  Graph flattens at zero
  Numbers: Steer: 0.000, PWM: 0
```

**It's like watching your steering wheel in action!**

---

## Understanding the Display

### Steering Wheel (Top Left)
- **Red dot** - Shows top of wheel (orientation indicator)
- **Rotation** - Matches what physical motor would do
- **Angle display** - Current steering angle in degrees
- **Range** - ±540° (1.5 full rotations each way)

### Motor Command (Top Right)
- **PWM Bar**
  - Center = neutral
  - Fill right (green) = clockwise/right turn
  - Fill left (orange) = counter-clockwise/left turn
  - Length = strength of command
- **PWM Value** - Actual number sent to motor (-255 to +255)
- **Direction** - Human-readable motor direction

### Openpilot Command (Middle Right)
- **Steer Value** - Raw command from openpilot (-1.0 to +1.0)
- **Color coded** - Green (right), Orange (left), White (neutral)
- **Scale/Cap** - Shows your config settings

### Steering History (Bottom)
- **Blue line** - Steering commands over time
- **Scrolls right to left** - Recent on right
- **Range** - ±1.0 full scale
- **Shows patterns** - Lane keeping, corrections, oscillations

### Stats (Top Left & Bottom)
- **Messages** - Total received from openpilot
- **Rate** - Update frequency (should match config)
- **Status** - Connection state

---

## Testing Scenarios

### Scenario 1: Gentle Curve
Watch how openpilot smoothly follows a curve:
```
Command: +0.1 to +0.3 (slight right)
PWM: +15 to +45
Wheel: Slow clockwise rotation
Motor: Gentle right pressure
```

### Scenario 2: Sharp Turn
See how it handles tighter curves:
```
Command: +0.5 to +0.8 (hard right)
PWM: +75 to +120
Wheel: Fast clockwise rotation
Motor: Strong right force
```

### Scenario 3: Lane Correction
When car drifts, watch the correction:
```
Drift left detected:
  Command jumps to +0.6
  PWM spikes to +90
  Wheel quickly rotates right
  Gradually returns to center
```

### Scenario 4: Straight Road
Perfect for testing neutral state:
```
Command: -0.05 to +0.05 (tiny corrections)
PWM: -8 to +8
Wheel: Barely moves
Motor: Micro-adjustments
```

---

## Interpreting What You See

### Good Patterns ✅
- **Smooth curves** - Gradual steering changes
- **Quick returns** - Fast correction to center
- **Small oscillations** - Normal lane keeping
- **Responsive** - Immediate reaction to lane detection

### Concerns ⚠️
- **Constant max PWM** - May need lower pwm_scale
- **Huge oscillations** - Tune PID or check data
- **No movement** - Check openpilot is sending data
- **Jerky motion** - May need smoothing

### Calibration Insights

**If steering looks too aggressive:**
```yaml
# Edit bridge/config.yaml
pwm_scale: 100  # Reduce from 150
```

**If steering looks too weak:**
```yaml
pwm_scale: 200  # Increase from 150
```

Re-run visualizer to see the difference!

---

## Tips & Tricks

### Multiple Windows

**Terminal 1:** Replay
```bash
tools/replay/replay '<route>|0'
```

**Terminal 2:** Visualizer
```bash
python3 scripts/visualize.py
```

**Terminal 3:** Monitor (optional)
```bash
watch -n 1 'echo "Replaying openpilot data..."'
```

### Adjusting Speed

Slow down replay to see details:
```bash
# 0.5x speed
tools/replay/replay --speed 0.5 '<route>|0'

# 2x speed  
tools/replay/replay --speed 2 '<route>|0'
```

### Recording Session

Want to share what you see?

**Linux/WSL:**
```bash
sudo apt install kazam  # Screen recorder
kazam  # Start recording
```

**Windows (for WSL window):**
- Win+G (Game Bar) → Record
- Or use OBS Studio

### Different Routes

Try different driving scenarios:
```bash
# Highway driving (higher speeds)
tools/replay/replay 'highway-route|0'

# City driving (frequent turns)
tools/replay/replay 'city-route|0'

# Curvy roads (lots of steering)
tools/replay/replay 'mountain-route|0'
```

Browse routes at: https://comma.ai/explore

---

## Controls

- **Q** or **ESC** - Quit visualizer
- **Window Close (X)** - Quit visualizer

That's it - fully automatic!

---

## Troubleshooting

### "pygame not found"

```bash
pip3 install pygame
```

If that fails:
```bash
sudo apt install python3-pygame
```

### "No messages received"

**Check openpilot is running:**
```bash
# In another terminal
cd ~/openpilot
tools/replay/replay '<route>|0'
```

**Check cereal is working:**
```bash
python3 -c "import cereal.messaging; print('OK')"
```

### "Window doesn't open"

**For WSL, you may need X server:**

1. Install VcXsrv on Windows
2. In WSL:
```bash
export DISPLAY=:0
python3 scripts/visualize.py
```

Or use Windows Terminal with WSLg (Windows 11).

### "Wheel doesn't move"

- Wait longer - data may take time to start
- Check replay is actually playing (frame counter incrementing)
- Try manual command test (Option C above)

---

## What This Proves

When you see the visualizer working:

✅ **Openpilot is functioning** - Lane detection, control logic  
✅ **Bridge can receive data** - Message subscription works  
✅ **Scaling is correct** - PWM values in expected range  
✅ **Timing is good** - Smooth, responsive updates  
✅ **System is integrated** - Complete data flow verified  

**When hardware is connected, it will do exactly what you see on screen!**

---

## Next Steps

After seeing it work visually:

1. ✅ **You've confirmed** - Software works perfectly
2. 🔧 **Order hardware** - ESP32, BTS7960, motor with confidence
3. 📦 **When it arrives** - Flash ESP32, wire up
4. 🧪 **Bench test** - Motor will respond just like visualization
5. 🚗 **Vehicle test** - Install and drive!

The visualization shows you **exactly** what the physical motor will do.

---

## Advanced: Side-by-Side Comparison

When you get hardware, run both at once:

**Terminal 1:** Real hardware
```bash
python3 bridge/op_serial_bridge.py --debug
```

**Terminal 2:** Visualizer
```bash
python3 scripts/visualize.py
```

**Terminal 3:** Replay
```bash
cd ~/openpilot
tools/replay/replay '<route>|0'
```

Watch the visualization match the physical motor in real-time!

---

**Now you can see, understand, and verify the complete system without any hardware!** 🎉
