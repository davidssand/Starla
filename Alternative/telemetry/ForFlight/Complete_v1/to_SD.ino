
void iniciate_csv_file() {
  while (!SD.begin(4)) {
    buzz(2, 300);
  }

  buzz(1, 100);
  
  // Remove before flight ----------------------------------------
  SD.remove("test.txt");
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
      buzz(1, 100);
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
