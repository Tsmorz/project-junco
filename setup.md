# Jetson Nano - Setup
1. Download and install the SD card image onto the Nano. Official instructions on [Nvidia](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit#write).

2. Increase the swap on the Nano. Official instructions on [Youtube](https://youtu.be/uvU8AXY1170).
```
$ free -m
$ sudo systemctl disable nvzramconfig
$ sudo fallocate -l 4G /mnt/4GB.swap
$ sudo chmod 600 /mnt/4GB.swap
$ sudo mkswap /mnt/4GB.swap
$ sudo vi /etc/fstab
```
```
# add the line below
/mnt/4GB.swap swap swap defaults 0 0
```
```
$ sudo reboot
```

3. Update the Jetson Nano
```
$ sudo apt update
$ sudo apt upgrade
$ sudo reboot
```

4. Setup virtual environments
```
$ sudo apt-get install python3-venv
$ mkdir project-junco && cd project-junco
$ python3 -m venv venv-junco
$ source venv-junco/bin/activate
```

5. Edit .bashrc file
```
# add this line after the rest of your aliases
alias venv='source ~/project-junco/venv-junco/bin/activate'
```
```
$ sudo reboot
```

5. Install Python and Pip in venv
```
$ venv
(venv) $ sudo apt install python-pip python3-pip
(venv) $ pip3 install testresources
(venv) $ pip3 install --upgrade setuptools
(venv) $ pip install -U pip setuptools 

```

## ROS install

```
$ sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
$ sudo apt install curl # if you haven't already installed curl
$ curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
$ sudo apt update
$ sudo apt install ros-melodic-desktop

$ echo "source /opt/ros/melodic/setup.bash" >> ~/.bashrc
$ source ~/.bashrc

$ sudo apt install python-rosdep python-rosinstall python-rosinstall-generator python-wstool build-essential

$ sudo apt install python-rosdep

$ sudo rosdep init
$ rosdep update
```


6. Install i2c development tools in venv:
```
(venv) $ sudo apt-get install libi2c-dev i2c-tools
(venv) $ sudo usermod -a -G i2c $USER
```

7. Testing for connect i2c devices:
```
(venv) $ sudo i2cdetect -y -r 1
```
There should be an output similar to the one below with the individual i2c devices corresponding the the IDs.
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
10: 10 -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- 4a -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --                         
```

8. Install [Adafruit Blinka](https://pypi.org/project/Adafruit-Blinka/) in venv:
```
(venv) $ sudo -H pip3 install adafruit-blinka
```

9. Connect the external sensors to the Jetson Nano. This is for the GPS and IMU with Stemma QT ports.
 
| Name | Color | Pin |
| --- | --- | --- |
| VIN | red | 2 |
| GND | black | 6 |
| SDA | blue | 3 |
| SCL | yellow | 5 |


10. Adafruit 9-DOF Orientation IMU Fusion Breakout - BNO085 help can be found on the following [instrustructions](https://github.com/adafruit/Adafruit_CircuitPython_BNO08x). Install in venv:
```
(venv) $ sudo apt update
sudo apt upgrade
sudo apt install nano
pip3 install adafruit-circuitpython-bno08x
```
Test the IMU stream with:
```
(venv) $ python3 imu_test.py
```

10. Adafruit MiniGPS PA1010D help can be found on the following [instrustructions](https://learn.adafruit.com/adafruit-mini-gps-pa1010d-module/circuitpython-python-i2c-usage).
Test the GPS stream with:
```
(venv) $ python3 gps_test.py
```

11. Install the servo board [software](https://docs.circuitpython.org/projects/servokit/en/latest/) from [Adafruit](https://learn.adafruit.com/16-channel-pwm-servo-driver?view=all&gclid=Cj0KCQjwlPWgBhDHARIsAH2xdNchkmeukeVPBQ1IYITSDNilWz4_tKLZpCee6GZLfH17hK6oDafZ5_0aAszsEALw_wcB#python-circuitpython). A helpful page can be found [here](https://jetsonhacks.com/2019/07/22/jetson-nano-using-i2c/) and a video can be found [here](https://www.youtube.com/watch?v=RnGUTny1hG8).
```
(venv) $ pip3 install adafruit-circuitpython-pca9685
(venv) $ pip3 install adafruit-circuitpython-servokit
```
| Name | Color | Pin |
| --- | --- | --- |
| VIN | red | 17 (3V3) |
| GND | black | 39 |
| SDA | blue | 27 |
| SCL | yellow | 28 |

12. Check for proper wiring and i2c detection:
```
(venv) $ i2cdetect -y -r 0

     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: 40 -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: 70 -- -- -- -- -- -- --                         
```

13. Test the servos for movement:

```
(venv) $ python3 servo_test.py
```


14. Sony DualShock4 software install:
```
(venv) $ set -e
(venv) $ pip3 install approxeng.input
(venv) $ sudo cp ./scripts/dualshock4.py /usr/local/lib/python3.6/dist-packages/approxeng/input/dualshock4.py
```
DualShock4, axes=['Left Horizontal=0', 'Left Vertical=0', 'Right Horizontal=0', 'Right Vertical=0', 'Left Trigger=0', 'Right Trigger=0', 'D-pad Horizontal=0', 'D-pad Vertical=0', 'Yaw rate=0', 'Roll=0', 'Pitch=0', 'Touch X=0', 'Touch Y=0'], buttons=<approxeng.input.Buttons object at 0x7fcaf5bf77f0>


15. Pair DualShock4 controller with Jetson Nano over bluetooth.
- open bluetooth settings and click the + to add a device
- filter so only "Joypad" is visible
- while pressing and holding the SHARE button, press and hold the PS Button until the light bar flashes. Enable Bluetooth on your device, and then select the controller from the list of Bluetooth devices. When pairing is complete, the light bar blinks, and then the player indicator lights up.
- add the wireless controller

17. Test controller and servos:
```
(venv) $ servo_ps4_test.py
```
