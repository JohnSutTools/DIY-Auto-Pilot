# Quick Start Guide

## What You're Building

A complete LKAS (Lane Keeping Assist System) that runs on a laptop or Raspberry Pi using a USB webcam and an external motor to turn your steering wheel.

**No comma device needed. No complex wiring. Just plug and play.**

## What You Need

### Hardware
- [ ] Laptop or Raspberry Pi 4 (4GB+ RAM)
- [ ] USB webcam (720p minimum)
- [ ] ESP32-S3 DevKitC-1
- [ ] BTS7960 motor driver
- [ ] JGB37-545 12V motor (316 RPM)
- [ ] 12V power supply (from car battery)
- [ ] USB cables

### Software
- [ ] Ubuntu 20.04/22.04 or Raspberry Pi OS
- [ ] Internet connection for setup

## Setup (One Time)

### 1. Clone and Setup

```bash
# Clone repository
cd ~
git clone <your-repo> steering-actuator
cd steering-actuator

# Run complete setup
chmod +x scripts/setup_system.sh
./scripts/setup_system.sh
```

☕ **Grab coffee** - this takes 15-30 minutes (mostly building openpilot)

### 1.5 Test in Simulation (Recommended!)

**Before touching hardware**, verify everything works:

```bash
chmod +x scripts/test_simulation.sh
./scripts/test_simulation.sh
# Select option 2 (full replay test)
```

This tests the complete system without hardware using real openpilot data.

See [`docs/SIMULATION.md`](docs/SIMULATION.md) for details.

### 2. Flash ESP32

- Install Arduino IDE
- Open `firmware/steering_motor/steering_motor.ino`
- Select Board: **ESP32S3 Dev Module**
- Connect ESP32 via USB
- Click Upload

### 3. Configure Serial Port

```bash
# Find your ESP32
ls /dev/ttyUSB*

# Edit config
nano bridge/config.yaml
```

Change `serial_port: /dev/ttyUSB0` to match your device.

### 4. Test ESP32

```bash
python3 scripts/test_esp32.py --port /dev/ttyUSB0 --interactive
```

You should see:
```
✓ ESP32 connected: ESP32-S3 Steering Controller Ready

Interactive mode - Enter commands:
> S:+100
  (motor spins clockwise)
> S:-100
  (motor spins counter-clockwise)
> STOP
  (motor stops)
```

## Daily Use

### Start System

```bash
cd ~/steering-actuator
python3 launch.py
```

That's it! You'll see:
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

[openpilot] Webcam initialized
[openpilot] Lane detection active
[bridge] Motor responding to steering commands
```

### Stop System

Press **Ctrl+C** - everything shuts down cleanly.

## First Drive

### 1. Bench Test (At Home)
```bash
python3 launch.py
```
- Point webcam at a picture of a road with lane lines
- Watch motor respond to "detected" lanes

### 2. Parked Test (In Car)
- Mount motor on steering wheel
- Start system
- Turn on car (engine doesn't need to run)
- Verify motor responds when you move

### 3. Real Drive (Empty Road)
- Start in empty parking lot or quiet road
- Engage system
- Let openpilot guide the steering
- Keep hands near wheel for override

## Troubleshooting

### "openpilot not found"
```bash
# Check if openpilot was installed
ls ~/openpilot

# If missing, re-run setup
./scripts/setup_system.sh
```

### "Serial port permission denied"
```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

### "No webcam detected"
```bash
# List cameras
v4l2-ctl --list-devices

# Test camera
ffplay /dev/video0
```

### "Motor doesn't respond"
1. Check ESP32 is connected: `ls /dev/ttyUSB*`
2. Test ESP32 standalone: `python3 scripts/test_esp32.py`
3. Check wiring (see `docs/wiring.md`)
4. Verify 12V power to BTS7960

### "Steering too weak/strong"
```bash
# Edit config
nano bridge/config.yaml

# Change pwm_scale:
pwm_scale: 100  # Weaker
pwm_scale: 200  # Stronger
```

## Tips

### Auto-Start on Boot

During setup, select "yes" to create systemd service. Then:
```bash
sudo systemctl enable openpilot-steering
```
System starts automatically when you power on!

### For Raspberry Pi

Mount in your car, connect to power:
- 5V USB-C for Raspberry Pi
- 12V for motor driver
- USB webcam

Boot sequence:
1. Raspberry Pi powers on
2. System auto-starts (if enabled)
3. Ready to drive in ~60 seconds

### View Logs

```bash
# If running as service
journalctl -u openpilot-steering -f

# If running manually
python3 launch.py
# Output shows on screen
```

## Safety Checklist

- [ ] Always keep hands near steering wheel
- [ ] Test in safe environment first
- [ ] Start with low `pwm_scale` (100-150)
- [ ] Have emergency stop method ready
- [ ] Monitor system during initial drives
- [ ] Comply with local laws

## Next Steps

Once comfortable:
1. Fine-tune `pwm_scale` for your vehicle
2. Adjust `stream_hz` for responsiveness
3. Optimize motor mount for better grip
4. Consider adding kill switch for emergency stop

## Getting Help

- **Documentation**: See `README.md`, `docs/INTEGRATION.md`
- **Openpilot Questions**: https://discord.comma.ai
- **Hardware Issues**: Check `docs/wiring.md`
- **Software Issues**: Run with `--debug` flag

---

**That's it!** You now have a working LKAS system. 🎉
