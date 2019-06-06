
void setup_bme280() {
  // # --------------- #

  // # Configures bme280

  // # --------------- #

  raw_bme_280.setI2CAddress(0x76);
  if (raw_bme_280.beginI2C() == false) buzz(4, 100);

  for (int i = 0; i < 5; i++) {
    bme_280.pressure = raw_bme_280.readFloatPressure();
    bme_280.temp = (raw_bme_280.readTempF() - 32.0) * 5 / 9;
    bme_280.height = (pow((101325 / bme_280.pressure), (1 / 5.257)) - 1) * (bme_280.temp + 273) / 0.0065 ;  
  }
  bme_rm_mean = bme_280.height;
}

void setup_mpu9250(){
  while (mpu.begin() != INV_SUCCESS);
  mpu.setSensors(INV_XYZ_GYRO | INV_XYZ_ACCEL);
  mpu.setGyroFSR(2000); // Set gyro to 2000 dps
  mpu.setAccelFSR(2); // Set accel to +/-2g
  mpu.setLPF(42); // Set LPF corner frequency to 5Hz
  mpu.setSampleRate(10); // Set sample rate to 10Hz
}

void setup_servos() {
  servo1.attach(6);
  servo2.attach(9);
}

void detach_servos() {
  servo1.detach();
  servo2.detach();
}
