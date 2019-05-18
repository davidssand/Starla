import smbus
import time

class Arduino:
  def __init__(self):
    self.bus = smbus.SMBus(1)
    self.address = 0x08

    print("Esperando 2 segundos")

    time.sleep(2)

  def start_reading(self):
    print("Iniciando leitura")
    while 1:
      data = self.bus.read_i2c_block_data(self.address, 0, 32)
      print("Leitura por bloco")
      print(data)
      time.sleep(0.5)

arduino = Arduino()
arduino.start_reading()