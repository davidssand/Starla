/*
  Communicate with BME280s with different I2C addresses
  Nathan Seidle @ SparkFun Electronics
  March 23, 2015

  Feel like supporting our work? Buy a board from SparkFun!
  https://www.sparkfun.com/products/14348 - Qwiic Combo Board
  https://www.sparkfun.com/products/13676 - BME280 Breakout Board

  This example shows how to connect two sensors on the same I2C bus.

  The BME280 has two I2C addresses: 0x77 (jumper open) or 0x76 (jumper closed)

  Hardware connections:
  BME280 -> Arduino
  GND -> GND
  3.3 -> 3.3
  SDA -> A4
  SCL -> A5
*/

#include <Wire.h>

#include "SparkFunBME280.h"


float pressure,temp,hight;


BME280 mySensorB; //Uses I2C address 0x76 (jumper closed)

struct bme_sensor{
  float pressure;
  float temp;
  float hight = pow((101325/pressure),((1/5.257)-1)) * (temp);
};

bme_sensor bme280 = {0, 0};

void setup()
{
  Serial.begin(9600);
  Serial.println("Example showing alternate I2C addresses");
  Wire.begin();
  mySensorB.setI2CAddress(0x76); //Connect to a second sensor
  if(mySensorB.beginI2C() == false) Serial.println("Sensor B connect failed");
}

void loop()
{
  bme280.pressure = mySensorB.readFloatPressure();
  bme280.temp = (mySensorB.readTempF() - 32.0) * 5/9;
  bm/e280.hight = pow((101325/bme280.pressure),((1/5.257)-1)) * (bme280.temp) ;

  Serial.print(" PressureB: ");
  Serial.print(bme280.pressure);

  Serial.print(" TempB: ");
  //Serial.print(mySensorB.readTempC(), 2);
  Serial.print(bme280.temp, 2);

  Serial.print(" Altura : ");
  Serial.print(bme280.hight);
  
  Serial.println();

  delay(50);
}
