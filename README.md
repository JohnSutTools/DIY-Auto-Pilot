# Openpilot External Steering Actuator

**Complete LKAS (Lane Keeping Assist) system running on laptop or Raspberry Pi with USB webcam.**

Bridge openpilot's lateral control to an external steering motor for a 2018 Honda Civic RS.

## 🚀 Start Here

**Choose your path:**

- 🎬 **Just want to SEE it?** → [`VISUAL_DEMO.md`](VISUAL_DEMO.md) - *2-minute demo, no hardware needed!*
- 🏃 **Ready to build?** → [`QUICKSTART.md`](QUICKSTART.md) - *Daily usage guide*
- 📚 **Need setup help?** → [`docs/UBUNTU_SETUP.md`](docs/UBUNTU_SETUP.md) - *Complete walkthrough*

## System Overview

**Unified, standalone system that runs on a laptop or Raspberry Pi with a USB webcam.**

```
USB Webcam → Openpilot (LKAS only)
              ↓ carControl messages
         op_serial_bridge.py
              ↓ Serial commands (S:<pwm>)
           ESP32-S3
              ↓ PWM signals (20 kHz)
         BTS7960 H-bridge
              ↓ Motor power
         JGB37-545 motor (316 RPM)
              ↓ Physical force
         Steering wheel roller
```

**Everything runs together as a single integrated system - just launch and go!**

## Hardware Components

- **Host**: Laptop running openpilot (Ubuntu/Debian)
- **Bridge**: Python process (`op_serial_bridge.py`)
- **Controller**: ESP32-S3 DevKitC-1 (USB-C)
- **Driver**: BTS7960 H-bridge motor driver
- **Motor**: JGB37-545 12V 316 RPM gearmotor
- **Power**: 12V from vehicle (fused), 5V for ESP32

## Hardware Requirements

- **Computer**: Laptop or Raspberry Pi 4 (4GB+ RAM recommended)
- **OS**: Ubuntu 20.04/22.04 or Raspberry Pi OS
- **Camera**: USB webcam (720p minimum, 1080p recommended)
- **Controller**: ESP32-S3 DevKitC-1
- **Motor Driver**: BTS7960 H-bridge
- **Motor**: JGB37-545 12V 316 RPM gearmotor
- **Power**: 12V (from vehicle battery, fused)
- **Vehicle**: 2018 Honda Civic RS (LKAS compatible)

## Quick Setup

### On Ubuntu / Raspberry Pi

**🚀 One-Command Setup:**
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnSutTools/DIY-Auto-Pilot/main/scripts/ubuntu_quick_setup.sh)
```

**Or Manual:**
```bash
git clone https://github.com/JohnSutTools/DIY-Auto-Pilot.git ~/steering-actuator
cd ~/steering-actuator
./scripts/setup_system.sh
./scripts/test_simulation.sh  # Test without hardware
```

➡️ **See [`docs/UBUNTU_SETUP.md`](docs/UBUNTU_SETUP.md) for complete walkthrough**

### On Windows (Until You Get Your Pi)

**Install WSL2 + Ubuntu** (PowerShell as Administrator):
```powershell
wsl --install -d Ubuntu-22.04
```

**Then in Ubuntu terminal:**
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnSutTools/DIY-Auto-Pilot/main/scripts/ubuntu_quick_setup.sh)
```

➡️ **See [`docs/WINDOWS_WSL_SETUP.md`](docs/WINDOWS_WSL_SETUP.md) for Windows-specific guide**

**Advantages of WSL2 for development:**
- ✅ Full Linux environment on Windows
- ✅ USB device access (ESP32, webcam)
- ✅ Same setup as Raspberry Pi
- ✅ Easy migration when Pi arrives

## One-Command Setup

```bash
# Clone this repository
git clone <your-repo-url> ~/steering-actuator
cd ~/steering-actuator

# Run complete setup (installs openpilot + dependencies)
chmod +x scripts/setup_system.sh
./scripts/setup_system.sh
```

This script will:
- ✅ Install all system dependencies
- ✅ Clone and build openpilot (LKAS only mode)
- ✅ Install Python bridge dependencies
- ✅ Set up serial port access
- ✅ Configure webcam support
- ✅ Optionally create auto-start service

