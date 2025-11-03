# Openpilot Serial Bridge

Python bridge process that connects openpilot's lateral control output to an external steering motor via ESP32.

## Installation

### Prerequisites
- Python 3.8+
- Openpilot installed (for cereal messaging library)
- ESP32-S3 connected via USB

### Setup
```bash
cd bridge
pip3 install -r requirements.txt
```

**Note**: If `cereal` isn't available via pip, you need openpilot installed:
```bash
# Clone openpilot if not already present
cd ~
git clone https://github.com/commaai/openpilot.git
cd openpilot
scons -j$(nproc)

# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:~/openpilot"
```

## Configuration

Edit `config.yaml`:

```yaml
serial_port: /dev/ttyUSB0  # Your ESP32 device
pwm_scale: 150             # Tune for steering authority
pwm_cap: 255               # Safety limit
stream_hz: 20              # Update rate
```

### Finding Serial Port
```bash
# List USB devices (before connecting ESP32)
ls /dev/ttyUSB* /dev/ttyACM*

# Connect ESP32, then list again
ls /dev/ttyUSB* /dev/ttyACM*

# Grant permissions
sudo usermod -a -G dialout $USER
# Log out and back in for group changes to take effect
```

## Usage

### Basic Operation
```bash
python3 op_serial_bridge.py --config config.yaml
```

### Debug Mode
```bash
python3 op_serial_bridge.py --config config.yaml --debug
```

Debug mode shows:
- Each steering command and PWM value
- Serial communication details
- ESP32 responses and errors

## Testing Without Openpilot

### Test Serial Communication
```bash
# Send manual commands to ESP32
python3 -c "import serial; s=serial.Serial('/dev/ttyUSB0', 115200); s.write(b'S:+120\n')"
```

### Simulate Openpilot Messages
```bash
# Use openpilot replay with recorded route
cereal-replay <route_name> --services carControl
```

## Message Priority

1. **carControl.actuators.steer** (primary)
   - Range: -1.0 (full left) to +1.0 (full right)
   - Direct output from openpilot's lateral controller

2. **controlsState.steer** (fallback)
   - Used if carControl unavailable
   - Same range and meaning

## Calibration

### Initial Calibration Process

1. **Start conservative**: Set `pwm_scale: 100`

2. **Test with parked vehicle**:
   ```bash
   python3 op_serial_bridge.py --debug --config config.yaml
   ```

3. **Monitor steering response**:
   - Too weak? Increase `pwm_scale` by 25
   - Too aggressive? Decrease by 25

4. **Repeat until comfortable**

5. **Test at slow speeds** before normal driving

### Safety Notes
- ALWAYS test in safe environment first
- Keep manual override ready
- Monitor debug output during initial runs
- Start with lower speeds

## Troubleshooting

**Bridge can't find cereal:**
```bash
export PYTHONPATH="${PYTHONPATH}:~/openpilot"
```

**Serial port permission denied:**
```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

**No steering commands received:**
- Verify openpilot is running and engaged
- Check that vehicle is supported and calibrated
- Use `cereal-replay` to test with known-good data

**Motor responds erratically:**
- Check `pwm_cap` - may be too high
- Verify ESP32 firmware is running (check serial output)
- Test ESP32 standalone with manual commands

**Watchdog triggering on ESP32:**
- Increase `stream_hz` in config.yaml
- Check USB cable quality
- Monitor bridge debug output for delays
