import picamera     # Importing the library for camera module
import time

objCamera = picamera.PiCamera()


class Camera():
    def __init__(self, vPixels, hPixels, framerate):
        #super().__init__()
        objCamera.resolution = (vPixels, hPixels)
        objCamera.framerate = framerate
        objCamera.vflip = 180
        objCamera.hflip = 180

    def startRecording(self):
        objCamera.start_recording('/home/pi/Components/Camera/video.h264')

    def stopRecording(self):
        objCamera.stop_recording()

    def takePicture(self):
        objCamera.capture('/home/pi/Components/Camera/imag.jpg')

