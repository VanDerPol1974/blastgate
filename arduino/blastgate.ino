#include <Servo.h>
#include <avr/wdt.h>

// ============================
// KONFIGURATION
// ============================
#define NUM_GATES 6
#define MOTOR1_PIN 8
#define MOTOR2_PIN 9

#define MOTOR_DELAY_MS 1500   // Verzögerung zwischen Motor 1 & 2
#define HEARTBEAT_MS 1000

// ============================
// PINBELEGUNG
// ============================
const uint8_t servoPins[NUM_GATES]  = {22, 23, 24, 25, 26, 27};
const uint8_t buttonPins[NUM_GATES] = {53, 51, 49, 47, 45, 43};

// ============================
// SERVO-WINKEL
// ============================
int servoOpen[NUM_GATES]  = {10, 10, 10, 10, 10, 10};
int servoClose[NUM_GATES] = {90, 90, 90, 90, 90, 90};

// ============================
// STATUS
// ============================
enum SystemState { RUN, SERVICE, ERROR };
SystemState systemState = RUN;

bool gateOpen[NUM_GATES] = {false};
bool motorRunning = false;
bool motor2Started = false;

unsigned long motorTimer = 0;
unsigned long heartbeatTimer = 0;

// ============================
// OBJEKTE
// ============================
Servo servos[NUM_GATES];

// ============================
// SETUP
// ============================
void setup() {
  Serial.begin(115200);

  // Watchdog: 2 Sekunden
  wdt_enable(WDTO_2S);

  for (int i = 0; i < NUM_GATES; i++) {
    pinMode(buttonPins[i], INPUT_PULLUP);
    servos[i].attach(servoPins[i]);
    servos[i].write(servoClose[i]);
  }

  pinMode(MOTOR1_PIN, OUTPUT);
  pinMode(MOTOR2_PIN, OUTPUT);
  digitalWrite(MOTOR1_PIN, LOW);
  digitalWrite(MOTOR2_PIN, LOW);

  Serial.println("STATE:RUN");
}

// ============================
// LOOP
// ============================
void loop() {
  wdt_reset();

  handleButtons();
  handleMotors();
  sendHeartbeat();
}

// ============================
// TASTER
// ============================
void handleButtons() {
  for (int i = 0; i < NUM_GATES; i++) {
    if (digitalRead(buttonPins[i]) == LOW) {
      toggleGate(i);
      delay(300); // Entprellen
    }
  }
}

// ============================
// GATE LOGIK
// ============================
void toggleGate(int idx) {
  if (systemState == ERROR) return;

  gateOpen[idx] = !gateOpen[idx];

  if (gateOpen[idx]) {
    servos[idx].write(servoOpen[idx]);
    startMotors();
  } else {
    servos[idx].write(servoClose[idx]);
    checkAllClosed();
  }

  Serial.print("GATE:");
  Serial.print(idx);
  Serial.print(":");
  Serial.println(gateOpen[idx] ? "OPEN" : "CLOSE");
}

// ============================
// MOTOREN
// ============================
void startMotors() {
  if (motorRunning) return;

  motorRunning = true;
  motor2Started = false;
  motorTimer = millis();

  digitalWrite(MOTOR1_PIN, HIGH);
  Serial.println("MOTOR1:ON");
}

void handleMotors() {
  if (!motorRunning) return;

  if (!motor2Started && millis() - motorTimer > MOTOR_DELAY_MS) {
    digitalWrite(MOTOR2_PIN, HIGH);
    motor2Started = true;
    Serial.println("MOTOR2:ON");
  }
}

void stopMotors() {
  digitalWrite(MOTOR1_PIN, LOW);
  digitalWrite(MOTOR2_PIN, LOW);
  motorRunning = false;
  motor2Started = false;

  Serial.println("MOTORS:OFF");
}

void checkAllClosed() {
  for (int i = 0; i < NUM_GATES; i++) {
    if (gateOpen[i]) return;
  }
  stopMotors();
}

// ============================
// HEARTBEAT
// ============================
void sendHeartbeat() {
  if (millis() - heartbeatTimer > HEARTBEAT_MS) {
    heartbeatTimer = millis();

    Serial.print("HB:");
    Serial.print(systemState == RUN ? "RUN" :
                 systemState == SERVICE ? "SERVICE" : "ERROR");
    Serial.print(":M1=");
    Serial.print(digitalRead(MOTOR1_PIN));
    Serial.print(":M2=");
    Serial.println(digitalRead(MOTOR2_PIN));
  }
}
