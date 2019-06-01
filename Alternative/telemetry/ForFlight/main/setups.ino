
void setup_bme280() {
  // # --------------- #

  // # Configures bme280

  // # --------------- #

  raw_bme_280.setI2CAddress(0x76);
  if (raw_bme_280.beginI2C() == false) Serial.println(F("BME280 connect failed"));

  for (int i = 0; i < 5; i++) {
    pressure = raw_bme_280.readFloatPressure();
    temp = (raw_bme_280.readTempF() - 32.0) * 5 / 9;
    height = (pow((101325 / pressure), (1 / 5.257)) - 1) * (temp + 273) / 0.0065 ;
  }
  bme_rm_mean = height;
}

void setup_servos() {
  servo1.attach(6);
  servo1.write(5);

  servo2.attach(9);
  servo2.write(175);
}
