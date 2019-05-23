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

void iniciate_csv_file(){
  Serial.print("Initializing SD card...");

  if (!SD.begin(4)) {
    Serial.println("initialization failed!");
    while (1);
  }
  SD.remove("test.txt");
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
