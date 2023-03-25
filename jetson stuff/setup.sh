# updates
sudo apt update
sudo apt upgrade
sudo apt autoremove

# install virtual environments
sudo apt-get install python3-venv
mkdir project-junco && cd project-junco
python3 -m venv .venv
source .venv/bin/activate

# install python and pip
apt install python-pip python3-pip
pip3 install testresources
pip3 install --upgrade setuptools

# install i2c software
apt-get install libi2c-dev i2c-tools
sudo usermod -a -G i2c $USER

# install circuit python related software
pip3 install adafruit-blinka
pip3 install adafruit-circuitpython-bno08x
pip3 install adafruit-circuitpython-pca9685
pip3 install adafruit-circuitpython-servokit

# install DualShock controller software
set -e
pip3 install approxeng.input
cp ./scripts/dualshock4.py /usr/local/lib/python3.6/dist-packages/approxeng/input/dualshock4.py

# additional stuff

