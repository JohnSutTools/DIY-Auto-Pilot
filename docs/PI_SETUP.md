# Raspberry Pi Installation Guide

## Hardware Requirements
- **Raspberry Pi 2 Model B** (or newer)
- **SD Card**: 32GB+ (recommended 64GB)
- **Camera**: USB webcam (720p+) or Pi Camera Module
- **Power**: 5V 2.5A+ power supply
- **Optional**: ESP32-S3 DevKitC-1 for hardware testing

## ⚠️ Important: Raspberry Pi 2 Performance Notes

The Raspberry Pi 2 Model B has:
- **1GB RAM** - Openpilot ML models will run but slower
- **ARMv7 CPU** - Limited performance for real-time vision processing
- **Expected Performance**: 5-10 FPS (vs 20 FPS on Pi 4)

**This setup IS designed to run the complete system (vision + steering) on Pi 2 for testing.**

Performance expectations:
- ✅ **Will work** - All components functional
- ⚠️ **Slower processing** - Reduced frame rate
- ⚠️ **Delayed response** - ~200-500ms latency
- 💡 **Acceptable for bench testing and initial validation**

Optimizations applied:
1. Reduced ML model resolution
2. Lower frame rate (10 FPS target)
3. Increased swap space
4. Disabled unnecessary services

## Installation Steps

### Option 1: One-Command Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/JohnSutTools/DIY-Auto-Pilot/main/scripts/pi_setup.sh | bash
```

### Option 2: Manual Installation

#### Step 1: Prepare Raspberry Pi OS

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install basic dependencies
sudo apt install -y git curl wget build-essential python3-pip
```

#### Step 2: Clone Repository

```bash
cd ~
git clone https://github.com/JohnSutTools/DIY-Auto-Pilot.git steering-actuator
cd steering-actuator
```

#### Step 3: Run Setup Script

```bash
chmod +x scripts/pi_setup.sh
./scripts/pi_setup.sh
```

This will:
- Install all system dependencies
- Clone and build openpilot (optimized for Pi 2)
- Compile ML models with GPU if available (90-120 min on Pi 2)
- Set up the bridge for steering control
- Configure webcam support
- Apply Pi 2 performance optimizations automatically

#### Step 4: Test the System

```bash
# Test bridge in mock mode (no hardware needed)
cd ~/steering-actuator
python3 launch.py
```

## Configuration

### Enable Mock Mode (Testing without ESP32)

Edit `bridge/config.yaml`:
```yaml
mock_mode: true  # Set to false when ESP32 connected
serial_port: /dev/ttyUSB0
baud_rate: 115200
pwm_scale: 150
pwm_cap: 255
stream_hz: 20
```

### Connect ESP32

1. Flash `firmware/steering_motor/steering_motor.ino` to ESP32
2. Connect ESP32 via USB
3. Find device: `ls /dev/ttyUSB* /dev/ttyACM*`
4. Update `serial_port` in config.yaml
5. Set `mock_mode: false`

### Camera Setup

**USB Webcam:**
```bash
# Check device
ls /dev/video*

# Should show: /dev/video0
```

**Pi Camera Module:**
```bash
# Enable camera in raspi-config
sudo raspi-config
# Navigate to: Interface Options -> Camera -> Enable

# Reboot
sudo reboot
```

## Running the System

### Full System (Openpilot + Bridge)

```bash
cd ~/steering-actuator
python3 launch.py
```

### Bridge Only (Manual openpilot)

```bash
cd ~/steering-actuator/bridge
python3 op_serial_bridge.py --config config.yaml --debug
```

### Test Steering Commands

```bash
cd ~/steering-actuator/scripts
python3 test_with_webcam.py
```

## Performance Optimization for Pi 2

### Reduce ML Model Resolution

Edit `~/openpilot/selfdrive/modeld/runners/runmodel_pyx.py`:
- Reduce input image size
- Lower frame rate (10-15 FPS instead of 20)

### Disable Unused Services

```bash
# Stop unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon
```

### Overclock (Carefully!)

Edit `/boot/config.txt`:
```
arm_freq=1000
core_freq=500
sdram_freq=500
over_voltage=2
```

**Warning**: Monitor temperature with `vcgencmd measure_temp`

## Troubleshooting

### Out of Memory Errors

```bash
# Increase swap space
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Change: CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Camera Not Detected

```bash
# USB camera
sudo apt install v4l-utils
v4l2-ctl --list-devices

# Pi Camera
vcgencmd get_camera
# Should show: supported=1 detected=1
```

### Serial Port Permission

```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Reboot or log out/in
sudo reboot
```

### Slow Performance

Consider **Bridge-Only Mode**:
1. Run openpilot on laptop/desktop
2. Run bridge on Pi 2
3. Connect via network:

Edit `bridge/config.yaml`:
```yaml
openpilot_host: "192.168.1.100:8002"  # Laptop IP
```

## Next Steps

1. ✅ Install system on Pi 2
2. ✅ Test in mock mode
3. 🔌 Connect ESP32 and motor hardware
4. 🚗 Bench test steering actuator
5. 🎯 Integrate with vehicle (safety testing!)

## Remote Access (Recommended)

### Enable SSH
```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

### Find Pi IP
```bash
hostname -I
```

### Connect from laptop
```bash
ssh pi@<PI_IP_ADDRESS>
```

## Support

- **GitHub Issues**: https://github.com/JohnSutTools/DIY-Auto-Pilot/issues
- **Logs**: `~/steering-actuator/logs/`
- **System Info**: `~/steering-actuator/scripts/check_paths.py`

## Safety Warning ⚠️

This system controls vehicle steering. Before vehicle testing:
1. Complete thorough bench testing
2. Test in safe, controlled environment
3. Have manual override ready
4. Never test on public roads
5. Understand local laws and regulations
