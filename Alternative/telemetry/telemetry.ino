/*
  SD card datalogger

 This example shows how to log data from three analog sensors
 to an SD card using the SD library.

 The circuit:
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

#include <Servo.h>

Servo parachute_servos;

int parachute_servos_pos = 0;

// SD
File myFile;
const int columns_length = 2;
String columns[columns_length] = {"Coluna1", "Coluna2"};

float t0 = 0;

float z_velocity = 0;
float inst_z_vel = 0;
float vel_filtered = 0;

// make a string for assembling the data to log:
String dataString = "";

bool valid_value = false;

// Data
int interval_storage_size = 3;
const int data_pack_size = 40;
int data_pack_index = 0;

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

// Time variables 
unsigned int system_time = 0;

//void setup(){}
//void loop(){}

// --- Setup --- //

void setup() {
  Serial.begin(9600); 
  parachute_servos.attach(9);

  for (int i = 0; i < rm_lenght; i++){
    rm_result[i] = 0;
  }
  
  // Open serial communications and wait for port to open:
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }


  Serial.print("Initializing SD card...");

  if (!SD.begin(4)) {
    Serial.println("initialization failed!");
    while (1);
  }
  Serial.println("initialization done.");

  // open the file. note that only one file can be open at a time,
  // so you have to close this one before opening another.
  myFile = SD.open("flight_data.txt", FILE_WRITE);

  // if the file opened okay, write to it:
  if (myFile) {
    Serial.print("Writing to test.txt...");
    myFile.println("testing 1, 2, 3.");
    // close the file:
    myFile.close();
    Serial.println("done.");
  } else {
    // if the file didn't open, print an error:
    Serial.println("aaaaaaaaaaa");
    Serial.println("error opening test.txt");
  }

  system_time = millis();
}

// --- Loop --- //

void loop() {
  // populate_data_arrays();

  // check_change();
  
  store_data();
  delay(1000);

  data_pack_index++;
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
  for (parachute_servos_pos = 0; parachute_servos_pos <= 180; parachute_servos_pos += 1) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    parachute_servos.write(parachute_servos_pos);              // tell servo to go to position in variable 'pos'
    delay(15);                       // waits 15ms for the servo to reach the position
  }
  for (parachute_servos_pos = 180; parachute_servos_pos >= 0; parachute_servos_pos -= 1) { // goes from 180 degrees to 0 degrees
    parachute_servos.write(parachute_servos_pos);              // tell servo to go to position in variable 'pos'
    delay(15);                       // waits 15ms for the servo to reach the position
  }
}

void populate_data_arrays(){
  // # --------------- #

  // # Puts read data in corresponding arrays
  
  // # --------------- #

//  time_list[data_pack_index] = millis() - system_time;
//  accel_list[data_pack_index] = (mpu.get_total_accel(self.mpu.accelerometer.scaled));
//  pitch_list[data_pack_index] = (mpu.angle[0]);
//  yaw_list[data_pack_index] = (mpu.angle[1]);
//  roll_list[data_pack_index] = (mpu.angle[2]);
//  altitude_list[data_pack_index] = (bme.running_mean(self.bme.hight));
}

void iniciate_csv_file(){
  // --- SD --- //
  myFile = SD.open("flight_data.txt", FILE_WRITE);

  if (myFile) {
    for(int i = 0; i < columns_length; i++){
      myFile.print("," + columns[i]);
    }
    myFile.println("");
    myFile.close();
    Serial.println("SD initialized");
  } else {
    Serial.println("error opening test.txt");
  }
  // ---  --- //
}

float store_data(){
  // --- SD --- //
  myFile = SD.open("flight_data.txt", FILE_WRITE);

  if (myFile) {
     myFile.print(String(data_pack_index));
    for(int i = 0; i < columns_length; i++){
      myFile.print("," + String(1));
    }
    myFile.println("");
    myFile.close();
    Serial.println("done");
  } else {
    Serial.println("error opening test.txt");
  }
  // ---  --- //
}

void check_change(){
    // # --------------- #

    // # Decides

    // # --------------- #

    inst_z_vel = (altitude_list[data_pack_index] - altitude_list[data_pack_index - 1])/
      (time_list[data_pack_index] - time_list[data_pack_index - 1]);
    vel_filtered = running_mean(inst_z_vel);
    change_checker(vel_filtered);

    z_velocity_list[data_pack_index] = vel_filtered;
    sr_list[data_pack_index] = time_list[data_pack_index] - time_list[data_pack_index - 1];
}

void change_checker(float z_velocity){
  if(z_velocity < 0.2 and valid_value == false){
    t0 = millis();
    valid_value = true;
  }
  if(millis() - t0 > 1000 && valid_value == true){
    valid_value = false;
    open_parachute();
  }
}
