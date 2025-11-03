# Wiring Diagram

## ESP32-S3 to BTS7960 Connections

```
ESP32-S3 DevKitC-1          BTS7960 Motor Driver
┌────────────────┐          ┌─────────────────┐
│                │          │                 │
│  GPIO 5 ───────┼──────────┤ RPWM            │
│  GPIO 6 ───────┼──────────┤ LPWM            │
│  GPIO 7 ───────┼──────────┤ R_EN            │
│  GPIO 8 ───────┼──────────┤ L_EN            │
│                │          │                 │
│  GND    ───────┼──────────┤ GND             │
│                │          │                 │
│  5V (USB) ─────┤          │ VCC (5V)        │
└────────────────┘          └─────────────────┘
                                    │
                                    │  12V Power
                            ┌───────┴───────┐
                            │  B+ ─── 12V   │
                            │  B- ─── GND   │
                            └───────────────┘
                                    │
                                    │  Motor Output
                            ┌───────┴───────┐
                            │  M+ ─── Red   │
                            │  M- ─── Black │
                            └───────────────┘
                                    │
                            JGB37-545 Motor
```

## Pin Assignments

### ESP32-S3 (Configurable in firmware)
| Pin | Function | Description |
|-----|----------|-------------|
| GPIO 5 | RPWM | Right PWM - Forward/Clockwise |
| GPIO 6 | LPWM | Left PWM - Reverse/Counter-clockwise |
| GPIO 7 | R_EN | Right Enable (Active HIGH) |
| GPIO 8 | L_EN | Left Enable (Active HIGH) |
| GND | Ground | Common ground |
| USB-C | Power & Serial | 5V power + programming/communication |

### BTS7960 H-Bridge
| Pin | Connection | Notes |
|-----|------------|-------|
| RPWM | ESP32 GPIO 5 | PWM input for forward direction |
| LPWM | ESP32 GPIO 6 | PWM input for reverse direction |
| R_EN | ESP32 GPIO 7 | Enable right side of bridge |
| L_EN | ESP32 GPIO 8 | Enable left side of bridge |
| VCC | 5V | Logic power (from ESP32 USB or buck converter) |
| GND | Common ground | Shared with ESP32 and motor power |
| B+ | 12V | Motor power supply (fused) |
| B- | GND | Motor power ground |
| M+ | Motor red wire | Motor positive |
| M- | Motor black wire | Motor negative |

## Power Supply

### ESP32-S3
- **Development**: USB-C (5V from laptop)
- **Production**: 5V buck converter from vehicle 12V

### BTS7960 + Motor
- **Source**: Vehicle 12V battery
- **Protection**: 10-15A fuse inline with B+
- **Wiring**: Use 14-16 AWG for motor power

## Recommended Fusing

| Component | Fuse Rating | Wire Gauge |
|-----------|-------------|------------|
| Motor power (12V) | 10-15A | 14-16 AWG |
| ESP32 5V supply | 2A | 22-24 AWG |

## Cable Lengths

- **ESP32 to BTS7960**: < 12 inches (minimize signal interference)
- **BTS7960 to Motor**: < 24 inches (minimize voltage drop)
- **12V power**: Shortest practical path from vehicle battery

## Grounding

**Critical**: All grounds must be connected together:
1. ESP32 GND
2. BTS7960 GND (logic)
3. BTS7960 B- (power)
4. Vehicle chassis ground

Use star grounding topology if possible to minimize ground loops.

## Safety Notes

1. **Fuse Protection**: Always use appropriate fuses on 12V supply
2. **Polarity**: Double-check motor polarity (reversal only changes direction)
3. **Heat**: BTS7960 may require heatsinking at high PWM duty cycles
4. **Isolation**: Keep power wiring away from signal wiring
5. **Emergency Stop**: Physical disconnect switch recommended for testing

## Testing Procedure

1. **Power Off**: Verify all connections with power disconnected
2. **Logic Test**: Power ESP32 only (via USB), verify firmware loads
3. **No-Load Test**: Power BTS7960, test motor with no mechanical load
4. **Low-Power Test**: Test with reduced `pwm_cap` (e.g., 100 instead of 255)
5. **Full System**: Gradually increase to full power range
