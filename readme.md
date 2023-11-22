Description
===========

Python host API for manipulating the acceleration controller.
Implements binary communication with the microcontroller in CDC virtual com port mode.

- stream decoding
- stream recording
- device configuration (writing and reading to/from device)

Example
=======

```bash
+----------------------------------------------------------------------------------------------------------------------------+
| $ ./3dpaccel.py  set --range G16 |                                                                                         |
| $ ./3dpaccel.py  get --all       |                                                                                         |
| INFO:root:odr=ODR3200            |                                                                                         |
| INFO:root:scale=FULL_RES_4MG_LSB |                                                                                         |
| INFO:root:range=G16              |                                                                                         |
|                                  | $ ./3dpaccel.py decode -                                                                |
| $ ./3dpaccel.py stream --start 7 |                                                                                         |
|                                  | INFO:root:decode stream to stdout                                                       |
|                                  | INFO:root:Sampling Started maxSamples=7                                                 |
|                                  | INFO:root:#run #sample x[mg] y[mg] z[mg]                                                |
|                                  | INFO:root:00 00000 -0405.600 +0210.600 -1006.200                                        |
|                                  | INFO:root:00 00001 -0405.600 +0210.600 -1029.600                                        |
|                                  | INFO:root:00 00002 -0397.800 +0218.400 -1021.800                                        |
|                                  | INFO:root:00 00003 -0405.600 +0210.600 -1014.000                                        |
|                                  | INFO:root:00 00004 -0397.800 +0187.200 -1014.000                                        |
|                                  | INFO:root:00 00005 -0390.000 +0226.200 -1021.800```                                     |
|                                  | INFO:root:00 00006 -0390.000 +0210.600 -1021.800- WIP: many features not working yet    |
|                                  | INFO:root:Sampling Finished at sample 7                                                 |
|                                  | INFO:root:Device Setup: {'rate': 'ODR3200', 'range': 'G4', 'scale': 'FULL_RES_4MG_LSB'} |
|                                  | INFO:root:Sampling Stopped                                                              |
|                                  | INFO:root:run 00: processed 7 samples in 0.010278 s (3158.1 samples/s; 227383.7 baud)   |
+----------------------------------------------------------------------------------------------------------------------------+
```

Getting Started
===============

### Create Environment

```bash
sudo apt install python3-poetry
# alternatively apply script from install.python-poetry.org as 
# described in https://github.com/python-poetry/poetry#documentation
cd host-api/python
poetry shell

# minimal installation to run controller_cli.py
poetry install

# for datavis.py, record_step.py and record_step_series.py  
poetry install --all-extras

# for development (full installation)
poetry install --all-extras --with dev --with doc

# list discovered devices
controller_cli.py device --list

# retrieve device settings
controller_cli.py get --all
```

### With Initialized Environment

```bash
cd host-api/python
poetry shell

# list discovered devices
controller_cli.py device --list
```

**Read the Docs** at [3dp-accelerometer.github.io](https://3dp-accelerometer.github.io/py3dpaxxel)
