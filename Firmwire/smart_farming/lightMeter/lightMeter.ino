#include <Wire.h>
#include <BH1750.h>

BH1750 lightMeter;

void setup() {
  Serial.begin(115200);

  // ESP32 I2C pins
  Wire.begin(21, 22);

  // Start BH1750
  if (lightMeter.begin()) {
    Serial.println("BH1750 started successfully");
  } else {
    Serial.println("Error: BH1750 not found!");
    while (1);
  }
}

void loop() {

  float lux = lightMeter.readLightLevel();

  Serial.print("Light: ");
  Serial.print(lux);
  Serial.println(" lux");

  delay(1000);
}