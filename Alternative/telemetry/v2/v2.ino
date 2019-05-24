/*
  SD card read/write

 This example shows how to read and write data to and from an SD card file
 The circuit:
 * SD card attached to SPI bus as follows:
 ** MOSI - pin 11
 ** MISO - pin 12
 ** CLK - pin 13
 ** CS - pin 4 (for MKRZero SD: SDCARD_SS_PIN)

 by David

 */

#include <SPI.h>
#include <SD.h>

// SD
File myFile;
const int columns_length = 2;
String columns[columns_length] = {"Coluna1", "Coluna2"};


#include <Servo.h>

Servo parachute_servos;

int parachute_servos_pos = 0;

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

// --- Setup --- //

void setup() {
  Serial.begin(9600);
  
  parachute_servos.attach(9);

  for (int i = 0; i < rm_lenght; i++){
    rm_result[i] = 0;
  }
  
  while (!Serial) {
    ;
  }

  iniciate_csv_file();

  system_time = millis();
}

// --- Loop --- //

void loop() {
  store_data();
  data_pack_index++;
  delay(1000);
  if((millis() - system_time) > 5000){
    read_txt();
    while(1){
      ;
    }
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
  Serial.print("Initializing SD card...");

  if (!SD.begin(4)) {
    Serial.println("initialization failed!");
    while (1);
  }
//  SD.remove("test.txt");
  Serial.println("initialization done.");

  myFile = SD.open("test.txt", FILE_WRITE);

  if (myFile) {
    for(int i = 0; i < columns_length; i++){
      myFile.print("," + columns[i]);
    }
    myFile.println();
    myFile.close();
  } else {
    // if the file didn't open, print an error:
    Serial.println("error opening test.txt");
  }
}

float store_data(){
  // --- SD --- //
  myFile = SD.open("test.txt", FILE_WRITE);
  myFile.print(data_pack_index);
  if (myFile) {
    for(int i = 0; i < columns_length; i++){
      myFile.print("," + String(1));
    }
    myFile.println("");
    myFile.close();
  } else {
    Serial.println("error opening test.txt");
  }
  // ---  --- //
}

void read_txt(){
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
  valid_value = z_velocity < 0.2;
  if(z_velocity < 0.2 and !valid_value) t0 = millis();
  if(millis() - t0 > 1000 && valid_value) open_parachute();
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