**That's it!** Everything is integrated and ready to run.

## Quick Start

### 1. Flash ESP32 Firmware

```bash
# Using Arduino IDE:
# - Open firmware/steering_motor/steering_motor.ino
# - Select Board: ESP32S3 Dev Module
# - Upload
```

See [`firmware/README.md`](firmware/README.md) for detailed instructions.

### 2. Configure Your System

Edit `bridge/config.yaml`:
```yaml
serial_port: /dev/ttyUSB0  # Your ESP32 device (check with: ls /dev/ttyUSB*)
pwm_scale: 150             # Start conservative, tune later
pwm_cap: 255               # Safety limit
stream_hz: 20              # Update rate
```

### 3. Test ESP32 Connection

```bash
python3 scripts/test_esp32.py --port /dev/ttyUSB0 --interactive
```

### 4. Launch Complete System

```bash
# Single command to run everything!
python3 launch.py
```

This starts:
- ✅ Openpilot with USB webcam
- ✅ LKAS-only mode (lateral control)
- ✅ Steering bridge
- ✅ Unified monitoring and control

**Press Ctrl+C to stop everything cleanly.**

## Project Structure

```
├── .github/
│   └── copilot-instructions.md  # AI agent guidance
├── bridge/                       # Python bridge application
│   ├── op_serial_bridge.py      # Main bridge logic
│   ├── config.yaml              # Configuration
│   ├── requirements.txt         # Python dependencies
│   └── README.md                # Bridge documentation
├── firmware/                     # ESP32-S3 firmware
│   ├── steering_motor/          # Arduino sketch
│   │   └── steering_motor.ino
│   └── README.md                # Firmware documentation
├── scripts/                      # Utilities
│   ├── install.sh               # Setup script
│   ├── launch.sh                # Tmux launcher
│   ├── test_esp32.py            # ESP32 testing
│   └── calibrate.py             # PWM calibration tool
├── docs/                         # Documentation (wiring, etc.)
├── project-overview.md          # Detailed system design
└── README.md                    # This file
```

## Serial Protocol

ESP32 accepts ASCII line-based commands:

- `S:<value>\n` - Set motor PWM
  - `S:+120\n` - Clockwise rotation (right turn)
  - `S:-80\n` - Counter-clockwise (left turn)
  - `S:0\n` - Neutral/stop
- `STOP\n` - Emergency halt

Range: -255 to +255 (enforced by both firmware and bridge)

## Calibration

### Initial Setup
1. Start with conservative `pwm_scale: 100` in `config.yaml`
2. Test in parked vehicle with debug mode
3. Gradually increase scale until steering feels responsive
4. Test at low speeds before normal driving

### Calibration Tool
```bash
python3 scripts/calibrate.py --config bridge/config.yaml
```

Interactive tool for adjusting PWM scaling and previewing steer→PWM mappings.

## Safety Features

### ESP32 Watchdog
- Automatically stops motor if no command received within 500ms
- Prevents runaway if bridge crashes or disconnects

### PWM Limits
- `pwm_cap` enforced in both firmware and bridge
- Hard limit of 255 (8-bit PWM)

### Graceful Degradation
- Bridge sends `STOP` on exception or shutdown
- ESP32 resets to safe state on malformed commands

## System Operation

### Auto-Start on Boot (Optional)

During setup, you can create a systemd service that starts everything automatically:

```bash
# Enable auto-start
sudo systemctl enable openpilot-steering

# Manual control
sudo systemctl start openpilot-steering   # Start
sudo systemctl stop openpilot-steering    # Stop
sudo systemctl status openpilot-steering  # Check status
journalctl -u openpilot-steering -f       # View logs
```

### Manual Launch

```bash
cd ~/steering-actuator
python3 launch.py
```

The unified launcher will:
1. Find and start openpilot with webcam
2. Configure LKAS-only mode
3. Start the steering bridge
4. Monitor all processes
5. Display combined output

### What You'll See

