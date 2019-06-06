void storer(){
  data_to_store[0] = current_time;
  data_to_store[1] = bme_280.pressure;
  data_to_store[2] = bme_280.temp;
  data_to_store[3] = bme_280.height;
  data_to_store[4] = velocimeter.z_velocity;
  data_to_store[5] = mpu_9250.accelX;
  data_to_store[6] = mpu_9250.accelY;
  data_to_store[7] = mpu_9250.accelZ;
  data_to_store[8] = mpu_9250.gyroX;
  data_to_store[9] = mpu_9250.gyroY;
  data_to_store[10] = mpu_9250.gyroZ;

  store_data(data_to_store);
}

void iniciate_csv_file() {
  while (!SD.begin(4)) {
    buzz(5, 300);
  }

  buzz(3, 200);
  
  // Remove before flight ----------------------------------------
//  SD.remove("test.txt");
  // -------------------------------------------------------------
}

float store_data(float data[data_to_store_length]) {
  // --- SD --- //
  myFile = SD.open("test.txt", FILE_WRITE);
  if (myFile) {
    myFile.print(csv_index);
    for(int i = 0; i < data_to_store_length; i++){      
      myFile.print(",");
      myFile.print(data[i]);
    }
    myFile.println("");
    myFile.close();
    csv_index++;
  } else {
      buzz(2, 100);
  }
  // ---  --- //
}

//void read_csv() {
//  // re-open the file for reading:
//  myFile = SD.open("test.txt");
//  if (myFile) {
//    Serial.println(F("test.txt:"));
//    while (myFile.available()) {
//      Serial.write(myFile.read());
//    }
//    // close the file:
//    myFile.close();
//  } else {
//    // if the file didn't open, print an error:
//    Serial.println(F("error opening test.txt"));
//  }
//}
