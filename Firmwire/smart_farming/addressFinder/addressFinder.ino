#include <Wire.h>

void setup() {
  Serial.begin(115200);

  Wire.begin(21, 22);

  Serial.println("I2C Scanner");

  for (byte address = 1; address < 127; address++) {
    Wire.beginTransmission(address);

    if (Wire.endTransmission() == 0) {
      Serial.print("Found I2C device at 0x");
      if (address < 16) {
        Serial.print("0");
      }
      Serial.println(address, HEX);
    }
  }

  Serial.println("Scan complete");
}

void loop() {
}