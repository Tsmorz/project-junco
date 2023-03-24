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
$ sudo apt update && sudo apt upgrade
```
4.
```
$ sudo apt install python-pip python3-pip
```
5.
6.
