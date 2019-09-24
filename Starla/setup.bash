# First make python3 the default, than execute this script

sudo apt-get update &&
echo "------ apt-get updated successfully" &&
sudo apt-get install -y python3-pip &&
echo "------ pip installed successfully" &&
sudo apt-get install -y python3-dev python3-rpi.gpio
echo "------ python3-dev and python3-rpi.gpio installed successfully" &&
sudo apt-get install -y python3-numpy &&
echo "------ numpy installed successfully" &&
sudo apt-get install -y python3-pandas &&
echo "------ pandas installed successfully" &&
sudo apt-get install -y python3-smbus &&
echo "------ smbus installed successfully" &&
sudo pip3 install RPi.bme280 &&
echo "------ RPi.bme280 installed successfully" &&
sudo pip3 install picamera &&
echo "------ picamera installed successfully"

echo "The system is now ready to be used"
