#include <OneWire.h>
#include <DallasTemperature.h>

// DS18B20 setup
#define ONE_WIRE_BUS D2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// Pulse sensor setup
#define PULSE_PIN A0
int pulseValue = 0;
unsigned long lastBeat = 0;
int BPM = 0;
int beatCount = 0;
unsigned long startTime;

void setup() {
  Serial.begin(115200);
  sensors.begin();
  pinMode(PULSE_PIN, INPUT);
  startTime = millis();
}

void loop() {
  // ========== TEMPERATURE ==========
  sensors.requestTemperatures();
  float temperatureC = sensors.getTempCByIndex(0);
  float temperatureF = sensors.toFahrenheit(temperatureC);

  // ========== PULSE SENSOR ==========
  pulseValue = analogRead(PULSE_PIN);
  unsigned long currentTime = millis();

  static bool beatDetected = false;

  if (pulseValue > 550 && !beatDetected) {
    beatDetected = true;
    beatCount++;
  }

  if (pulseValue < 500) {
    beatDetected = false;
  }

  if (currentTime - startTime >= 10000) { // every 10s
    BPM = beatCount * 6;
    beatCount = 0;
    startTime = currentTime;

    // ========== SIMULATED BLOOD PRESSURE ==========
    int systolicBP = 120 + random(-5, 5);
    int diastolicBP = 80 + random(-5, 5);

    // ========== STATUS CHECKS ==========
    String heartStatus = (BPM >= 60 && BPM <= 100) ? "NORMAL" : "NOT NORMAL";
    String tempStatus = (temperatureC >= 36.1 && temperatureC <= 37.5) ? "NORMAL" : "NOT NORMAL";
    String bpStatus = (systolicBP >= 90 && systolicBP <= 120 && diastolicBP >= 60 && diastolicBP <= 80) ? "NORMAL" : "NOT NORMAL";

    // ========== PRINT RESULTS ==========
    Serial.println("===== HEALTH MONITORING =====");

    Serial.print("Heart Rate (BPM): ");
    Serial.print(BPM);
    Serial.print(" --> ");
    Serial.println(heartStatus);

    Serial.print("Body Temp (°C): ");
    Serial.print(temperatureC);
    Serial.print(" --> ");
    Serial.println(tempStatus);

    Serial.print("Blood Pressure: ");
    Serial.print(systolicBP);
    Serial.print("/");
    Serial.print(diastolicBP);
    Serial.print(" mmHg --> ");
    Serial.println(bpStatus);

    Serial.println("=============================");
  }

  delay(100); // short delay for loop
}
