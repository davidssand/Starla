

float bme_running_mean(float data) {
  //  # --------------- #
  //
  //  # Running mean for velocity
  //
  //  # --------------- #
  bme_rm_sum -= bme_rm_result[bme_rm_input_index];
  bme_rm_result[bme_rm_input_index] = data;
  bme_rm_sum += bme_rm_result[bme_rm_input_index];
  bme_rm_input_index = (bme_rm_input_index + 1) % bme_rm_length;

//  Serial.print("bme_result: ");
//  Serial.print(bme_rm_result[bme_rm_input_index]);
//  Serial.print(" bme_input_index: ");
//  Serial.print(bme_rm_input_index);
//  Serial.print(" bme_rm_sum: ");
//  Serial.println(bme_rm_sum);

  return bme_rm_sum / bme_rm_length;
}