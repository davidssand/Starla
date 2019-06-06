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

// CSV
unsigned int csv_index = 0;

// Running mean
float bme_rm_mean = 0.0;
int bme_rm_length = 30;

float velocity_rm_mean = 0.0;
int velocity_rm_length = 30;

// Time variables
unsigned long system_time = 0;
unsigned int apooge_time = 0;
unsigned int valid_value_detection_time = 0;
unsigned long current_time = 0;

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
  // Open serial communications and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    buzz(5, 100); 
  }

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
//  Serial.print(velocimeter.z_velocity);
//  Serial.print(" ");
//  Serial.println(velocimeter.filtered_z_velocity);
  
  populate_variables();
  
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
  change_checker(velocimeter.filtered_z_velocity);
}

void change_checker(float z_velocity) {
  valid_value = z_velocity < -0.5;
  if (!valid_value) {
    valid_value_detection_time = millis();
  }
  if (millis() - valid_value_detection_time > 500) {
    valid_value_detection_time = millis();
    open_parachute();
    after_fall();
  }
}

void after_fall(){
  delay(1000);
  detach_servos();
  delay(5000);
  buzz(1, 400);
  while(1);
}
