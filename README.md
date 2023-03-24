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

## Jetson Nano - Setup
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

6. Install [Adafruit Blinka](https://pypi.org/project/Adafruit-Blinka/) in venv:
```
(venv) $ pip3 install adafruit-blinka
```

5. Adafruit 9-DOF Orientation IMU Fusion Breakout - BNO085 help can be found on the following [instrustructions](https://github.com/adafruit/Adafruit_CircuitPython_BNO08x). Install in venv:
```
(venv) $ pip3 install adafruit-circuitpython-bno08x
```
Test the IMU stream with:
```
(venv) $ python3 imu_test.py
```

8. Adafruit MiniGPS PA1010D help can be found on the following [instrustructions](https://learn.adafruit.com/adafruit-mini-gps-pa1010d-module/circuitpython-python-i2c-usage)
Test the GPS stream with:
```
(venv) $ python3 gps_test.py
```
