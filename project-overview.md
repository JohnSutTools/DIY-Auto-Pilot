project_overview.md
Goal

Use openpilot as the single source of truth for lateral control. Bridge its steering command to an external steering actuator made from ESP32-S3 → BTS7960 → JGB37-545, mounted above the steering wheel with a roller.

Components (chosen)

Host: Laptop running openpilot

Bridge: Python process subscribing to openpilot control messages via cereal.messaging and sending serial commands (S:<pwm>)

Controller: ESP32-S3 DevKitC-1 (USB-C)

Driver: BTS7960 H-bridge

Motor: JGB37-545 12 V 316 RPM gearmotor

Mount: 3D-printed top-mount with spring-loaded roller contacting the steering wheel rim

Power: Vehicle 12 V (fused) for BTS7960; 5 V for ESP32 via buck or USB

Software flow
openpilot (perception/planning/control)
    └── publishes control messages (carControl / controlsState)
           └── op_serial_bridge.py (Python)
                 └── scale steer [-1..1] → PWM [-pwm_cap..+pwm_cap]
                       └── USB serial to ESP32-S3
                            └── LEDC PWM → BTS7960 → Motor

Implementation notes

The bridge prioritizes the carControl message’s actuator field (actuators.steer). If not available, it falls back to controlsState.

Scaling is adjustable in config.yaml (pwm_scale, pwm_cap, stream_hz).

The ESP32 firmware exposes a stable line-based API and drives the BTS7960 with 20 kHz PWM.

Bring-up plan

Verify ESP32 serial API with a terminal: send S:+120, S:-120, STOP.

Run openpilot in a mode that emits lateral commands (replay or your preferred run mode).

Start op_serial_bridge.py; monitor motor response.

Tune pwm_scale until steering authority matches expectations.

If you want, I can also add a simple openpilot replay command example and a Makefile to launch bridge + openpilot together in tmux so it’s one command to run.