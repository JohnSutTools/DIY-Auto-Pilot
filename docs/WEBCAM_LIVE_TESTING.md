# Live Webcam Testing - See Openpilot Work With YOUR Camera

## What This Does

Run openpilot with your USB webcam **while driving** and see the steering commands it would send - all visualized in real-time on your laptop screen!

**Perfect for:**
- Testing before buying ESP32/motor hardware
- Validating openpilot works with your webcam
- Seeing what steering commands it generates on your roads
- Tuning parameters for your specific setup

---

## System Flow

```
Your USB Webcam (mounted in car)
    ↓ Real-time video feed
Openpilot (running on laptop)
    ↓ Lane detection + steering calculation
carControl messages
    ↓ Steer commands (-1.0 to +1.0)
Visualizer Window (on laptop screen)
    ↓ Shows steering wheel animation
You can see what it would do!
```

**No motor needed** - just visual confirmation!

---

## Setup Steps

### 1. Install WSL2 on Your Laptop

Follow `docs/WINDOWS_WSL_SETUP.md` to get WSL2 + Ubuntu running.

### 2. Setup Openpilot System

```bash
cd ~/steering-actuator
./scripts/setup_system.sh
```

This installs openpilot + all dependencies (~30-60 minutes).

### 3. Connect USB Webcam to WSL

**Windows 11 (Easiest):**
```powershell
# In PowerShell (as Administrator)
usbipd list  # Find your webcam
usbipd bind --busid <BUSID>
usbipd attach --wsl --busid <BUSID>
```

**Verify in WSL:**
```bash
ls /dev/video*
# Should show: /dev/video0
```

### 4. Test Webcam

```bash
sudo apt install v4l-utils
v4l2-ctl --list-devices
v4l2-ctl --device=/dev/video0 --list-formats-ext
```

You should see your webcam listed with supported resolutions (720p or 1080p).

---

## Running Live Test

### Start System (Two Options)

**Option A: With Visualization (Recommended)**

Terminal 1:
```bash
cd ~/steering-actuator
python3 launch.py --visualize
```

Terminal 2:
```bash
python3 scripts/visualize.py --mode live
```

**Option B: Text Output Only**

```bash
cd ~/steering-actuator
python3 launch.py --debug
```

You'll see steering commands printed:
```
[Bridge] Steer: +0.234 → PWM: +35 (RIGHT)
[Bridge] Steer: -0.156 → PWM: -23 (LEFT)
[Bridge] Steer: +0.089 → PWM: +13 (RIGHT)
```

---

## What You'll See

### GUI Visualization Window

```
┌─────────────────────────────────────────┐
│  LIVE MODE - Using /dev/video0          │
├─────────────────────────────────────────┤
│                                          │
│   🎡 Steering Wheel                     │
│   (rotates based on lane detection)     │
│                                          │
│   ▓▓▓░░░░░░░░ Motor Command             │
│   PWM: +45  → RIGHT TURN                │
│                                          │
│   Openpilot: Steer +0.300               │
│   Lane Confidence: 95%                   │
│                                          │
│   📈 Steering History (scrolling)       │
│                                          │
│   Camera: ● ACTIVE  |  20 FPS           │
└─────────────────────────────────────────┘
```

### Terminal Output

```
[Openpilot] Initializing with /dev/video0
[Openpilot] Camera: 1920x1080 @ 30fps
[Openpilot] Lane detection: ACTIVE
[Bridge] Connected to openpilot messages
[Bridge] Steer: +0.234 → PWM: +35
[Bridge] Steer: +0.267 → PWM: +40
[Bridge] Steer: +0.198 → PWM: +30
```

---

## Testing While Driving

### Safe Testing Setup

1. **Passenger operates laptop** (not you!)
2. Mount webcam on dashboard (facing road)
3. Power laptop from car (12V → 120V inverter or USB-C PD)
4. Start system before driving
5. Passenger watches visualization

### What to Observe

**Straight Road:**
- Steering commands near zero (±0.05)
- Small micro-adjustments
- Wheel barely moves in visualization

**Gentle Curve:**
- Steering gradually increases (0.1 → 0.3)
- Smooth rotation in visualization
- Follows curve naturally

**Sharp Turn:**
- Stronger steering (0.5 → 0.8)
- Fast wheel rotation in visualization
- Quick response to lane change

**Lane Drift:**
- Sudden correction (spike to 0.6)
- Quick return to center
- Reactive behavior

**Poor Lane Visibility:**
- Erratic commands or zero output
- Low confidence indicators
- May need better camera placement

---

## Interpreting Results

### Good Signs ✅

- Smooth, gradual steering changes
- Quick corrections when drifting
- Returns to center on straight roads
- Responds to lane markers
- Stable in curves

### Concerns ⚠️

