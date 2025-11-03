/**
 * ESP32-S3 Steering Motor Controller
 * 
 * Accepts ASCII serial commands and drives BTS7960 H-bridge bidirectionally
 * Command format: "S:<pwm>\n" where pwm in [-255, +255]
 *                 "STOP\n" for emergency halt
 * 
 * Hardware: ESP32-S3 DevKitC-1 -> BTS7960 -> JGB37-545 12V motor
 */

// Pin assignments
#define RPWM_PIN 5      // Right PWM (forward/clockwise)
#define LPWM_PIN 6      // Left PWM (reverse/counter-clockwise)
#define R_EN_PIN 7      // Right enable
#define L_EN_PIN 8      // Left enable

// PWM configuration
#define PWM_FREQ 20000  // 20 kHz
#define PWM_RESOLUTION 8 // 8-bit (0-255)
#define RPWM_CHANNEL 0
#define LPWM_CHANNEL 1

// Safety timeout
#define WATCHDOG_TIMEOUT_MS 500
unsigned long lastCommandTime = 0;

void setup() {
  Serial.begin(115200);
  
  // Configure PWM channels
  ledcSetup(RPWM_CHANNEL, PWM_FREQ, PWM_RESOLUTION);
  ledcSetup(LPWM_CHANNEL, PWM_FREQ, PWM_RESOLUTION);
  ledcAttachPin(RPWM_PIN, RPWM_CHANNEL);
  ledcAttachPin(LPWM_PIN, LPWM_CHANNEL);
  
  // Configure enable pins
  pinMode(R_EN_PIN, OUTPUT);
  pinMode(L_EN_PIN, OUTPUT);
  
  // Start in stopped state
  stopMotor();
  
  Serial.println("ESP32-S3 Steering Controller Ready");
  Serial.println("Commands: S:<pwm> | STOP");
}

void loop() {
  // Check for serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command.startsWith("S:")) {
      int pwm = command.substring(2).toInt();
      setMotor(pwm);
      lastCommandTime = millis();
    } else if (command == "STOP") {
      stopMotor();
      lastCommandTime = millis();
    } else {
      Serial.print("ERROR: Invalid command: ");
      Serial.println(command);
      stopMotor();
    }
  }
  
  // Watchdog: stop if no command received recently
  if (millis() - lastCommandTime > WATCHDOG_TIMEOUT_MS) {
    stopMotor();
    delay(10); // Prevent flooding
  }
}

void setMotor(int pwm) {
  // Clamp PWM value
  pwm = constrain(pwm, -255, 255);
  
  // Enable bridge
  digitalWrite(R_EN_PIN, HIGH);
  digitalWrite(L_EN_PIN, HIGH);
  
  if (pwm > 0) {
    // Clockwise (right turn)
    ledcWrite(RPWM_CHANNEL, pwm);
    ledcWrite(LPWM_CHANNEL, 0);
  } else if (pwm < 0) {
    // Counter-clockwise (left turn)
    ledcWrite(RPWM_CHANNEL, 0);
    ledcWrite(LPWM_CHANNEL, -pwm);
  } else {
    // Neutral
    ledcWrite(RPWM_CHANNEL, 0);
    ledcWrite(LPWM_CHANNEL, 0);
  }
}

void stopMotor() {
  // Disable all outputs
  ledcWrite(RPWM_CHANNEL, 0);
  ledcWrite(LPWM_CHANNEL, 0);
  digitalWrite(R_EN_PIN, LOW);
  digitalWrite(L_EN_PIN, LOW);
}
