void populate_variables() {
  // # --------------- #

  // # Puts read data in corresponding variables

  // # --------------- #

  if (mpu.dataReady()) mpu.update(UPDATE_ACCEL | UPDATE_GYRO | UPDATE_COMPASS);

  mpu_9250.accelX = mpu.calcAccel(mpu.ax);
  mpu_9250.accelY = mpu.calcAccel(mpu.ay);
  mpu_9250.accelZ = mpu.calcAccel(mpu.az);
  mpu_9250.gyroX = mpu.calcGyro(mpu.gx);
  mpu_9250.gyroY = mpu.calcGyro(mpu.gy);
  mpu_9250.gyroZ = mpu.calcGyro(mpu.gz);

  bme_280.pressure = raw_bme_280.readFloatPressure();
  bme_280.temp = (raw_bme_280.readTempF() - 32.0) * 5 / 9;
  bme_280.height = (pow((101325 / bme_280.pressure), (1 / 5.257)) - 1) * (bme_280.temp + 273) / 0.0065 ;  

  bme_280.filtered_height = bme_rm(bme_280.height);
  velocimeter.filtered_z_velocity = velocity_rm(velocimeter.z_velocity);
  
  velocimeter.z_velocity = (bme_280.filtered_height - bme_280.last_height) /
               (0.001 * ((millis() - system_time) - current_time));

  bme_280.last_height = bme_280.filtered_height;

  current_time = millis() - system_time;
}
