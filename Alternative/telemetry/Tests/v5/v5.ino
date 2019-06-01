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
const int columns_length = 1;
String columns[columns_length] = {"Hight"};

// Servo
#include <Servo.h>
Servo servo1;
Servo servo2;

float z_velocity = 0;
float inst_z_vel = 0;
float vel_filtered = 0;

// make a string for assembling the data to log:
String dataString = "";

bool valid_value = false;

// CSV
const int data_pack_size = 20;
unsigned long int csv_index = 0;

// Data
int data_pack_index = 0;

float time_list[data_pack_size];

float accel_list[data_pack_size];
float pitch_list[data_pack_size];
float yaw_list[data_pack_size];
float roll_list[data_pack_size];

float altitude_list[data_pack_size];
float z_velocity_list[data_pack_size] = {0};

// sr -> sampling rate
float sr_list[data_pack_size] = {0};

// Running mean
float rm_sum = 0;
const int rm_lenght = 30;
float rm_result[rm_lenght];
int rm_input_index = 0;

float bme_rm_sum;
const int bme_rm_length = 30;
float bme_rm_result[rm_lenght];
int bme_rm_input_index = 0;

// Time variables
unsigned long int system_time = 0;
float valid_value_detection_time = 0;

struct bme_sensor {
  float pressure;
  float temp;
  float hight;
};

bme_sensor bme_280 = {0, 0, 0};

// ------------- //
// --- Setup --- //
// ------------- //

void setup() {
  Serial.begin(9600);

  setup_servos();

  setup_bme280();

  for (int i = 0; i < rm_lenght; i++) {
    rm_result[i] = 0;
  }

  while (!Serial) {
    ;
  }

//  iniciate_csv_file();

  for (int i = 0; i < rm_lenght; i++) {
    bme_rm_result[i] = hight;
  }
  bme_rm_sum = hight * bme_rm_length;

  system_time = millis();
}

void setup_servos() {
  servo1.attach(9);
  servo1.write(5);

  servo2.attach(6);
  servo2.write(175);
}

void setup_bme280() {
  // # --------------- #

  // # Configures bme280

  // # --------------- #

  raw_bme_280.setI2CAddress(0x76);
  if (raw_bme_280.beginI2C() == false) Serial.println("BME280 connect failed");

  for (int i = 0; i < 5; i++) {
    pressure = raw_bme_280.readFloatPressure();
    temp = (raw_bme_280.readTempF() - 32.0) * 5 / 9;
    hight = (pow((101325 / pressure), (1 / 5.257)) - 1) * (temp + 273) / 0.0065 ;
  }
}

// ------------ //
// --- Loop --- //
// ------------ //

void loop() {
  populate_data_arrays();

  Serial.print(altitude_list[data_pack_index]);
  Serial.print(" ");
  Serial.println(z_velocity_list[data_pack_index]);

  if (data_pack_index > 0) {
    check_change();
  }

  data_pack_index++;
  if (data_pack_index == data_pack_size) {
    store_data(1.2);
    data_pack_index = 0;
    z_velocity_list[data_pack_index] = z_velocity_list[data_pack_size];
    sr_list[data_pack_index] = sr_list[data_pack_size];
  }

//  if (millis() - system_time > 10000){
//    read_csv();
//    while (1);
//  }
}

void populate_data_arrays() {
  // # --------------- #

  // # Puts read data in corresponding arrays

  // # --------------- #

  bme_280.pressure = raw_bme_280.readFloatPressure();
  bme_280.temp = (raw_bme_280.readTempF() - 32.0) * 5 / 9;
  bme_280.hight = (pow((101325 / bme_280.pressure), (1 / 5.257)) - 1) * (bme_280.temp + 273) / 0.0065 ;

  time_list[data_pack_index] = millis() - system_time;
//    accel_list[data_pack_index] = (mpu.get_total_accel(self.mpu.accelerometer.scaled));
//    pitch_list[data_pack_index] = (mpu.angle[0]);
//    yaw_list[data_pack_index] = (mpu.angle[1]);
//    roll_list[data_pack_index] = (mpu.angle[2]);
  altitude_list[data_pack_index] = bme_running_mean(bme_280.hight);
}

void check_change() {
  // # --------------- #

  // # Decides

  // # --------------- #

  inst_z_vel = (altitude_list[data_pack_index] - altitude_list[data_pack_index - 1]) /
               (0.001 * (time_list[data_pack_index] - time_list[data_pack_index - 1]));
  vel_filtered = running_mean(inst_z_vel);
  change_checker(vel_filtered);

  z_velocity_list[data_pack_index] = vel_filtered;
  sr_list[data_pack_index] = time_list[data_pack_index] - time_list[data_pack_index - 1];
}

void change_checker(float z_velocity) {
  valid_value = z_velocity < -0.3;
  if (!valid_value) {
    //    Serial.println("Valor valido");
    valid_value_detection_time = millis();
  }
  if (millis() - valid_value_detection_time > 500) {
    Serial.print("# ---- OPEN ---- #");
    valid_value_detection_time = millis();
    open_parachute();
  }
}

void open_parachute() {
  servo1.write(175);
  servo2.write(5);
}

void iniciate_csv_file() {
  Serial.print("Initializing SD card...");

  if (!SD.begin(4)) {
    
    Serial.println("initialization failed!");
    while (1);
  }
  
  // Remove before flight ----------------------------------------
  SD.remove("test.txt");
  // -------------------------------------------------------------
    
  Serial.println("initialization done.");

  myFile = SD.open("test.txt", FILE_WRITE);

  if (myFile) {
    for (int i = 0; i < columns_length; i++) {
      myFile.print("," + columns[i]);
    }
    myFile.println();
    myFile.close();
  } else {
    // if the file didn't open, print an error:
    Serial.println("error opening test.txt");
  }
}

float store_data(float data) {
  // --- SD --- //
  myFile = SD.open("test.txt", FILE_WRITE);
  if (myFile) {
    myFile.print(csv_index);
    for(int i = 0; i < columns_length; i++){
      myFile.print("," + String(data));
    }
    myFile.println("");
    myFile.close();
    csv_index++;
  } else {
    Serial.println("error opening test.txt");
  }
  // ---  --- //
}

void read_csv() {
  // re-open the file for reading:
  myFile = SD.open("test.txt");
  if (myFile) {
    Serial.println("test.txt:");
    while (myFile.available()) {
      Serial.write(myFile.read());
    }
    // close the file:
    myFile.close();
  } else {
    // if the file didn't open, print an error:
    Serial.println("error opening test.txt");
  }
}

float running_mean(float data) {
  //  # --------------- #
  //
  //  # Running mean for velocity
  //
  //  # --------------- #
  rm_sum -= rm_result[rm_input_index];
  rm_result[rm_input_index] = data;
  rm_sum += rm_result[rm_input_index];
  rm_input_index = (rm_input_index + 1) % rm_lenght;

  //  Serial.print("result", rm_result);
  //  Serial.print("input_index", rm_input_index);
  //  Serial.print("sum", rm_sum);

  return rm_sum / rm_lenght;
}

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

  //  Serial.print("result", bme_rm_result);
  //  Serial.print("input_index", bme_rm_input_index);
  //  Serial.print("sum", bme_rm_sum);

  return bme_rm_sum / bme_rm_length;
}
