# System Integration Details

## Architecture Overview

**This is a unified, standalone system** that runs openpilot and your steering bridge together as an integrated package.

```
Laptop/Raspberry Pi
├── USB Webcam → Openpilot (vision + LKAS)
│                    ↓
│                Steering commands
│                    ↓
└── Bridge (Python) → ESP32 → Motor → Steering Wheel
```

**Key Points:**
- ✅ Everything runs on ONE device (laptop or Raspberry Pi)
- ✅ No comma device needed - uses USB webcam
- ✅ LKAS only (Lane Keeping Assist System)
- ✅ Unified launcher starts everything together
- ✅ Clean shutdown with Ctrl+C

## Installation

### Automated Setup (Recommended)

**One command installs everything:**

```bash
cd ~/steering-actuator
./scripts/setup_system.sh
```

This will:
1. Install system dependencies (build tools, libraries)
2. Clone and build openpilot (release3 branch)
3. Install Python bridge dependencies
4. Configure USB webcam support
5. Set up serial port access
6. Optionally create auto-start service

**Time required:** 15-30 minutes (mostly openpilot build time)

### Manual Launch

```bash
# Single command runs everything!
python3 launch.py
```

The launcher automatically:
- Finds your openpilot installation
- Starts openpilot with webcam enabled
- Configures LKAS-only mode (no longitudinal control)
- Starts steering bridge
- Monitors all processes
- Provides unified output

**Stop everything:** Press Ctrl+C once - clean shutdown of all components

## Understanding Openpilot's Control Flow

### What Openpilot Provides

1. **Vision Processing**: Cameras → lane detection, lead car tracking
2. **Planning**: Route planning, speed control decisions
3. **Lateral Control**: Calculates steering angle needed
4. **Message Publishing**: Outputs `carControl` messages via cereal

### What Your Bridge Does

1. **Subscribes** to openpilot's control messages
2. **Extracts** steering command (normalized -1 to +1)
3. **Scales** to motor PWM range
4. **Sends** to ESP32 via serial

### Message Structure

```python
# What openpilot publishes
carControl = {
    'actuators': {
        'steer': 0.45,        # -1.0 to +1.0 (you use this)
        'accel': 0.5,         # Acceleration (not used)
        'gas': 0.2,           # Gas pedal (not used)
        'brake': 0.0          # Brake (not used)
    },
    'enabled': True,          # Whether openpilot is engaged
    # ... many other fields
}
```

## Project Directory Structure

Keep your project separate from openpilot for clean separation:

```
~/
├── openpilot/                    # Main openpilot repository
│   ├── selfdrive/               # Core driving logic
│   ├── cereal/                  # Message definitions
│   ├── tools/                   # Development tools
│   └── launch_openpilot.sh      # Main launcher
│
└── steering_actuator/            # Your project (this repo)
    ├── bridge/                   # Your Python bridge
    ├── firmware/                 # ESP32 code
    └── scripts/                  # Your utilities
```

## Configuration for Your 2018 Honda Civic RS

### Verify Openpilot Support

```bash
# Check if your car is supported
cd ~/openpilot
cat docs/CARS.md | grep -i "honda civic"
```

The Honda Civic is well-supported by openpilot. However, **your external motor setup bypasses the normal steering interface.**

### Important Considerations

**Your Setup is Unconventional:**
- Openpilot normally sends CAN bus commands to the car's steering system
- You're using a **physical motor on top of the steering wheel**
- This is a **development/testing setup**, not production

**Advantages:**
- No modification to vehicle wiring
- Easy to install/remove
- Good for testing openpilot integration

**Limitations:**
- Not as precise as direct CAN bus control
- Mechanical lag and friction
- Requires calibration for your specific mount

## Testing Workflow

### 1. Test ESP32 Standalone
```bash
python3 scripts/test_esp32.py --port /dev/ttyUSB0 --interactive
```

### 2. Test Bridge with Replay Data
```bash
# Download sample route (one-time)
cd ~/openpilot
tools/replay/route_downloader.py '<route-name>'

# Replay
tools/replay/replay '<route-name>|0'

# In another terminal: run bridge
cd ~/steering_actuator
python3 bridge/op_serial_bridge.py --debug --config bridge/config.yaml
```

### 3. Test in Parked Vehicle
- Mount motor on steering wheel
- Run openpilot in your car
- Run bridge on laptop
- Verify motor responds to lane detection

### 4. Test at Low Speed
- Start in empty parking lot
- Monitor debug output
- Verify steering authority
- Tune `pwm_scale` as needed

## Calibration for Your Setup

Your external motor needs different calibration than direct CAN bus control:

```yaml
# Start very conservative
pwm_scale: 50   # Much lower than default
pwm_cap: 150    # Limit maximum power

# Test and gradually increase
pwm_scale: 75
pwm_scale: 100
pwm_scale: 150  # Typical final value
```

## Common Issues & Solutions

### "cereal module not found"
```bash
export PYTHONPATH="${PYTHONPATH}:~/openpilot"
```

### "No carControl messages"
- Openpilot must be **engaged** (lateral control active)
- Vehicle must be moving >5 mph typically
- Use replay data for testing without driving

### "Motor doesn't respond"
- Check ESP32 is connected and firmware loaded
- Verify serial port in config.yaml
- Test ESP32 standalone first

### "Steering too aggressive/weak"
- Adjust `pwm_scale` in config.yaml
- Use calibration tool: `python3 scripts/calibrate.py`
- Consider mechanical leverage of your mount

## Development Tips

### Debug Both Systems
```bash
# Terminal 1: Openpilot with logs
cd ~/openpilot
PASSIVE=1 ./launch_openpilot.sh

# Terminal 2: Bridge with debug
cd ~/steering_actuator
python3 bridge/op_serial_bridge.py --debug --config bridge/config.yaml

# Terminal 3: Monitor messages
cd ~/openpilot
tools/replay/logreader '<route>|<segment>' | grep carControl
```

### Log Everything
```bash
# Bridge logs
python3 bridge/op_serial_bridge.py --debug 2>&1 | tee bridge.log

# ESP32 logs
screen -L /dev/ttyUSB0 115200
```

## Safety Warnings

⚠️ **This is an experimental setup:**

1. **Physical Override**: Keep hands near wheel at all times
2. **Kill Switch**: Have emergency stop button ready
3. **Start Slow**: Test extensively at parking lot speeds
4. **Monitor Always**: Watch debug output during initial runs
5. **Legal Compliance**: Ensure your setup complies with local laws

## Next Steps

1. ✅ Install openpilot: `git clone https://github.com/commaai/openpilot.git`
2. ✅ Build openpilot: `cd openpilot && scons -j$(nproc)`
3. ✅ Test with replay: Use recorded route data
4. ✅ Flash ESP32: Upload firmware from `firmware/steering_motor/`
5. ✅ Connect bridge: Run your bridge with openpilot
6. ✅ Bench test: Verify motor responds to replay data
7. ✅ Vehicle test: Mount and test in parked car
8. ✅ Low-speed test: Empty parking lot validation
9. ✅ Calibrate: Tune pwm_scale for your setup

## Resources

- [Openpilot Documentation](https://docs.comma.ai/)
- [Openpilot Discord](https://discord.comma.ai/)
- [Replay Tool Guide](https://github.com/commaai/openpilot/tree/master/tools/replay)
- [Car Support List](https://github.com/commaai/openpilot/blob/master/docs/CARS.md)
