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
BME280 raw_bme_280;

// mpu9250
#include <SparkFunMPU9250-DMP.h>
MPU9250_DMP mpu;

// SD
#include <SD.h>
File myFile;

const byte data_to_store_length = 11;
float data_to_store[data_to_store_length];

// Servo
#include <Servo.h>
Servo servo1;
Servo servo2;

bool valid_value = false;
bool apogee = false;

// CSV
unsigned long int csv_index = 0;

// Running mean
float bme_rm_mean = 0.0;
const int bme_rm_length = 30;

float velocity_rm_mean = 0.0;
const int velocity_rm_length = 30;

// Time variables
unsigned long int system_time = 0;
unsigned long int apooge_time = 0;
unsigned long int valid_value_detection_time = 0;
unsigned long int current_time = 0;

struct bme_sensor {
  float pressure;
  float temp;
  float height;
  float last_height;
  float filtered_height;
};

struct mpu_sensor {
  float accelX;
  float accelY;
  float accelZ;
  float gyroX;
  float gyroY;
  float gyroZ;
};

struct velocimeter {
  float z_velocity;
  float filtered_z_velocity;
};

mpu_sensor mpu_9250 = {0, 0, 0, 0, 0, 0};
bme_sensor bme_280 = {0, 0, 0, 0, 0};
velocimeter velocimeter = {0, 0};

void setup() {
  pinMode(A2, OUTPUT);

  iniciate_csv_file();

  setup_servos();

  setup_mpu9250();
  setup_bme280();

  system_time = millis();

  open_parachute();
  while(millis() - system_time < 10000) populate_variables();
  arm_parachute();
  delay(100);
}

void loop() {  
  populate_variables();
  storer();
  if(!apogee) change_checker(velocimeter.filtered_z_velocity);
  else{
    if((millis() - apooge_time) > 2000) detach_servos();
    if((millis() - apooge_time) > 15000){
      while(1){
        rescue();
      }
    }
  }
}

void change_checker(float z_velocity) {
  valid_value = z_velocity < -0.5;
  if (!valid_value) {
    valid_value_detection_time = millis();
  }
  if (millis() - valid_value_detection_time > 500) {
    valid_value_detection_time = millis();
    open_parachute();
    apooge_time = millis();
    apogee = true;
  }
}

void rescue(){
  buzz(3, 100);
  delay(1000);
}
