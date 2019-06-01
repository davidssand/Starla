
#include <SparkFunMPU9250-DMP.h>

MPU9250_DMP imu;

void setup() 
{
  Serial.begin(9600);

  if (imu.begin() != INV_SUCCESS)
  {
    while (1)
    {
      Serial.println(F("Unable to communicate with MPU-9250"));
      Serial.println(F("Check connections, and try again."));
      Serial.println();
      delay(1000);
    }
  }

  imu.setSensors(INV_XYZ_GYRO | INV_XYZ_ACCEL | INV_XYZ_COMPASS);
  imu.setGyroFSR(2000); // Set gyro to 2000 dps
  imu.setAccelFSR(2); // Set accel to +/-2g
  imu.setLPF(42); // Set LPF corner frequency to 5Hz
  imu.setSampleRate(10); // Set sample rate to 10Hz


}

void loop() 
{
  if ( imu.dataReady() )
  {
    imu.update(UPDATE_ACCEL | UPDATE_GYRO | UPDATE_COMPASS);
    printIMUData();
  }
}

void printIMUData(void)
{  
  float accelX = imu.calcAccel(imu.ax);
  accelX = accelX;
  float accelY = imu.calcAccel(imu.ay);
  accelY = accelY;
  float accelZ = imu.calcAccel(imu.az);
  float gyroX = imu.calcGyro(imu.gx);
  float gyroY = imu.calcGyro(imu.gy);
  float gyroZ = imu.calcGyro(imu.gz);

  
  Serial.println("Accel: " + String(accelX) + ", " +
              String(accelY) + ", " + String(accelZ) + " g");
  Serial.println("Gyro: " + String(gyroX) + ", " +
              String(gyroY) + ", " + String(gyroZ) + " dps");

  Serial.println("Time: " + String(imu.time) + " ms");
  Serial.println();
}
