# Fresh Ubuntu Setup - Complete Walkthrough

**System Requirements:**
- Ubuntu 20.04 or 22.04 (Desktop or Server)
- 4GB+ RAM (8GB+ recommended)
- 30GB+ free disk space
- Internet connection

**Time Required:** 30-45 minutes (mostly automated)

---

## Step 1: Update System

```bash
# Update package list
sudo apt update

# Upgrade existing packages
sudo apt upgrade -y

# Install basic tools
sudo apt install -y git curl wget
```

**Expected output:**
```
Reading package lists... Done
Building dependency tree... Done
...
0 upgraded, X newly installed, 0 to remove
```

---

## Step 2: Clone Repository

```bash
# Navigate to home directory
cd ~

# Clone your project
git clone https://github.com/JohnSutTools/DIY-Auto-Pilot.git steering-actuator

# Enter directory
cd steering-actuator

# Verify files
ls -la
```

**Expected output:**
```
total XX
drwxrwxr-x  bridge/
drwxrwxr-x  docs/
drwxrwxr-x  firmware/
drwxrwxr-x  scripts/
-rw-rw-r--  launch.py
-rw-rw-r--  README.md
...
```

---

## Step 3: Run Complete Setup

```bash
# Make setup script executable
chmod +x scripts/setup_system.sh

# Run setup (this takes 15-30 minutes)
./scripts/setup_system.sh
```

**What this does:**
1. ✅ Installs system dependencies (compilers, libraries)
2. ✅ Clones openpilot from GitHub
3. ✅ Builds openpilot (this is the slow part - 10-20 min)
4. ✅ Installs Python dependencies
5. ✅ Sets up serial port access
6. ✅ Configures your environment

**During setup, you'll be asked:**

```
⚠️  You need to log out and back in for serial port access
   (Continue for now, remember to log out later)

Create Python virtual environment? (recommended) [y/N]: n
   (Type 'n' - we'll use system Python for simplicity)

Test ESP32 now? [y/N]: n
   (Type 'n' - you don't have it connected yet)

Create systemd service for auto-start on boot? [y/N]: n
   (Type 'n' for now - you can add this later)
```

**Wait for completion message:**
```
==========================================
Setup Complete!
==========================================

Next steps:
1. ✓ Openpilot installed at: /home/YOUR_USER/openpilot
2. Flash ESP32 firmware (see firmware/README.md)
3. Configure bridge/config.yaml with your serial port
4. Connect USB webcam
5. Launch system:

   python3 launch.py
```

---

## Step 4: Verify Installation

```bash
# Check openpilot is installed
ls ~/openpilot
# Should show: cereal, selfdrive, tools, launch_openpilot.sh, etc.

# Test Python environment
python3 -c "import cereal.messaging; print('✓ Cereal works')"

# Test bridge imports
python3 -c "import yaml; import serial; print('✓ Dependencies installed')"
```

**All three commands should complete without errors.**

---

## Step 5: Test in Simulation (No Hardware Needed!)

This is the best way to verify everything works.

```bash
# Make test script executable
chmod +x scripts/test_simulation.sh

# Run simulation test
./scripts/test_simulation.sh
```

**Interactive menu appears:**
```
Simulation Options:
1. Simulated bridge only
2. Full replay test (recommended)  ← Choose this!
3. Custom replay route

Select option [1-3]: 2
```

**Type `2` and press Enter.**

**What happens:**
1. Downloads demo route (~100MB, one time only)
2. Starts openpilot replay in background
3. Starts simulated bridge
4. Shows combined output

**You'll see:**
```
[openpilot] Loading route: 4cf7a6ad03080c90...
[openpilot] Frame: 1234/5000
[bridge] 📡 Steer: +0.234 → PWM: +35
[bridge] 🔧 Motor: PWM= +35 Direction: RIGHT (clockwise)
[bridge] 📡 Steer: -0.089 → PWM: -13
[bridge] 🔧 Motor: PWM= -13 Direction: LEFT (counter-clockwise)
...
```

**Press Ctrl+C to stop when you've seen enough.**

**✓ Success!** If you see steering commands and motor responses, your software is working perfectly.

---

## Step 6: Connect USB Webcam (Optional for Now)

```bash
# List video devices
v4l2-ctl --list-devices

# Test camera feed (if connected)
ffplay /dev/video0
# Press Q to quit
```

**Expected output:**
```
USB Camera (usb-0000:00:14.0-1):
        /dev/video0
        /dev/video1
```

If you see your camera, great! If not, don't worry - you can test with simulation data.

---

## Step 7: Prepare for Hardware (When Ready)

### Flash ESP32 Firmware

