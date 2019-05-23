/*
  SD card datalogger

 This example shows how to log data from three analog sensors
 to an SD card using the SD library.

 The circuit:
 * analog sensors on analog ins 0, 1, and 2
 * SD card attached to SPI bus as follows:
 ** MOSI - pin 11
 ** MISO - pin 12
 ** CLK - pin 13
 ** CS - pin 4 (for MKRZero SD: SDCARD_SS_PIN)

 created  24 Nov 2010
 modified 9 Apr 2012
 by Tom Igoe

 This example code is in the public domain.

 */

#include <SPI.h>
#include <SD.h>

const int chipSelect = 4;
float t0 = 0;

float z_velocity = 0;

// make a string for assembling the data to log:
String dataString = "";

bool valid_value = false;

// Data
int interval_storage_size = 3;
const int data_pack_size = 100;
const int data_pack_index = 0;

float time_list[data_pack_size];

float accel_list[data_pack_size];
float pitch_list[data_pack_size];
float yaw_list[data_pack_size];
float roll_list[data_pack_size];

float altitude_list[data_pack_size];
float last_z_vel_value = 0;
float z_velocity_list[data_pack_size] = {last_z_vel_value};

// sr -> sampling rate
float last_sr_value = 0;
float sr_list[data_pack_size] = {last_sr_value};

// Running mean
float rm_sum = 0;
const int rm_lenght = 60;
float rm_result[rm_lenght];
int rm_input_index = 0;

void setup() {
  for (int i = 0; i < rm_lenght; i++){
    rm_result[i] = 0;
  }
  
  Serial.begin(9600);
  while (!Serial) {
    ; 
  }

  Serial.print("Initializing SD card...");

  // see if the card is present and can be initialized:
  if (!SD.begin(chipSelect)) {
    Serial.println("Card failed, or not present");
    // don't do anything more:
    return;
  }
  Serial.println("card initialized.");
}

void loop() {
  populate_data_arrays()

  z_velocity = (altitude_list[data_pack_index] - altitude_list[data_pack_index-1])/
    (time_list[data_pack_index] - time_list[data_pack_index-1])

  if(z_velocity < 0.2 and valid_value == false){
    t0 = millis();
    valid_value = true;
  }
  if(millis() - t0 > 1000 && valid_value == true){
    valid_value = false;
    open_parachute();
  }

  // read three sensors and append to the string:
  for (int analogPin = 0; analogPin < 3; analogPin++) {
    int sensor = analogRead(analogPin);
    dataString += String(sensor);
    if (analogPin < 2) {
      dataString += ",";
    }
  }

  // open the file. note that only one file can be open at a time,
  // so you have to close this one before opening another.
  File dataFile = SD.open("datalog.txt", FILE_WRITE);

  // if the file is available, write to it:
  if (dataFile) {
    dataFile.println(dataString);
    dataFile.close();
    // print to the serial port too:
    Serial.println(dataString);
  }
  // if the file isn't open, pop up an error:
  else {
    Serial.println("error opening datalog.txt");
  }
}

float running_mean(float data){
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

  return rm_sum/rm_lenght;
}

void open_parachute(){
  ;
}

void populate_data_arrays(){
  // # --------------- #

  // # Puts read data in corresponding arrays
  
  // # --------------- #

  mpu.get_data(0.03)
  bme.get_data()

  time_list[data_pack_index] = (millis() - system_time)
  accel_list.[data_pack_index] = (mpu.get_total_accel(self.mpu.accelerometer.scaled))
  pitch_list[data_pack_index] = (mpu.angle[0])
  yaw_list[data_pack_index] = (mpu.angle[1])
  roll_list[data_pack_index] = (mpu.angle[2])
  altitude_list[data_pack_index] = (bme.running_mean(self.bme.hight))
  
  data_pack_index++
}

void pack_decision_data(){
    // # --------------- #

    // # Gathers all data in a package for decision_thread

    // # --------------- #

    // vel = (self.altitude_list[-1] - self.altitude_list[-2])/(self.time_list[-1] - self.time_list[-2])
    // vel_filtered = self.running_mean(vel)
    // self.z_velocity_list.append(vel_filtered)
    // self.data_to_check.put(vel_filtered)
    // self.sr_list.append(self.time_list[-1]-self.time_list[-2])
}











