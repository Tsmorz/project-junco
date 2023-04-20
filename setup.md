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

3. Update the Jetson Nano
```
$ sudo apt update
$ sudo apt upgrade
$ sudo autoremove
```

3. Update the Jetson Nano
```
$ sudo apt install python3-pip
$ pip3 install --upgrade setuptools
$ pip3 install wheel
$ pip3 install testresources
$ pip3 install -U pip setuptools
```

4.
```
$ sudo /opt/nvidia/jetson-io/jetson-io.py
```


5.
```
$ sudo groupadd -f -r gpio
$ sudo usermod -a -G gpio jetsmorz
$ cd ~
$ git clone https://github.com/NVIDIA/jetson-gpio.git 
$ sudo cp ~/jetson-gpio/lib/python/Jetson/GPIO/99-gpio.rules /etc/udev/rules.d
$ sudo reboot
```

5.
```
$ pip3 install adafruit-blinka
```

4. Setup virtual environments
```
$ apt-get install python3-venv
$ mkdir ~/Documents/junco && cd ~/Documents/junco
$ python3 -m venv venv-junco
$ source venv-junco/bin/activate
```

5. Edit .bashrc file
```
# add this line after the rest of your aliases
alias venv='source ~/Documents/junco/venv-junco/bin/activate'
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
(venv) $ pip install wheel
```
