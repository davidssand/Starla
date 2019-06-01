
void iniciate_csv_file() {
  
  Serial.print(F("Initializing SD card..."));

  while (!SD.begin(4)) {
    Serial.println(F("initialization failed!"));
  }
  
  // Remove before flight ----------------------------------------
  SD.remove("test.txt");
  // -------------------------------------------------------------
    
  Serial.println(F("initialization done."));

  myFile = SD.open("test.txt", FILE_WRITE);

  if (myFile) {
    for (int i = 0; i < columns_length; i++) {
      myFile.print("," + columns[i]);
    }
    myFile.println();
    myFile.close();
  } else {
    // if the file didn't open, print an error:
    Serial.println(F("error opening test.txt"));
  }
}

float store_data(float data[]) {
  // --- SD --- //
  myFile = SD.open("test.txt", FILE_WRITE);
  if (myFile) {
    myFile.print(csv_index);
    for(int i = 0; i < columns_length; i++){      
      myFile.print(",");
      myFile.print(data[i]);
    }
    myFile.println("");
    myFile.close();
    csv_index++;
  } else {
    Serial.println(F("error opening test.txt"));
  }
  // ---  --- //
}

void read_csv() {
  // re-open the file for reading:
  myFile = SD.open("test.txt");
  if (myFile) {
    Serial.println(F("test.txt:"));
    while (myFile.available()) {
      Serial.write(myFile.read());
    }
    // close the file:
    myFile.close();
  } else {
    // if the file didn't open, print an error:
    Serial.println(F("error opening test.txt"));
  }
}