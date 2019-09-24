# Author : David Sand
# Date   : 16/01/2019
#
# --------------------------------------

# Reading rate ≃ 20 ms

import smbus
import time
import bme280
import sys

sys.path.append("/home/pi/Starla")
from Sensors.Sensor import Sensor

class BME280(Sensor):
  def __init__(self, rm_lenght=50):
    super().__init__()

    self.device = 0x76  # Default device I2C address

    self.bus = smbus.SMBus(1)  

    bme280.load_calibration_params(self.bus, self.device)

    self.temperature = 0
    self.pressure = 0
    self.humidity = 0
    self.height = 0
    self.status = True

    # Filter
    # rm = running mean
    self.rm_lenght = rm_lenght
    self.rm_input_index = 0

    # Populating rm with initial value
    self.get_data()
    self.rm_result = [self.height for _ in range(0, self.rm_lenght)]
    self.rm_sum = self.height * self.rm_lenght
  
  def read_data(self):
    try:
      bme280_data = bme280.sample(self.bus, self.device)
      humidity  = bme280_data.humidity
      pressure  = bme280_data.pressure
      temperature = bme280_data.temperature
      height = ((1024/pressure)**(1/5.257) - 1) * (temperature + 273.15) / 0.0065
      return {"humidity": humidity, "pressure": pressure, "temperature": temperature, "height": height, "status": True}
    except:
      return {"humidity": self.humidity, "pressure": self.pressure, "temperature": self.temperature, "height": self.height, "status": False}

  def get_data(self):
    data = self.read_data()
    self.humidity = data["humidity"]
    self.pressure = data["pressure"]
    self.temperature = data["temperature"]
    self.height = data["height"]
    self.status = data["status"]

  def show_data(self):
    self.get_data()

    print("BME280")
    print("----------------")

    print("Temperature : ", self.temperature, "C")
    print("Pressure : ", self.pressure, "Pa")
    print("Humidity : ", self.humidity, "%")
    print("height : ", self.height, "m")
    print("status : ", self.status)

  def data_pack(self):
    self.get_data()
    data = [round(self.temperature, 1), round(self.pressure, 1), round(self.height, 1)]
    return data

  def running_mean(self, data):
    self.rm_sum -= self.rm_result[self.rm_input_index]
    self.rm_result[self.rm_input_index] = data
    self.rm_sum += self.rm_result[self.rm_input_index]
    self.rm_input_index = (self.rm_input_index + 1) % self.rm_lenght

    # print("result", self.rm_result)
    # print("input_index", self.rm_input_index)
    # print("sum", self.rm_sum)

    return self.rm_sum/self.rm_lenght
