import picamera     # Importing the library for camera module
import time

class Camera(picamera.PiCamera):
    def __init__(self):
        super().__init__(resolution = (1920, 1080), framerate = 30)
        self.vflip = 180
        self.hflip = 180

    def startRecording(self):
        self.start_recording('/home/pi/Starla/CameraData/video.h264')

    def stopRecording(self):
        self.stop_recording()

    def takePicture(self):
        self.capture('/home/pi/Starla/CameraData/imag.jpg')



