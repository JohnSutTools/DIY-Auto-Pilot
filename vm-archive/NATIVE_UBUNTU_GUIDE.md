# Native Ubuntu Installation Guide
## Quick Setup for DIY Auto Pilot LKAS System

This guide will get your LKAS system running on native Ubuntu with full GPU acceleration.

---

## Prerequisites

**Hardware:**
- HP EliteBook 840 G8 (or similar laptop with Intel GPU)
- Logitech C920/C910 USB webcam (720p+, wide FOV)
- ESP32-S3 DevKitC-1 (for motor control)
- BTS7960 motor driver + JGB37-545 gearmotor

**Software:**
- Ubuntu 24.04 LTS (fresh install recommended)
- Internet connection for setup

---

## Part 1: Install Ubuntu 24.04

### Create Installation Media
1. Download Ubuntu 24.04 LTS Desktop ISO from ubuntu.com
2. Create bootable USB with Rufus (Windows) or Etcher
3. Boot from USB (F9/F12 on HP EliteBook)

### Installation Options
**Option A: Dual Boot (Keep Windows)**
- Choose "Install Ubuntu alongside Windows"
- Allocate at least 50GB for Ubuntu partition

**Option B: Ubuntu Only (Recommended for POC)**
- Choose "Erase disk and install Ubuntu"
- Faster performance, no dual-boot complexity

### During Installation
- Username: `user` (or your preference)
- Enable "Download updates while installing"
- Install third-party software (for WiFi/GPU drivers)

---

## Part 2: Automated Setup Script

This single script installs everything needed!

### 1. Boot into Ubuntu

### 2. Open Terminal (Ctrl+Alt+T)

### 3. Copy Project Files

If you have the DIY-Auto-Pilot folder on USB/external drive:
```bash
# Mount and copy
cp -r /path/to/DIY-Auto-Pilot ~/DIY-Auto-Pilot
cd ~/DIY-Auto-Pilot
```

Or clone from GitHub:
```bash
git clone https://github.com/JohnSutTools/DIY-Auto-Pilot.git ~/DIY-Auto-Pilot
cd ~/DIY-Auto-Pilot
```

### 4. Run Setup Script

```bash
# Make executable
chmod +x vm-archive/native-ubuntu-setup.sh

# Run setup (takes 15-30 minutes)
./vm-archive/native-ubuntu-setup.sh
```

**What this installs:**
- Build tools and dependencies
- Python 3.11+
- OpenCL drivers (Intel GPU support)
- OpenCV with V4L2 support
- openpilot (full build)
- All project dependencies

---

## Part 3: Apply Patches and Configure

### 1. Apply openpilot Patches
```bash
cd ~/DIY-Auto-Pilot
chmod +x vm-archive/apply-patches.sh
./vm-archive/apply-patches.sh
```

This applies:
- Forced engagement (bypass safety checks)
- Fake car state injection
- Webcam camera format fix

### 2. Setup CarParams
```bash
cd ~/openpilot
source .venv/bin/activate
python3 ~/DIY-Auto-Pilot/scripts/setup_honda_civic_carparams.py
```

### 3. Connect Webcam
```bash
# Verify camera detected
ls -l /dev/video*

# Should see: /dev/video0 (or similar)
```

---

## Part 4: Launch LKAS System

### Test Camera First
```bash
cd ~/openpilot
source .venv/bin/activate
export ROAD_CAM=0
timeout 5 python3 -m tools.webcam.camerad
```

**Expected:** "Corrupt JPEG data..." messages (normal), camera capturing frames

### Launch Full LKAS System
```bash
cd ~/DIY-Auto-Pilot
~/openpilot/.venv/bin/python3 scripts/launch_lkas.py --no-ui
```

**What runs:**
1. webcamerad - Camera capture (20 FPS)
2. modeld - Lane detection (10-20 FPS with GPU!)
3. paramsd - Parameters
4. locationd - Localization  
5. calibrationd - Camera calibration
6. card - Car interface
7. selfdrived - State machine
8. plannerd - Path planning
9. controlsd - Steering control
10. bridge - Serial bridge to ESP32

### Monitor Steering Commands
Open another terminal:
```bash
cd ~/openpilot
source .venv/bin/activate
python3 ~/DIY-Auto-Pilot/scripts/monitor_steering.py
```

**Expected output:**
```
[0001] SelfdriveState: enabled=True, active=True
  carControl: enabled=True, latActive=True, steer=+0.123
```

