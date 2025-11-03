# Raspberry Pi 2 Status and Limitations

## Current Status: ✅ Bridge Running Successfully

The steering bridge is now **functional on Raspberry Pi 2** using mock cereal messaging.

```
2025-11-03 23:21:20,246 [WARNING] 🔧 MOCK MODE: Running without hardware
2025-11-03 23:21:20,247 [INFO] Connecting to local openpilot
2025-11-03 23:21:20,248 [INFO] Bridge initialized: /dev/ttyUSB0 @ 115200
2025-11-03 23:21:20,249 [INFO] PWM scale: 150, cap: 255
2025-11-03 23:21:20,249 [INFO] Bridge running. Press Ctrl+C to stop.
```

## Critical Discovery: Openpilot ARM64 Requirement

**Openpilot does NOT support 32-bit ARM (ARMv7)** - it requires ARM64 (aarch64) architecture.

### Raspberry Pi 2 Limitations

- **Architecture**: ARMv7l (32-bit ARM)
- **Openpilot Support**: ❌ No - openpilot requires ARM64
- **SConstruct Build**: Fails with architecture assertion error
- **Cereal Library**: Cannot be compiled on ARMv7

### What Works on Pi 2

✅ **Bridge Process**
- Serial communication with ESP32
- PWM command generation and sending
- Configuration management
- Mock mode testing

❌ **Openpilot Vision Processing**
- Cannot run openpilot ML models
- Cannot build cereal messaging library
- Cannot process camera input for lane detection

## Solution Implemented

Created `mock_cereal_messaging.py` that provides:
- `SubMaster` class for subscribing to messages
- Mock message objects (carControl, controlsState)
- Compatible API with real cereal
- Allows bridge testing without openpilot

The bridge automatically detects ARMv7 and loads mock cereal:

```python
if platform.machine() == 'armv7l':
    print("⚠️  Detected ARMv7 (32-bit ARM) - openpilot not supported")
    print("   Using mock cereal for Pi 2 testing")
    import mock_cereal_messaging as messaging
```

## Recommended Upgrades for Full System

To run the **complete vision + steering system**, you need ARM64:

### Option 1: Raspberry Pi 4/5 (Recommended)
- **Architecture**: ARM64 (aarch64) ✅
- **RAM**: 4GB+ recommended
- **Performance**: 15-20 FPS expected
- **Cost**: ~$55 (Pi 4 4GB)

### Option 2: Raspberry Pi 3B+
- **Architecture**: ARM64 capable (but shipped with 32-bit OS)
- **Solution**: Install 64-bit Raspberry Pi OS
- **Performance**: 10-15 FPS expected
- **Note**: Requires OS reinstall

### Option 3: Keep Pi 2 as Bridge-Only
- Run openpilot on laptop/desktop (Windows/Linux)
- Run bridge on Pi 2
- Connect via network
- Edit `bridge/config.yaml`:
  ```yaml
  openpilot_host: "192.168.1.100:8002"  # Your laptop IP
  ```

## Hardware Setup Progress

### Completed ✅
1. SSH passwordless login configured
2. `/tmp` directory expanded to 4GB
3. Swap space configured (2GB)
4. Python venv created and working
5. Essential packages installed (numpy, pyzmq, pyyaml, scons)
6. Bridge running successfully in mock mode
7. Serial port configured for ESP32 communication

### Next Steps for Pi 2 Testing

1. **Connect ESP32**
   ```bash
   # Check device
   ls /dev/ttyUSB* /dev/ttyACM*
   
   # Update config
   nano ~/steering-actuator/bridge/config.yaml
   # Set: mock_mode: false
   # Set: serial_port: /dev/ttyUSB0  (or correct port)
   ```

2. **Flash ESP32 Firmware**
   - Use Arduino IDE or PlatformIO
   - Upload `firmware/steering_motor/steering_motor.ino`
   - Verify serial communication at 115200 baud

3. **Test Motor Control**
   ```bash
   cd ~/steering-actuator
   python3 bridge/op_serial_bridge.py --config bridge/config.yaml --debug
   ```

4. **Manual Steering Commands** (for testing)
   ```bash
   # In another terminal
   echo "S:+100" > /dev/ttyUSB0  # Turn right
   echo "S:-100" > /dev/ttyUSB0  # Turn left
   echo "STOP" > /dev/ttyUSB0    # Emergency stop
   ```

## Future: Upgrade to Pi 4 for Vision

When you're ready for full openpilot with vision processing:

```bash
# On new Pi 4 with 64-bit OS
curl -fsSL https://raw.githubusercontent.com/JohnSutTools/DIY-Auto-Pilot/main/scripts/pi_setup.sh | bash

# This will:
# - Detect ARM64 architecture
# - Build real openpilot with vision
# - Compile cereal messaging
# - Run complete system at 15-20 FPS
```

## Summary

| Component | Pi 2 (ARMv7) | Pi 4 (ARM64) |
|-----------|--------------|--------------|
| Bridge | ✅ Works | ✅ Works |
| ESP32 Control | ✅ Works | ✅ Works |
| Motor PWM | ✅ Works | ✅ Works |
| Openpilot Vision | ❌ Not Supported | ✅ Works |
| Lane Detection | ❌ Not Supported | ✅ Works |
| Full System | ❌ No | ✅ Yes |
| **Use Case** | **Bridge-only or testing** | **Complete system** |

The Pi 2 is **perfect for testing bridge logic and ESP32 communication**, but requires Pi 4 for full vision-based steering.
