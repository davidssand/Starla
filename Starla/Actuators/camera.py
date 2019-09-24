import picamera     # Importing the library for camera module
import time

class Camera(picamera.PiCamera):
  def __init__(self):
    try:
      super().__init__(resolution = (1920, 1080), framerate = 30)
      self.vflip = 180
      self.hflip = 180
    except Exception as ex:
      print(ex)

  def startRecording(self, path, time):
    try:
      self.start_recording(path + "time_" + str(int(time)) + ".h264")
    except:
      pass

  def stopRecording(self):
    try:
      self.stop_recording()
    except:
      pass

  def takePicture(self, path, time):
    try:
      self.capture(path + "time_" + str(int(time)) + ".jpg")
    except Exception as ex:
      print(ex)



