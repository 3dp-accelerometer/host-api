Description
-----------

Python host API for communicating with the accelerator.
Allows reading and setting device configuration and to start/stop data stream from device.

- WIP: many features not working yet
- see `3dpaccel.py --help`
- example

      3dpaccel.py get --all  # read all settings from device
      odr=ODR200
      scale=FULL_RES_G4
      range=G4

- communicates in binary (not ascii)

Prerequisites
-------------

1. `venv -m venv venv`
2. `source venv/bin/activate`
3. `pip install pyserial`
