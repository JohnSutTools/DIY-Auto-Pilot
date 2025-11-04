# POC Testing Guide - In-Car Visualization

## Your POC Setup

### Hardware Required
- ✓ Laptop with Ubuntu VM (VirtualBox with bridged network)
- ✓ USB Webcam mounted on windshield
- ✓ Car with passenger seat for you
- ✓ Driver to operate the vehicle

### What You'll See

The openpilot UI will display:
1. **Live camera feed** from your windshield-mounted webcam
2. **Green lane lines** - detected left and right lanes
3. **Red path line** - the desired trajectory openpilot wants to follow
4. **Steering angle indicator** - how much steering correction is needed
5. **Model confidence** - how confident the AI is in lane detection
6. **Status indicators** - system health, active/inactive states

### POC Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  REAL WORLD              VIRTUAL (UI)           FUTURE       │
├─────────────────────────────────────────────────────────────┤
│  Webcam captures    →    openpilot detects   →   (Eventually)│
│  road/lanes              lanes and path           ESP32 motor│
│                                                    steers     │
│  Human drives       →    UI shows steering    →   (Future)   │
│  the car                 corrections needed        Auto-steer│
└─────────────────────────────────────────────────────────────┘
```

### Testing Scenarios

#### 1. Straight Road with Clear Lanes
**Expected:** Green lane lines track perfectly, red path stays centered, minimal steering corrections

#### 2. Gentle Curves
**Expected:** Lane lines follow curve smoothly, red path adjusts ahead of curve, steering angle increases

#### 3. Lane Changes (Driver Initiated)
**Expected:** System detects lane departure, lane lines shift, path recalculates

#### 4. Poor Lighting / Faded Lines
**Expected:** Model confidence drops, lane detection may become intermittent

#### 5. Highway vs City Streets
**Expected:** Better performance on highways with clear markings

## Running the POC

### Setup (One Time)
```bash
# On Ubuntu VM
ssh user@192.168.68.115

# Ensure OpenCL is installed (you're doing this now)
sudo apt-get install -y pocl-opencl-icd ocl-icd-opencl-dev

# Verify webcam is detected
ls /dev/video0  # Should exist

# Test webcam capture
v4l2-ctl --list-devices
```

### Launch System
```bash
cd ~/DIY-Auto-Pilot
source ~/openpilot/.venv/bin/activate

# Full system with UI (default for POC)
python3 scripts/launch_lkas.py

# Headless mode (no UI, for production later)
python3 scripts/launch_lkas.py --no-ui
```

### What to Watch For

✅ **Good Signs:**
- UI window opens and shows camera feed
- Lane lines appear as green overlays
- Red path line is visible and smooth
- Steering angle changes when driver turns
- System stays active for extended periods

⚠️ **Issues to Note:**
- Lane lines flickering or disappearing (poor detection)
- Red path jumps around erratically (unstable planning)
- UI crashes or freezes (resource issues)
- No steering commands in bridge output (controlsd not working)

### Reading the Bridge Output

With `--debug` flag, bridge shows:
```
[DEBUG] Steer: +0.25 → PWM: +37  # Right turn, 25% of max
[DEBUG] Steer: -0.15 → PWM: -22  # Left turn, 15% of max
[DEBUG] Steer: 0.00 → PWM: 0     # Straight, no correction
```

**For your POC:**
- Positive values = steer right
- Negative values = steer left
- Magnitude = strength of correction

### Comparing Virtual vs Real

| Real World | Virtual UI Should Show |
|------------|------------------------|
| Driver turns left | Steering angle goes negative |
| Driver turns right | Steering angle goes positive |
| Car drifts left | Red path shifts right, corrective steering |
| Car drifts right | Red path shifts left, corrective steering |
| Perfect lane keeping | Minimal steering corrections, path centered |

### Data Collection

Things to document during POC:
1. **Lane Detection Accuracy** - How often are lanes correctly identified?
2. **Path Stability** - Does the red path line look smooth or jumpy?
3. **Steering Response** - Do corrections make sense given road conditions?
4. **Edge Cases** - When does the system struggle? (curves, lighting, etc.)
5. **Resource Usage** - Does laptop/VM handle the processing load?

### POC Success Criteria

Before moving to hardware integration:
- [ ] UI consistently shows lane detection on various roads
- [ ] Steering commands are reasonable and safe
- [ ] System runs stably for 15+ minutes
- [ ] Can visualize difference between good/bad lane detection
- [ ] Confident in the algorithm's decision-making

### Next Steps After POC

Once UI/visualization is proven:
1. Add ESP32 hardware to the mix
2. Connect bridge to actual motor
3. Test in stationary vehicle (parking lot)
4. Gradually increase to low-speed driving
5. Full integration with human override

## Troubleshooting

### UI Doesn't Appear
```bash
# Check DISPLAY is set
echo $DISPLAY  # Should be :0 or :1

# Check X11 forwarding
xhost +  # Allow all connections (testing only)

# Try setting display explicitly
export DISPLAY=:0
python3 scripts/launch_lkas.py
```

### Webcam Not Detected
```bash
# List video devices
ls -la /dev/video*

# Check USB passthrough to VM
lsusb  # Should show your webcam

# Test webcam with simple capture
ffmpeg -f v4l2 -i /dev/video0 -frames 1 test.jpg
```

### Modeld Crashes
```bash
# Verify OpenCL is working
clinfo  # Should show CPU device

# Check if pocl is installed
dpkg -l | grep pocl
```

### Low Performance
- Reduce camera resolution in webcamerad
- Close other applications
- Allocate more CPU/RAM to VM
- Use physical Linux instead of VM

## Safety Reminders

⚠️ **CRITICAL:**
- This is a **VISUALIZATION POC ONLY**
- No actual steering control yet
- Always have a human driver in full control
- Test in safe environments (empty roads, good weather)
- Have emergency stop plan before hardware integration

## Questions to Answer During POC

1. Is lane detection reliable enough for your use case?
2. Do steering corrections align with your driving intuition?
3. What road conditions cause the most problems?
4. Is the latency acceptable (camera → decision → display)?
5. Would you trust this system with actual steering control?

Your POC answers these questions BEFORE connecting to real hardware! 🎯