**On Windows (easiest):**
1. Install [Arduino IDE](https://www.arduino.cc/en/software)
2. Add ESP32 board support:
   - File → Preferences
   - Additional Board Manager URLs: `https://espressif.github.io/arduino-esp32/package_esp32_index.json`
   - Tools → Board Manager → Search "ESP32" → Install
3. Open `firmware/steering_motor/steering_motor.ino`
4. Select Board: ESP32S3 Dev Module
5. Connect ESP32 via USB
6. Upload

**On Ubuntu (alternative):**
```bash
# Install Arduino CLI
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh

# Add to PATH
export PATH=$PATH:$HOME/bin

# Install ESP32 platform
arduino-cli core install esp32:esp32

# Compile and upload
cd ~/steering-actuator/firmware/steering_motor
arduino-cli compile --fqbn esp32:esp32:esp32s3
arduino-cli upload -p /dev/ttyUSB0 --fqbn esp32:esp32:esp32s3
```

### Configure Serial Port

```bash
# Connect ESP32 to Ubuntu machine

# Find device
ls /dev/ttyUSB*
# Example: /dev/ttyUSB0

# Edit config
cd ~/steering-actuator
nano bridge/config.yaml
```

**Change this line:**
```yaml
serial_port: /dev/ttyUSB0  # Update to match your device
```

**Save:** Ctrl+X, then Y, then Enter

### Test ESP32

```bash
# Run ESP32 test
python3 scripts/test_esp32.py --port /dev/ttyUSB0 --interactive
```

**You should see:**
```
Testing serial connection to /dev/ttyUSB0...
✓ ESP32 connected: ESP32-S3 Steering Controller Ready

Interactive mode - Enter commands:
> S:+100
  (motor should spin clockwise)
> S:-100
  (motor should spin counter-clockwise)  
> STOP
  (motor stops)
> q
```

---

## Step 8: Run Complete System

Once hardware is ready:

```bash
cd ~/steering-actuator
python3 launch.py
```

**Expected output:**
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
[openpilot] LKAS mode enabled
[bridge] ESP32 connected: ESP32-S3 Steering Controller Ready
[bridge] Bridge running at 20 Hz
[openpilot] Lane detection: searching...
...
```

**Stop:** Press Ctrl+C once - everything shuts down cleanly.

---

## Troubleshooting

### Issue: "Permission denied" on serial port

```bash
# Add yourself to dialout group
sudo usermod -a -G dialout $USER

# Log out and back in (or reboot)
sudo reboot
```

### Issue: "cereal module not found"

```bash
# Add to current session
export PYTHONPATH="${PYTHONPATH}:$HOME/openpilot"

# Permanently add to bash
echo 'export PYTHONPATH="${PYTHONPATH}:$HOME/openpilot"' >> ~/.bashrc
source ~/.bashrc
```

### Issue: "scons: command not found" during setup

```bash
# Install scons manually
sudo apt install -y scons
```

### Issue: Build fails with memory error

```bash
# Limit parallel jobs (for systems with <8GB RAM)
cd ~/openpilot
scons -j2  # Use only 2 cores instead of all
```

### Issue: Webcam not detected

```bash
# Check USB connection
lsusb

# Check video devices
ls -l /dev/video*

# Add to video group
sudo usermod -a -G video $USER
```

### Issue: Simulation shows no steering commands

```bash
# Verify openpilot is working
cd ~/openpilot
python3 -c "
import cereal.messaging as messaging
sm = messaging.SubMaster(['carControl'])
print('✓ Messaging system works')
"
```

---

## Quick Command Reference

```bash
# Daily use
cd ~/steering-actuator
python3 launch.py                    # Start everything

# Testing
./scripts/test_simulation.sh         # Test without hardware
python3 scripts/test_esp32.py        # Test ESP32
python3 scripts/calibrate.py         # Adjust PWM settings

# Debugging
python3 launch.py --debug            # Verbose output
python3 bridge/op_serial_bridge.py --debug  # Bridge only

# Logs (if using systemd service)
journalctl -u openpilot-steering -f  # View live logs
```

---

## Next Steps After Fresh Install

- [x] Step 1-3: System setup ✓
- [x] Step 4: Verify installation ✓
- [x] Step 5: Test simulation ✓
- [ ] Step 6: Connect webcam
- [ ] Step 7: Flash ESP32 & test hardware
- [ ] Step 8: Run complete system
- [ ] Mount motor in vehicle
- [ ] Calibrate in parked car
- [ ] Test in empty parking lot
- [ ] Supervised road testing

---

## Files You'll Interact With

**Configuration:**
- `bridge/config.yaml` - Serial port, PWM settings

**Running:**
- `launch.py` - Main launcher (start everything)
- `scripts/test_simulation.sh` - Testing without hardware
- `scripts/test_esp32.py` - Hardware testing

**Documentation:**
- `QUICKSTART.md` - Getting started guide
- `docs/TESTING.md` - Complete testing procedures
- `docs/SIMULATION.md` - Simulation reference
- `firmware/README.md` - ESP32 setup
- `docs/wiring.md` - Hardware connections

---

## Support

**If you get stuck:**

1. Check `docs/TESTING.md` for detailed troubleshooting
2. Review `QUICKSTART.md` for step-by-step guidance
3. Check openpilot Discord: https://discord.comma.ai
4. Review logs: `journalctl -u openpilot-steering -f`

---

**You're all set!** 🎉

Your Ubuntu system is now ready to run the complete LKAS system. Test in simulation first, then add hardware when ready.
