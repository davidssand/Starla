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
float pressure, temp, height;
BME280 raw_bme_280;

// SD
#include <SD.h>
File myFile;
const int columns_length = 3;
String columns[columns_length] = {"time", "height", "z_velocity"};
float data_to_store[columns_length];

// Servo
#include <Servo.h>
Servo servo1;
Servo servo2;

// make a string for assembling the data to log:
String dataString = "";

bool valid_value = false;

// CSV
unsigned long int csv_index = 0;

// Running mean
float bme_rm_mean = 0.0;
int bme_rm_length = 30;

float velocity_rm_mean = 0.0;
int velocity_rm_length = 30;

// Time variables
unsigned long int system_time = 0;
float valid_value_detection_time = 0;

struct bme_sensor {
  float pressure;
  float temp;
  float height;
  float last_height;
  float filtered_height;
};

struct velocimeter {
  float z_velocity;
  float filtered_z_velocity;
};

struct timer {
  float current_time;
  float last_time;
};

bme_sensor bme_280 = {0, 0, 0, 0, 0};
velocimeter velocimeter = {0, 0};
timer timer = {0, 0};

void setup() {
  // Open serial communications and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    buzz(5, 100); 
  }

  setup_servos();

  iniciate_csv_file();

  setup_bme280();

  system_time = millis();
  timer.current_time = millis() - system_time;
}

void loop() {
  Serial.print(velocimeter.z_velocity);
  Serial.print(" ");
  Serial.println(velocimeter.filtered_z_velocity);
  
  populate_variables();
  
  data_to_store[0] = timer.current_time;
  data_to_store[1] = bme_280.filtered_height;
  data_to_store[2] = velocimeter.filtered_z_velocity;
  store_data(data_to_store);
  change_checker(velocimeter.filtered_z_velocity);
}

void change_checker(float z_velocity) {
  valid_value = z_velocity < -0.5;
  if (!valid_value) {
    //    Serial.println("Valor valido");
    valid_value_detection_time = millis();
  }
  if (millis() - valid_value_detection_time > 400) {
    valid_value_detection_time = millis();
    open_parachute();
  }
}
