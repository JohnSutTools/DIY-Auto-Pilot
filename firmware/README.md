# ESP32-S3 Steering Motor Firmware

## Hardware Setup

### Connections
```
ESP32-S3         BTS7960
---------        -------
GPIO 5    -->    RPWM (right PWM input)
GPIO 6    -->    LPWM (left PWM input)
GPIO 7    -->    R_EN (right enable)
GPIO 8    -->    L_EN (left enable)
GND       -->    GND

BTS7960          Motor
-------          -----
M+        -->    Motor + (red)
M-        -->    Motor - (black)
VCC       -->    12V (vehicle power, fused)
GND       -->    GND
```

### Pin Configuration
- **RPWM (GPIO 5)**: Forward/clockwise rotation PWM
- **LPWM (GPIO 6)**: Reverse/counter-clockwise rotation PWM
- **R_EN/L_EN (GPIO 7/8)**: Active HIGH enables for BTS7960

## Building & Flashing

### Arduino IDE
1. Install ESP32 board support: https://docs.espressif.com/projects/arduino-esp32/
2. Select **ESP32S3 Dev Module** from Tools > Board
3. Connect ESP32-S3 via USB-C
4. Select correct COM port
5. Upload sketch

### ESP-IDF (Alternative)
```bash
cd firmware/steering_motor
idf.py build
idf.py -p /dev/ttyUSB0 flash monitor
```

## Serial Protocol

### Commands
- `S:<value>\n` - Set motor PWM (-255 to +255)
  - Positive: Clockwise (right turn)
  - Negative: Counter-clockwise (left turn)
  - Zero: Neutral
- `STOP\n` - Emergency stop

### Examples
```bash
# Test with Python
python3 -c "import serial; s=serial.Serial('/dev/ttyUSB0', 115200); s.write(b'S:+120\n')"

# Test with screen
screen /dev/ttyUSB0 115200
S:+100
S:-100
STOP
```

## Safety Features

### Watchdog Timer
- If no command received within 500ms, motor automatically stops
- Prevents runaway if bridge crashes or disconnects

### PWM Limits
- Firmware clamps all PWM values to [-255, +255]
- Invalid commands trigger immediate STOP

## Troubleshooting

**Motor doesn't move:**
- Check BTS7960 power supply (12V)
- Verify enable pins are HIGH when commanded
- Test motor directly with bench power supply

**Erratic behavior:**
- Check serial baud rate (115200)
- Verify command format (newline-terminated)
- Monitor serial output for error messages

**Watchdog triggering:**
- Increase `WATCHDOG_TIMEOUT_MS` if bridge update rate is slow
- Check USB cable quality
