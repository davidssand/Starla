/*
  SD card read/write

  This example shows how to read and write data to and from an SD card file
  The circuit:
   SD card attached to SPI bus as follows:
 ** MOSI - pin 11
 ** MISO - pin 12
 ** CLK - pin 13
 ** CS - pin 4 (for MKRZero SD: SDCARD_SS_PIN)

  by David

*/

#include <Wire.h>
#include <SPI.h>

// bme280
#include "SparkFunBME280.h"
float pressure, temp, hight;
BME280 raw_bme_280;

// SD
#include <SD.h>
File myFile;
const int columns_length = 3;
String columns[columns_length] = {"Time", "Hight", "Z Velocity"};
float data_to_store[columns_length];

// Servo
#include <Servo.h>
Servo servo1;
Servo servo2;

float z_velocity = 0;
float inst_z_vel = 0;

// make a string for assembling the data to log:
String dataString = "";

bool valid_value = false;

// CSV
const int data_pack_size = 20;
unsigned long int csv_index = 0;

// Running mean
float rm_sum = 0.0;
const int rm_lenght = 30;
float rm_result[rm_lenght] = {0, 0};
int rm_input_index = 0;

float bme_rm_sum = 0.0;
const int bme_rm_length = 30;
float bme_rm_result[rm_lenght] = {0, 0};
int bme_rm_input_index = 0;

// Time variables
unsigned long int system_time = 0;
float valid_value_detection_time = 0;

struct bme_sensor {
  float pressure;
  float temp;
  float hight;
  float last_hight;
  float filtered_hight;
};

struct timer {
  float current_time;
  float last_time;
};

bme_sensor bme_280 = {0, 0, 0, 0, 0};
timer timer = {0, 0};

void setup() {
  // Open serial communications and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  iniciate_csv_file();

  setup_bme280();

  system_time = millis();
}

void setup_bme280() {
  // # --------------- #

  // # Configures bme280

  // # --------------- #

  raw_bme_280.setI2CAddress(0x76);
  if (raw_bme_280.beginI2C() == false) Serial.println(F("BME280 connect failed"));

  for (int i = 0; i < 5; i++) {
    pressure = raw_bme_280.readFloatPressure();
    temp = (raw_bme_280.readTempF() - 32.0) * 5 / 9;
    hight = (pow((101325 / pressure), (1 / 5.257)) - 1) * (temp + 273) / 0.0065 ;
  }
}

void loop() {
  Serial.print(30);
  Serial.print(" ");
  Serial.println(bme_280.hight);
  populate_data_arrays();
  store_data(bme_280.hight);
//  
//  if (millis() - system_time > 20000){
//    read_csv();
//    while(1);
//  }
}

void populate_data_arrays() {
  // # --------------- #

  // # Puts read data in corresponding arrays

  // # --------------- #

  bme_280.pressure = raw_bme_280.readFloatPressure();
  bme_280.temp = (raw_bme_280.readTempF() - 32.0) * 5 / 9;
  bme_280.hight = (pow((101325 / bme_280.pressure), (1 / 5.257)) - 1) * (bme_280.temp + 273) / 0.0065 ;
}

void iniciate_csv_file() {
  Serial.print(F("Initializing SD card..."));

  if (!SD.begin(4)) {
    Serial.println(F("initialization failed!"));
    while (1);
  }
  
  // Remove before flight ----------------------------------------
  SD.remove("test.txt");
  // -------------------------------------------------------------
    
  Serial.println(F("initialization done."));

  delay(500);
  myFile = SD.open("test.txt", FILE_WRITE);
  delay(500);

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

float store_data(float data) {
  // --- SD --- //
  myFile = SD.open("test.txt", FILE_WRITE);
  if (myFile) {
    myFile.print(csv_index);
    for(int i = 0; i < columns_length; i++){      
      myFile.print(",");
      myFile.print(String(data));
//      myFile.write((const uint8_t *)&bme_280, sizeof(bme_280));
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
