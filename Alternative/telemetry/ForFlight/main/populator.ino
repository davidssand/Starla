void populate_variables() {
  // # --------------- #

  // # Puts read data in corresponding variables

  // # --------------- #

  bme_280.pressure = raw_bme_280.readFloatPressure();
  bme_280.temp = (raw_bme_280.readTempF() - 32.0) * 5 / 9;
  bme_280.height = (pow((101325 / bme_280.pressure), (1 / 5.257)) - 1) * (bme_280.temp + 273) / 0.0065 ;
  
  timer.current_time = millis() - system_time;

  bme_280.filtered_height = bme_rm(bme_280.height);
  velocimeter.filtered_z_velocity = velocity_rm(velocimeter.z_velocity);

  velocimeter.z_velocity = (bme_280.filtered_height - bme_280.last_height) /
               (0.001 * (timer.current_time - timer.last_time));

  bme_280.last_height = bme_280.filtered_height;
  timer.last_time = timer.current_time;
}
