# Project Junco
RC Fixed Wing for Mobile Robotics at Northeastern University

<img src="https://user-images.githubusercontent.com/83112082/219784226-13e02755-722b-4fa2-a51d-c8f658bcd7af.jpg" width="40%" height="40%">

## Papers to read
Preliminary weight sizing of light pure-electric and hybrid-electric aircraft - [link](https://www.sciencedirect.com/science/article/pii/S2352146518300383?ref=pdf_download&fr=RR-2&rr=79b13761fdc53b9f) \
Electric Flight – Potential and Limitations - [link](https://elib.dlr.de/78726/1/MP-AVT-209-09.pdf) \
Airfoil choice - [link](http://airfoiltools.com/airfoil/details?airfoil=sd7062-il) \
Longitudinal Static Stability - [link](https://ocw.tudelft.nl/wp-content/uploads/Hand-out-Stability_01.pdf) \
Drone Design - [link](https://www.rand.org/content/dam/rand/pubs/research_reports/RR3000/RR3047/RAND_RR3047.pdf)


## About the program
I tried to be very complete in creating a useful model to streamline the initial design phase. The model is not without assumptions but (in my opinion) represents a helpful tool in novel a/c design.
\
\
Some physical phenomenon that are modeled include:
  - Skin friction drag with a boundary layer theory.
  - Form drag from airfoil data
  - FAA structural loading limits
  - Disk loading to estimate hovering power costs
  - Taper ratio and induced drag
  - Euler bending beam theory for thin structures (torsion and bending)
  - Battery considerations for electric flight

# Equipment Purchasing
 
| Name | Units |
| --- | --- |
| [Jetson Nano](https://www.sparkfun.com/products/16271) | 1 |
| [Wifi Chip](https://www.amazon.com/gp/product/B01MZA1AB2/ref=ppx_yo_dt_b_asin_title_o00_s01?ie=UTF8&psc=1) | 1 |
| [Antennas](https://www.amazon.com/gp/product/B07QKF18KM/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1) | 1 |
| [GPS]() | 1 |
| [IMU]() | 1 |
| [Differential Pressure Sensor]() | 1 |
| [Time of Flight Sensor](https://www.adafruit.com/product/5425) | 1 |
| [atmos sensor](https://www.adafruit.com/product/4716) |  |
| [fan for jetson](https://www.amazon.com/gp/product/B07TYZ3RG5/ref=ppx_yo_dt_b_asin_title_o00_s02?ie=UTF8&th=1) | 1 |
| [servos](https://www.horizonhobby.com/product/hs-85mg-micro-analog-metal-gear-servo/HRC32085S.html) | 1 |
| [servo cables](https://www.adafruit.com/product/973) | 4 |
| [servo board](https://www.adafruit.com/product/815) | 1 |
| [stemma cables](https://www.adafruit.com/product/4210) | 1 |
| [motor]() | 1 |
| [comms system](https://www.sparkfun.com/products/20029) | 1 |
| []() |  |
| []() |  |
| []() |  |
| []() |  |


# Jetson Nano - Setup
1. Download and install the SD card image onto the Nano. Official instructions on [Nvidia](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit#write).

2. Increase the swap on the Nano. Official instructions on [Youtube](https://youtu.be/uvU8AXY1170).

3. Update the Jetson Nano
```
$ sudo apt update
$ sudo apt upgrade
$ sudo apt autoremove
```

4. Setup virtual environments
```
$ sudo apt-get install python3-venv
$ mkdir project-junco && cd project-junco
$ python3 -m venv .venv
$ source .venv/bin/activate
```

5. Install Python and Pip in venv
```
(venv) $ apt install python-pip python3-pip
(venv) $ pip3 install testresources
(venv) $ pip3 install --upgrade setuptools
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
(venv) $ pip3 install adafruit-blinka
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
(venv) $ pip3 install adafruit-circuitpython-bno08x
```
Test the IMU stream with:
```
import board
import busio
from adafruit_bno08x.i2c import BNO08X_I2C
from adafruit_bno08x import BNO_REPORT_ACCELEROMETER
from adafruit_bno08x import BNO_REPORT_ROTATION_VECTOR

i2c = busio.I2C(board.SCL, board.SDA)
bno = BNO08X_I2C(i2c)
bno.enable_feature(BNO_REPORT_ACCELEROMETER)
bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

while True:
    accel_x, accel_y, accel_z = bno.acceleration  # pylint:disable=no-member
    i, j, k, w = bno.quaternion  # pylint:disable=no-member
    print("X: %0.6f  Y: %0.6f Z: %0.6f  m/s^2" % (accel_x, accel_y, accel_z))
    print("I: %0.6f J: %0.6f K: %0.6f REAL: %0.6f" % (i,j,k,w))

```
```
(venv) $ python3 imu_test.py
```

10. Adafruit MiniGPS PA1010D help can be found on the following [instrustructions](https://learn.adafruit.com/adafruit-mini-gps-pa1010d-module/circuitpython-python-i2c-usage).
Test the GPS stream with:
```
import time
import board
import busio

import adafruit_gps

# If using I2C, we'll create an I2C interface to talk to using default pins
i2c = board.I2C()  # uses board.SCL and board.SDA

# Create a GPS module instance.
gps = adafruit_gps.GPS_GtopI2C(i2c)  # Use I2C interface

# Turn on the basic GGA and RMC info (what you typically want)
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")

# Set update rate to once a second (1hz) which is what you typically want.
gps.send_command(b"PMTK220,1000")

# Main loop runs forever printing data as it comes in
timestamp = time.monotonic()
while True:
    data = gps.read(32)  # read up to 32 bytes
    # print(data)  # this is a bytearray type

    if data is not None:
        # convert bytearray to string
        data_string = "".join([chr(b) for b in data])
        print(data_string, end="")

    if time.monotonic() - timestamp > 5:
        # every 5 seconds...
        gps.send_command(b"PMTK605")  # request firmware version
        timestamp = time.monotonic()
```
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
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""Simple test for a standard servo on channel 0 and a continuous rotation servo on channel 1."""
import time
from adafruit_servokit import ServoKit

# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
kit = ServoKit(channels=8)

kit.servo[0].angle = 180
kit.continuous_servo[1].throttle = 1
time.sleep(1)
kit.continuous_servo[1].throttle = -1
time.sleep(1)
kit.servo[0].angle = 0
kit.continuous_servo[1].throttle = 0
```

```
(venv) $ python3 servo_test.py
```


14. Sony DualShock4 software install:
```
(venv) $ set -e
(venv) $ pip3 install approxeng.input
(venv) $ sudo cp ./scripts/dualshock4.py /usr/local/lib/python3.6/dist-packages/approxeng/input/dualshock4.py
```

15. Pair DualShock4 controller with Jetson Nano over bluetooth.
- open bluetooth settings and click the + to add a device
- filter so only "Joypad" is visible
- while pressing and holding the SHARE button, press and hold the PS Button until the light bar flashes. Enable Bluetooth on your device, and then select the controller from the list of Bluetooth devices. When pairing is complete, the light bar blinks, and then the player indicator lights up.
- add the wireless controller

17. Test controller and servos:

```
# SDA = pin.SDA_1
# SCL = pin.SCL_1
# SDA_1 = pin.SDA
# SCL_1 = pin.SCL

from adafruit_servokit import ServoKit
import board
import busio
import time
from approxeng.input.selectbinder import ControllerResource


# On the Jetson Nano
# Bus 0 (pins 28,27) is board SCL_1, SDA_1 in the jetson board definition file
# Bus 1 (pins 5, 3) is board SCL, SDA in the jetson definition file
# Default is to Bus 1; We are using Bus 0, so we need to construct the busio first ...
print("Initializing Servos")
i2c_bus0=(busio.I2C(board.SCL_1, board.SDA_1))
print("Initializing ServoKit")
kit = ServoKit(channels=16, i2c=i2c_bus0)
# kit[0] is the bottom servo
# kit[1] is the top servo
print("Done initializing")
sweep = range(0,180)
for degree in sweep :
    kit.servo[0].angle=degree
    # kit.servo[1].angle=degree
    # time.sleep(0.01)

time.sleep(0.5)
sweep = range(180,0, -1)
for degree in sweep :
    kit.servo[0].angle=degree
    
last_presses = None
while True:
       with ControllerResource() as joystick:
           print(type(joystick).__name__)
           while joystick.connected:
                axis_list = [ 'lx', 'ry' ]
                for axis_name in axis_list:
                    # desired_angle is in degrees
                    joystick_value = joystick[axis_name]
                    # The joystick value goes from -1.0 ... 1.0 (a range of 2)
                    # Normalize within a range of 180 degrees
                    desired_angle = (joystick_value+1)/2*180
                    
                    if  axis_name == 'lx' :
                        kit.servo[0].angle=desired_angle
                        # print(axis_name, joystick[axis_name])
                        
                    if axis_name == 'ry' :
                         kit.continuous_servo[1].throttle=joystick[axis_name]
```
```
(venv) $ servo_ps4_test.py
```

16. 
```
$ sudo pip3 install adafruit-circuitpython-ms8607
```

```
# SPDX-FileCopyrightText: 2020 Bryan Siepert, written for Adafruit Industries
# SPDX-License-Identifier: MIT
from time import sleep
import board
from adafruit_ms8607 import MS8607

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
sensor = MS8607(i2c)

while True:

    print("Pressure: %.2f hPa" % sensor.pressure)
    print("Temperature: %.2f C" % sensor.temperature)
    print("Humidity: %.2f %% rH" % sensor.relative_humidity)
    print("\n------------------------------------------------\n")
    sleep(1)
```