**If you see non-zero steer values → LKAS IS WORKING! 🎉**

---

## Part 5: Connect ESP32

### 1. Find Serial Port
```bash
# Plug in ESP32
ls /dev/ttyUSB* /dev/ttyACM*
# Should see: /dev/ttyUSB0 (or similar)
```

### 2. Update Bridge Config
```bash
nano ~/DIY-Auto-Pilot/bridge/config.yaml
```

Change:
```yaml
serial_port: "/dev/ttyUSB0"  # Your ESP32 port
pwm_scale: 100    # Start conservative
pwm_cap: 255      # Max PWM limit
stream_hz: 20     # Update rate
```

### 3. Test Bridge Standalone
```bash
cd ~/DIY-Auto-Pilot
source ~/openpilot/.venv/bin/activate
python3 bridge/op_serial_bridge.py --config bridge/config.yaml --debug
```

Watch for steering commands being sent to ESP32!

---

## Part 6: Validation Checklist

Before taking it on the road:

- [ ] Camera captures frames (no errors)
- [ ] modeld detects lanes (modelV2 publishing)
- [ ] controlsd generates steering commands (non-zero steer values)
- [ ] Bridge receives carControl messages
- [ ] ESP32 responds to serial commands
- [ ] Motor responds to PWM signals
- [ ] Emergency stop works (unplug ESP32 or kill processes)

---

## Troubleshooting

### Camera Not Detected
```bash
# Check USB devices
lsusb | grep -i camera

# Check permissions
sudo usermod -aG video $USER
# Log out and back in
```

### modeld Not Detecting Lanes
```bash
# Check GPU/OpenCL
clinfo | grep "Device Name"

# Should see: Intel GPU

# If not, install OpenCL:
sudo apt install intel-opencl-icd
```

### No Steering Commands (steer=0.000)
1. **Check camera view** - Point at road with visible lane lines
2. **Check modeld output** - Should see "modelV2" updates
3. **Check forced engagement** - Should see enabled=True, active=True

### Process Crashes
```bash
# Check logs
tail -100 /tmp/launch.log

# Kill all and restart
pkill -f launch_lkas
sleep 2
~/openpilot/.venv/bin/python3 ~/DIY-Auto-Pilot/scripts/launch_lkas.py --no-ui
```

---

## Performance Expectations

**Native Ubuntu with Intel Iris Xe GPU:**
- webcamerad: 20-30 FPS
- modeld: 10-20 FPS (GPU accelerated!)
- Lane detection: Real-time, <100ms latency
- Steering commands: 20 Hz update rate
- CPU usage: 30-50% (vs 100% in VM)

**This is FAST ENOUGH for real LKAS operation!**

---

## Safety Reminders

⚠️ **This is a proof of concept system:**
- Always have driver ready to take control
- Test in safe environment first (parking lot)
- Emergency stop: kill processes or unplug ESP32
- Start with low PWM values (pwm_scale=50)
- Monitor system constantly during testing

---

## Next Steps After LKAS Works

1. **Calibration** - Adjust pwm_scale for proper steering feel
2. **Tuning** - Optimize controlsd gains if needed
3. **Mount hardware** - Secure webcam, laptop, ESP32 in vehicle
4. **Real-world testing** - Gradually increase confidence
5. **Data logging** - Record sessions for analysis

---

## Quick Reference Commands

**Start LKAS:**
```bash
cd ~/DIY-Auto-Pilot
~/openpilot/.venv/bin/python3 scripts/launch_lkas.py --no-ui
```

**Monitor steering:**
```bash
cd ~/openpilot && source .venv/bin/activate
python3 ~/DIY-Auto-Pilot/scripts/monitor_steering.py
```

**Stop everything:**
```bash
pkill -f launch_lkas
```

**Check what's running:**
```bash
ps aux | grep python | grep -E 'modeld|controlsd|camerad'
```

---

## Support

**Issue**: Something not working?
1. Check `vm-archive/README.md` for VM troubleshooting lessons
2. Review logs in `/tmp/launch.log`
3. Test components individually (camera, modeld, controlsd)
4. Verify patches applied: `ls -l ~/openpilot/.backups/`

**Success**: LKAS working? Document your setup for future reference!

---

**Created**: November 4, 2025  
**Target**: Native Ubuntu 24.04 on HP EliteBook 840 G8  
**Expected Setup Time**: 30-45 minutes  
**Expected Result**: Full LKAS with real lane detection and steering commands flowing to ESP32
