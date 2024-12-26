#define ENA 9
#define IN1 7
#define IN2 6
#define IN3 5
#define IN4 4
#define ENB 10
#define LED 13  // Pin for LED

// Variables
bool firstStop = true; // To track if it's the first or second STOP

void setup() {
  // Initialize motor pins as outputs
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  // Initialize LED pin
  pinMode(LED, OUTPUT);

  // Initialize serial communication
  Serial.begin(9600);

  // Start with motors off and LED off
  stopMotors();
  digitalWrite(LED, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');

    if (command == "STOP") {
      if (firstStop) {
        slowDownMotors(); // Slow down motors on first STOP
        firstStop = false;
      } else {
        stopMotors(); // Stop motors immediately on second STOP
        blinkLED(); // Start blinking LED
      }
    } else if (command == "START") {
      runMotors(); // Start motors
      firstStop = true; // Reset to allow slowing down on next STOP
      digitalWrite(LED, LOW); // Turn off LED
    }
  }
}

void runMotors() {
  // Set full speed and direction for both motors
  analogWrite(ENA, 255);  // Full speed for Motor A
  analogWrite(ENB, 255);  // Full speed for Motor B

  // Set Motor A direction
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  // Set Motor B direction
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void slowDownMotors() {
  // Set half speed for both motors
  analogWrite(ENA, 128);  // Half speed for Motor A
  analogWrite(ENB, 128);  // Half speed for Motor B
}

void stopMotors() {
  // Stop both motors immediately
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);

  analogWrite(ENA, 0);  // Disable Motor A
  analogWrite(ENB, 0);  // Disable Motor B
}

void blinkLED() {
  // Blink the LED until a START command is received
  while (true) {
    digitalWrite(LED, HIGH);
    delay(500);
    digitalWrite(LED, LOW);
    delay(500);

    // Check if a START command is received
    if (Serial.available() > 0) {
      String command = Serial.readStringUntil('\n');
      if (command == "START") {
        return; // Exit the blinking loop
      }
    }
  }
}
