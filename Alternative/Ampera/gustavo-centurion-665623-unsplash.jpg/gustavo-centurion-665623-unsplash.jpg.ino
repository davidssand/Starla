//26/nov/2018

#include <SD.h>
#include <SPI.h>
#include <Amp_CAN.h>  //Biblioteca interna para tratamento do CAN bus
#include <DS3231.h>
#include <Wire.h>

//DS3231:  SDA pin   -> Arduino Analog 4 or the dedicated SDA pin
//         SCL pin   -> Arduino Analog 5 or the dedicated SCL pin
//         Endereço : 0x68 (cuidar com endereco do MPU6050)

#define SPI_SS_SD 9     //Pino SS do SD
#define SPI_SS_CAN 10
#define LED_DAQ 5
/*
#define SERIAL
#define SD_CARD
#define CAN_BUS
#define RTC
#define MPU_6050
#define ESCRITASD
//#define LEITURASD
*/

const int MPU_addr=0x69;  // I2C address of the MPU-6050 + 1 (Vcc --> AD0)
int16_t AcX,AcY,AcZ,Tmp,GyX,GyY,GyZ; //Variaveis adquiridas pelo MPU6050


UNO can_bus(SPI_SS_CAN);
Frame msg_can;
File arquivotxt;
DS3231  rtc(SDA, SCL);

void setup(){
  #ifdef SERIAL 
  Serial.begin(9600);
  #endif

  pinMode(LED_DAQ, OUTPUT);
  
  Wire.begin();
  Wire.beginTransmission(MPU_addr);
  Wire.write(0x6B);  // PWR_MGMT_1 register
  Wire.write(0);     // set to zero (wakes up the MPU-6050)
  Wire.endTransmission(true);
  
  rtc.begin(); // inicializa o módulo de data e hora

  can_bus.setup();//Inicializa o barramento CAN (setup dos mcp 2515 e 2551)
  
  #ifdef SERIAL 
  Serial.print("Initializing SD card...");
  if (!SD.begin(SPI_SS_SD)) {
    Serial.println("initialization failed!");
    return;
  }
  Serial.println("initialization done.");
  #endif
}

void loop(){
  can_bus.read(&msg_can); //Guarda o valor de leitura no endereco do frame "msg_can"
  if (msg_can.data != 0){
    digitalWrite(LED_DAQ,HIGH);
  }
  Wire.beginTransmission(MPU_addr); 
  Wire.write(0x3B);  // starting with register 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_addr,14,true);  // request a total of 14 registers
  AcX=Wire.read()<<8|Wire.read();  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)    
  AcY=Wire.read()<<8|Wire.read();  // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
  AcZ=Wire.read()<<8|Wire.read();  // 0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
  Tmp=Wire.read()<<8|Wire.read();  // 0x41 (TEMP_OUT_H) & 0x42 (TEMP_OUT_L)
  GyX=Wire.read()<<8|Wire.read();  // 0x43 (GYRO_XOUT_H) & 0x44 (GYRO_XOUT_L)
  GyY=Wire.read()<<8|Wire.read();  // 0x45 (GYRO_YOUT_H) & 0x46 (GYRO_YOUT_L)
  GyZ=Wire.read()<<8|Wire.read();  // 0x47 (GYRO_ZOUT_H) & 0x48 (GYRO_ZOUT_L)
  
  #ifdef SERIAL  
    Serial.print("ID CAN: ");
    Serial.println(msg_can.id, HEX);
    Serial.print("Mensagem: ");
    Serial.println((uint32_t)(msg_can.data >> 32), HEX);
    Serial.println((uint32_t)(msg_can.data >> 0), HEX);
    Serial.print("Data:");
    Serial.print(rtc.getDOWStr()); // dia da semana
    Serial.print(" ");
    Serial.print(rtc.getDateStr()); // dia
    Serial.print(" -- ");
    Serial.println(rtc.getTimeStr()); // hora
  
    Serial.print("AcX = "); Serial.print(AcX);
    Serial.print(" | AcY = "); Serial.print(AcY); 
    Serial.print(" | AcZ = "); Serial.print(AcZ);
    Serial.print(" | Tmp = "); Serial.print(Tmp/340.00+36.53);  //equation for temperature in degrees C from datasheet
    Serial.print(" | GyX = "); Serial.println(GyX);
    Serial.print(" | GyY = "); Serial.print(GyY);
    Serial.print(" | GyZ = "); Serial.println(GyZ);
    Serial.println("------------------------------------");
  #endif

  //Escrita dos dados no cartao SD
  arquivotxt = SD.open("dadoscan.txt", FILE_WRITE); //O nome do arquivo deve conter apenas letras
 //#ifdef SD_CARD
  if(arquivotxt){
    digitalWrite(LED_DAQ,HIGH);
  //#ifdef CAN_BUS
    arquivotxt.print("ID CAN: ");
    arquivotxt.println(msg_can.id, HEX);
    arquivotxt.print("Mensagem: ");
    arquivotxt.println((uint32_t)(msg_can.data >> 32), HEX);
    arquivotxt.println((uint32_t)(msg_can.data >> 0), HEX);
  //#endif
  //#ifdef RTC  
    arquivotxt.print("Data:");
    arquivotxt.print(rtc.getDOWStr()); // dia da semana
    arquivotxt.print(" ");
    arquivotxt.print(rtc.getDateStr()); // dia
    arquivotxt.print(" -- ");
    arquivotxt.println(rtc.getTimeStr()); // hora
  //#endif
  //#ifdef MPU_6050
    arquivotxt.print("AcX = "); Serial.print(AcX);
    arquivotxt.print(" | AcY = "); Serial.print(AcY); 
    arquivotxt.print(" | AcZ = "); Serial.print(AcZ);
    arquivotxt.print(" | Tmp = "); Serial.print(Tmp/340.00+36.53);  //equation for temperature in degrees C from datasheet
    arquivotxt.print(" | GyX = "); Serial.println(GyX);
    arquivotxt.print(" | GyY = "); Serial.print(GyY);
    arquivotxt.print(" | GyZ = "); Serial.println(GyZ);
    arquivotxt.println("------------------------------------");
  //#endif
    arquivotxt.close();   //Apos realizar a escrita, é necessario fechar o arquivo antes de poder acessar o SD novamente
  }else{  //  Verifica se abriu o arquivo
    digitalWrite(LED_DAQ,LOW);
  }
 //#endif
  delay(100);
}
