import bme280
import smbus2
from time import sleep

port = 1
address = 0x76 # Adafruit BME280 address. Other BME280s may be different
bus = smbus2.SMBus(port)

bme280.load_calibration_params(bus,address)

while True:
    bme280_data = bme280.sample(bus,address)
    humidity  = bme280_data.humidity
    pressure  = bme280_data.pressure
    ambient_temperature = bme280_data.temperature

    a = (1024/pressure)**(1/5.257)
    height_1 = (a - 1) * (ambient_temperature + 273.15) / 0.0065
    height_2 = 44330*(1-(1024/pressure)**(1/5.257))
    print(humidity, pressure, ambient_temperature, height_1, height_2)
    sleep(1)