- **No output on marked roads** → Camera positioning issue
- **Extreme oscillations** → May need tuning
- **Stuck at max PWM** → Scale too high
- **Delayed response** → Check camera FPS
- **Random jitter** → Poor lane detection

### Adjustments

**If steering looks too aggressive:**
```yaml
# Edit bridge/config.yaml
pwm_scale: 100  # Reduce from 150
```

**If steering looks too weak:**
```yaml
pwm_scale: 200  # Increase from 150
```

**If detection is poor:**
- Adjust camera angle (slight downward tilt)
- Clean webcam lens
- Test in better lighting conditions
- Try different roads (clearer lane markings)

---

## Data Logging

### Record Your Test Session

```bash
# Start logging
python3 launch.py --log-session ~/test-drives/session1

# Drive around for 10-15 minutes

# Stop (Ctrl+C)

# Review data
ls ~/test-drives/session1/
# Shows: video.mp4, steering_commands.csv, openpilot_logs/
```

### Analyze Later

```bash
# Plot steering commands
python3 scripts/analyze_session.py ~/test-drives/session1

# Replay in visualizer
python3 scripts/visualize.py --replay ~/test-drives/session1
```

---

## Troubleshooting

### Webcam Not Detected

```bash
# Check USB connection
lsusb | grep -i camera

# Check video devices
ls -l /dev/video*

# Test webcam
ffplay /dev/video0
```

### Openpilot Fails to Start

```bash
# Check camera permissions
sudo usermod -a -G video $USER
# Logout and login again

# Test openpilot separately
cd ~/openpilot
python3 -c "import cereal.messaging as messaging; print('OK')"
```

### No Steering Commands

```bash
# Check bridge is running
ps aux | grep op_serial_bridge

# Check messages flowing
cd ~/openpilot
python3 << 'EOF'
import cereal.messaging as messaging
sm = messaging.SubMaster(['carControl'])
while True:
    sm.update(1000)
    if sm.updated['carControl']:
        print(f"Steer: {sm['carControl'].actuators.steer}")
EOF
```

### Visualization Window Not Showing

```bash
# For WSL, ensure X server running
export DISPLAY=:0

# Test pygame
python3 -c "import pygame; pygame.init(); print('OK')"

# Check VcXsrv/WSLg is running
```

---

## Safety Notes

### Critical Safety Rules

⚠️ **DO NOT:**
- Rely on this for actual steering (no motor connected)
- Test alone (need passenger to operate laptop)
- Look at laptop screen while driving
- Test in heavy traffic or unsafe conditions

✅ **DO:**
- Have passenger operate and observe
- Test on safe, empty roads first
- Keep hands on wheel at all times
- Treat as data gathering only
- Pull over to check results

**This is a PREVIEW system** - it shows what steering commands would be sent, but **does not control your vehicle**!

---

## Next Steps After Testing

### If Results Look Good ✅

1. **Data validated** - You've confirmed openpilot works with your setup
2. **Order hardware** - ESP32, BTS7960, motor
3. **Bench test** - Wire up hardware, test on workbench
4. **Vehicle integration** - Install motor on steering wheel
5. **Gradual testing** - Start in parking lot, then safe roads

### If Results Need Work ⚠️

1. **Camera positioning** - Adjust angle/height
2. **Parameter tuning** - Adjust `pwm_scale` in config
3. **Different camera** - Try higher resolution webcam
4. **Road selection** - Test on roads with clearer markings
5. **Lighting** - Test in better conditions

---

## Performance Expectations

### Typical Results

**Good Conditions:**
- Lane detection: 90-95% confidence
- Steering updates: 20 Hz
- Latency: <100ms camera → command
- Smooth, predictable steering

**Challenging Conditions:**
- Worn lane markings: 70-80% confidence
- Night/rain: May need IR camera
- Construction zones: Detection may fail
- Dirt roads: No lane markings detected

---

## Summary

**YES** - You can absolutely:

1. ✅ Install WSL2 on your laptop
2. ✅ Connect USB webcam to WSL
3. ✅ Run openpilot with your webcam
4. ✅ See steering commands while driving
5. ✅ Visualize on laptop screen

**This lets you validate the complete system BEFORE buying any motor hardware!**

When you're satisfied with the results, then order the ESP32/motor and it will physically execute the same commands you're seeing on screen.

---

## Quick Commands Reference

```bash
# Setup (one time)
./scripts/setup_system.sh

# Attach webcam to WSL (Windows PowerShell as Admin)
usbipd attach --wsl --busid <BUSID>

# Start live testing (WSL Ubuntu)
python3 launch.py --visualize

# In another terminal
python3 scripts/visualize.py --mode live

# Stop testing
Ctrl+C (in both terminals)
```

**Now you can test the complete software system with real driving before any hardware investment!** 🚗✨
