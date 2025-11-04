# Openpilot External Steering Actuator - AI Agent Instructions

## Project Architecture

**Goal**: Unified LKAS system running openpilot + steering bridge on laptop/Raspberry Pi with USB webcam.
Memory locked:

All openpilot and DIY-Auto-Pilot code is LOCAL in: c:\Users\John\OneDrive - Sutton Tools Pty Ltd\Private\DIY Auto Pilot\
Research/read code locally from Windows filesystem
After making changes, SCP files to VM at user@192.168.68.115
Execute everything via SSH on the VM

**Signal flow**: `USB webcam -> openpilot (LKAS) -> Python bridge -> ESP32-S3 -> BTS7960 -> motor`

### System Type
- **Standalone, integrated system** - not a separate bridge
- **Single launcher** (`launch.py`) starts everything together
- **LKAS only** - no longitudinal control, only steering
- **No comma device needed** - uses USB webcam

### Components
- **Host**: Laptop or Raspberry Pi 4+ (Ubuntu/Pi OS)
- **Camera**: USB webcam (720p+)
- **Openpilot**: Built-in, launches with webcam support
- **Bridge**: `op_serial_bridge.py` - subscribes via `cereal.messaging`, sends serial commands
- **MCU**: ESP32-S3 DevKitC-1 (USB-C, 20 kHz PWM via LEDC)
- **Driver**: BTS7960 H-bridge (bidirectional PWM control)
- **Motor**: JGB37-545 12V 316 RPM gearmotor

## Code Structure

```
├── launch.py               # MAIN LAUNCHER - starts everything
├── firmware/               # ESP32-S3 Arduino/ESP-IDF code
│   └── steering_motor/    # Main firmware sketch
├── bridge/                 # Python bridge process
│   ├── op_serial_bridge.py # Main bridge logic
│   └── config.yaml        # pwm_scale, pwm_cap, stream_hz
├── scripts/
│   ├── setup_system.sh    # Complete system setup
│   ├── test_esp32.py      # ESP32 testing
│   └── calibrate.py       # PWM calibration
└── docs/                  # Wiring diagrams, integration notes
```

**Openpilot lives separately at `~/openpilot/` and is launched by `launch.py`**

## Critical Implementation Details

### Serial Protocol (ESP32 <-> Bridge)
- **Format**: ASCII line-based, newline-terminated
- **Commands**: 
  - `S:<value>` where value in [-pwm_cap, +pwm_cap] (e.g., `S:+120\n`, `S:-80\n`)
  - `STOP\n` - emergency halt
- **Baud**: 115200 (standard, adjustable)

### Openpilot Message Priority
1. **Primary**: `carControl.actuators.steer` (range: -1.0 to +1.0)
2. **Fallback**: `controlsState.steer` (if carControl unavailable)

### Scaling Logic
```python
# Bridge scales normalized steer to PWM
pwm_value = int(steer_command * pwm_scale)
pwm_value = clamp(pwm_value, -pwm_cap, +pwm_cap)
```

### Configuration (config.yaml)
- `pwm_scale`: Multiplier for steer -> PWM (tune for steering authority)
- `pwm_cap`: Absolute max PWM value (safety limit, typically 255)
- `stream_hz`: Bridge update rate (10-50 Hz recommended)
- `serial_port`: ESP32 device path (e.g., `/dev/ttyUSB0`)

## Development Workflow

### Initial Setup (One Time)
```bash
./scripts/setup_system.sh  # Installs openpilot + all dependencies
```

### Daily Development
```bash
python3 launch.py  # Starts openpilot + bridge together
```

### Initial Bring-up
1. **Setup system**: Run `setup_system.sh` (15-30 min, includes openpilot build)
2. **Flash ESP32**: Upload firmware via Arduino IDE
3. **Test ESP32**: `python3 scripts/test_esp32.py --interactive`
4. **Launch system**: `python3 launch.py`
5. **Calibration**: Adjust `pwm_scale` in `config.yaml` until steering feel matches

### Testing Commands
```bash
# Test ESP32 standalone
python3 scripts/test_esp32.py --port /dev/ttyUSB0 --interactive

# Launch complete system
python3 launch.py

# Manual bridge only (if openpilot already running)
python3 bridge/op_serial_bridge.py --debug --config bridge/config.yaml
```

## Hardware Constraints

### ESP32-S3 Pin Assignment (Firmware)
- **LPWM/RPWM**: Use LEDC channels for BTS7960 control
- **Enable pins**: Active HIGH to enable BTS7960
- **Serial**: Hardware UART (USB-C for dev, GPIO for production)

### Safety Considerations
- **Watchdog**: ESP32 must implement timeout - if no command received within 500ms, trigger STOP
- **PWM limits**: Enforce `pwm_cap` in both firmware AND bridge
- **Failsafe**: Bridge should send `STOP` on exception or disconnect

## Key Dependencies

### Python Bridge
- `cereal` (openpilot messaging library)
- `pyserial` for UART communication
- `pyyaml` for config parsing

### ESP32 Firmware
- ESP-IDF or Arduino framework
- LEDC peripheral for PWM generation

## Conventions

### Coordinate System
- **Positive steer/PWM**: Clockwise rotation (right turn)
- **Negative steer/PWM**: Counter-clockwise rotation (left turn)
- **Zero**: Neutral/straight

### Error Handling
- Bridge logs all exceptions to stdout/file but continues running
- ESP32 resets to STOP state on malformed commands
- Both components implement graceful degradation

## Reference Files
- `project-overview.md` - Detailed system design and bring-up plan
- `firmware/README.md` - ESP32 build and flash instructions
- `bridge/README.md` - Python setup and usage
