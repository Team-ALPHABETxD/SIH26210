#define MQ135_PIN 32

void setup() {
  Serial.begin(115200);

  analogReadResolution(12);  // 0–4095

  Serial.println("MQ-135 Calibration");
  Serial.println("Keep sensor in clean normal air.");
  Serial.println("Warm-up started...");
}

void loop() {

  int adcValue = analogRead(MQ135_PIN);

  // Voltage at GPIO 32 after your voltage divider
  float voltage = (adcValue / 4095.0) * 3.3;

  Serial.print("ADC = ");
  Serial.print(adcValue);

  Serial.print("   Voltage = ");
  Serial.print(voltage, 3);
  Serial.println(" V");

  delay(2000);
}