```
========================================
Openpilot Steering Actuator System
========================================

🚗 Starting openpilot...
✓ Openpilot started
  Waiting for openpilot to initialize (10s)...

🔌 Starting steering bridge...
✓ Bridge started

========================================
System running - Press Ctrl+C to stop
========================================

[openpilot] Webcam initialized: /dev/video0
[openpilot] LKAS mode enabled
[bridge] ESP32 connected: ESP32-S3 Steering Controller Ready
[bridge] Steer: +0.234 -> PWM: +35
[openpilot] Lane detected, engaged
...
```

## Testing

### 1. Bench Test (No Car)
```bash
# Test ESP32 only
python3 scripts/test_esp32.py --port /dev/ttyUSB0 --interactive
```

### 2. Webcam Test
```bash
# Check camera is detected
v4l2-ctl --list-devices

# Test with openpilot
cd ~/openpilot
USE_WEBCAM=1 ./launch_openpilot.sh
```

### 3. Full System Test (Parked Car)
```bash
# Mount motor on steering wheel
# Sit in driver's seat
python3 launch.py

# Observe:
# - Webcam feed appears
# - Lane detection activates
# - Motor responds to steering corrections
```

## Troubleshooting

### Serial Port Access
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER
# Log out and back in

# Find serial port
ls /dev/ttyUSB* /dev/ttyACM*
```

### cereal/openpilot Not Found
```bash
# Add openpilot to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:~/openpilot"
```

### Motor Not Responding
1. Check 12V power to BTS7960
2. Verify ESP32 firmware is running (check serial output)
3. Test with manual commands: `python3 -c "import serial; s=serial.Serial('/dev/ttyUSB0', 115200); s.write(b'S:+120\n')"`
4. Check wiring (see `firmware/README.md`)

### Steering Too Aggressive/Weak
- Adjust `pwm_scale` in `config.yaml`
- Lower values = gentler, higher = more aggressive
- Use calibration tool: `python3 scripts/calibrate.py`

## Documentation

### Getting Started
- **[`QUICKSTART.md`](QUICKSTART.md) - Start here for first-time setup** 🚀
- **[`docs/UBUNTU_SETUP.md`](docs/UBUNTU_SETUP.md) - Fresh Ubuntu install walkthrough** 🐧
- **[`docs/WINDOWS_WSL_SETUP.md`](docs/WINDOWS_WSL_SETUP.md) - Run on Windows (WSL2)** 🪟
- **[`docs/TESTING.md`](docs/TESTING.md) - Complete testing guide (simulation)** 🧪

### System Details
- [`docs/INTEGRATION.md`](docs/INTEGRATION.md) - How openpilot integrates
- [`firmware/README.md`](firmware/README.md) - ESP32 setup, wiring, flashing
- [`bridge/README.md`](bridge/README.md) - Bridge installation, usage, troubleshooting
- [`docs/wiring.md`](docs/wiring.md) - Hardware wiring diagrams
- [`project-overview.md`](project-overview.md) - Detailed system design and architecture
- [`.github/copilot-instructions.md`](.github/copilot-instructions.md) - AI agent guidance

## Development

### Running in Debug Mode
```bash
# Bridge with verbose output
python3 bridge/op_serial_bridge.py --debug --config bridge/config.yaml

# ESP32 serial monitor
screen /dev/ttyUSB0 115200
# or
arduino-cli monitor -p /dev/ttyUSB0
```

### Modifying Firmware
1. Edit `firmware/steering_motor/steering_motor.ino`
2. Adjust pin assignments if needed
3. Upload via Arduino IDE or ESP-IDF
4. Test with `scripts/test_esp32.py`

### Modifying Bridge
1. Edit `bridge/op_serial_bridge.py`
2. Update `config.yaml` if adding new parameters
3. Test with openpilot replay data

## License

[Your License Here]

## Contributing

Contributions welcome! Please:
1. Test thoroughly in safe environment
2. Document any hardware/configuration changes
3. Follow existing code style
4. Update relevant README files

## Disclaimer

**Safety Warning**: This system controls vehicle steering. Always:
- Test in safe, controlled environments
- Keep manual override available
- Start with low speeds
- Monitor system behavior closely
- Follow all local laws and regulations
