# Raspberry Pi 2 Setup - Copy & Paste Commands

## 📥 Installation (One Command)

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnSutTools/DIY-Auto-Pilot/main/scripts/pi_setup.sh)
```

**What this does:**
- Installs all dependencies
- Builds openpilot (90-120 min)
- Sets up steering bridge
- Applies Pi 2 optimizations automatically
- Increases swap to 2GB
- Disables unnecessary services

**After installation completes:**
```bash
sudo reboot
```

---

## 🧪 Testing After Reboot

### Test 1: Integration Test (No Hardware Needed)

```bash
cd ~/steering-actuator/scripts
./test_integration.sh
```

**Expected Output:**
```
[SIMULATOR] Publishing steering commands...
[BRIDGE] MOCK: S:+72  Steer: +0.481 -> PWM: +72
[BRIDGE] MOCK: S:-57  Steer: -0.385 -> PWM: -57
```

Press `Ctrl+C` to stop.

---

### Test 2: Full System with Camera

```bash
cd ~/steering-actuator
python3 launch.py
```

**What you'll see:**
- Openpilot starting (takes 30-60 seconds on Pi 2)
- Camera feed processing
- Bridge receiving steering commands
- Performance: 5-10 FPS (normal for Pi 2)

Press `Ctrl+C` to stop.

---

## 🔌 Connect ESP32 Hardware

### 1. Check if ESP32 detected
```bash
ls /dev/ttyUSB* /dev/ttyACM*
```

Should show: `/dev/ttyUSB0` (or similar)

### 2. Update config
```bash
nano ~/steering-actuator/bridge/config.yaml
```

Change:
```yaml
mock_mode: false
serial_port: /dev/ttyUSB0  # Use your device from step 1
```

Save: `Ctrl+X`, then `Y`, then `Enter`

### 3. Test with real hardware
```bash
cd ~/steering-actuator
python3 launch.py
```

Motor should respond to steering commands!

---

## 📹 Camera Troubleshooting

### USB Camera
```bash
# Check if detected
ls /dev/video*

# Test camera
fswebcam test.jpg
```

### Pi Camera Module
```bash
# Enable in config
sudo raspi-config
# Navigate: Interface Options -> Camera -> Enable

# Reboot
sudo reboot

# Test
raspistill -o test.jpg
```

---

## 🔍 Monitoring

### Check System Performance
```bash
# CPU temperature
vcgencmd measure_temp

# Memory usage
free -h

# CPU usage
htop
```

Press `q` to exit htop.

### Check Processes
```bash
# See if openpilot is running
ps aux | grep python

# See bridge status
ps aux | grep bridge
```

---

## 🛠️ Common Issues

### Permission Denied (Serial Port)
```bash
sudo usermod -a -G dialout $USER
sudo reboot
```

### Out of Memory
```bash
# Check swap is enabled
free -h

# Should show 2GB swap
# If not, run:
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Camera Not Working
```bash
# USB camera not detected
lsusb

# Pi camera not working
vcgencmd get_camera
# Should show: supported=1 detected=1
```

### System Too Slow
```bash
# Check what's running
htop

# Disable more services
sudo systemctl disable cups
sudo systemctl disable ModemManager
```

---

## 🌐 Remote Access (SSH)

### Enable SSH
```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

### Find Pi IP Address
```bash
hostname -I
```

### Connect from Laptop
```bash
ssh pi@<IP_ADDRESS>
# Example: ssh pi@192.168.1.100
```

---

## 📊 Performance Expectations (Pi 2)

| Metric | Value | Notes |
|--------|-------|-------|
| FPS | 5-10 | Normal for Pi 2 |
| Latency | 200-500ms | Acceptable for testing |
| CPU Load | 80-95% | Expected |
| Memory | ~900MB | Will use swap |
| Temperature | 50-70°C | Normal range |

---

## 🚀 Quick Commands Reference

```bash
# Start complete system
cd ~/steering-actuator && python3 launch.py

# Start bridge only (if openpilot running separately)
cd ~/steering-actuator/bridge
python3 op_serial_bridge.py --config config.yaml --debug

# Run test simulator
cd ~/steering-actuator/scripts
PYTHONPATH=~/openpilot ~/openpilot/.venv/bin/python test_with_webcam.py

# Check logs
tail -f ~/steering-actuator/logs/*.log

# Update code from GitHub
cd ~/steering-actuator
git pull
```

---

## ⚠️ Safety Checklist

Before vehicle testing:

- [ ] Bench tested motor responds correctly
- [ ] Emergency stop works (Ctrl+C)
- [ ] Steering direction is correct (not inverted)
- [ ] PWM limits are safe (check config.yaml)
- [ ] Physical mechanical limits tested
- [ ] Manual override mechanism available
- [ ] Test in safe, controlled environment only

---

## 📖 Full Documentation

- Installation Guide: `~/steering-actuator/docs/PI_SETUP.md`
- Project Overview: `~/steering-actuator/project-overview.md`
- Integration Notes: `~/steering-actuator/docs/INTEGRATION.md`

---

## 🆘 Get Help

If stuck, check:
1. System logs: `~/steering-actuator/logs/`
2. GitHub issues: https://github.com/JohnSutTools/DIY-Auto-Pilot/issues
3. Run diagnostics: `~/steering-actuator/scripts/check_paths.py`
