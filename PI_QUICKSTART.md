# Raspberry Pi Quick Start

## 🚀 One-Line Install

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnSutTools/DIY-Auto-Pilot/main/scripts/pi_setup.sh)
```

## ⚙️ Manual Install

```bash
# 1. Download setup script
curl -O https://raw.githubusercontent.com/JohnSutTools/DIY-Auto-Pilot/main/scripts/pi_setup.sh

# 2. Make executable
chmod +x pi_setup.sh

# 3. Run
./pi_setup.sh
```

## 📋 What Gets Installed

- System dependencies (build tools, libraries)
- Openpilot (full installation)
- Steering bridge components
- Camera support (USB webcam + Pi Camera)
- Serial communication tools

## ⏱️ Installation Time

- **Raspberry Pi 4**: 30-45 minutes
- **Raspberry Pi 3**: 45-90 minutes  
- **Raspberry Pi 2**: 90-120 minutes

**Note**: Pi 2 installation includes automatic performance optimizations for complete system operation (vision + steering control). Expect 5-10 FPS performance, suitable for testing.

## 🧪 First Test

After installation and reboot:

```bash
cd ~/steering-actuator/scripts
PYTHONPATH=~/openpilot ~/openpilot/.venv/bin/python test_integration.sh
```

You should see:
```
[SIMULATOR] Publishing steering commands...
[BRIDGE] MOCK: S:+72  Steer: +0.481 -> PWM: +72
[BRIDGE] MOCK: S:-57  Steer: -0.385 -> PWM: -57
```

This confirms the communication pipeline is working!

## 🔌 Connect Hardware

1. Flash ESP32 with `firmware/steering_motor/steering_motor.ino`
2. Connect ESP32 via USB to Pi
3. Find device: `ls /dev/ttyUSB*`
4. Edit `bridge/config.yaml`:
   ```yaml
   mock_mode: false
   serial_port: /dev/ttyUSB0  # Your device
   ```

## 📹 Camera Setup

**USB Webcam**: Plug and play - should appear as `/dev/video0`

**Pi Camera Module**:
```bash
sudo raspi-config
# Navigate to: Interface Options -> Camera -> Enable
sudo reboot
```

## 🆘 Troubleshooting

**Serial permission denied:**
```bash
sudo usermod -a -G dialout $USER
sudo reboot
```

**Camera not found:**
```bash
# Check USB cameras
ls /dev/video*

# Check Pi Camera
vcgencmd get_camera
```

**Out of memory:**
```bash
# Increase swap
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set: CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

## 📖 Full Documentation

See `docs/PI_SETUP.md` for complete guide including:
- Performance optimization
- Remote access setup
- Network mode configuration
- Safety guidelines
