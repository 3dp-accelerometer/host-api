Introduction
============

Python host API for manipulating the acceleration [controller](https://github.com/3dp-accelerometer/controller/).
Implements binary communication with the microcontroller in CDC virtual com port mode.
This package not only provides a Python API but also command line scripts to operate the controller.

- start/stop sampling (in streaming mode or up to specific limit of samples)
- configure/reset device (output data rate, range, scale)
- decode samples from controller
- print samples or store in tabular separated values file

See also:

- Controller [Firmware](https://github.com/3dp-accelerometer/controller)
- OctoPrint plugin [Octoprint Accelerometer](https://github.com/3dp-accelerometer/octoprint-accelerometer)
- **Read the Docs** at [3dp-accelerometer.github.io](https://3dp-accelerometer.github.io/py3dpaxxel/)

[![Build Test Docs](https://github.com/3dp-accelerometer/py3dpaxxel/actions/workflows/pack-builddocs.yaml/badge.svg)](https://github.com/3dp-accelerometer/py3dpaxxel/actions/workflows/pack-builddocs.yaml)

Example
=======

The following example illustrates how to configure and stream from the controller using CLI.
First the controller configuration takes place (left shell).
The controller uses it full `16g` range at an output data rate of `3200ks/s` where the scale is set at full resolution, meaning each LSB equals `4mg`.
Subsequently, the decoder is started and waiting for the controller's data stream (right shell).
Finally, on the left shell, the streaming of `7` samples is triggered.
The stream from the controller also contains all required metadata for data integrity so that the decoder either reports a valid and complete stream or error.

```bash
+------------------------------------------------------------------------------------------+
| $ ./controller_cli.py set --range G16 |                                                  |
| $ ./controller_cli.py get --all       |                                                  |
| version=0.1.1                         |                                                  |
| odr=ODR3200                           |                                                  |
| scale=FULL_RES_4MG_LSB                |                                                  |
| range=G16                             |                                                  |
|                                       | $ ./controller_cli.py decode -                   |
| $ ./3dpaccel.py stream --start 7      |                                                  |
|                                       | decode stream to stdout                          |
|                                       | Sampling Started maxSamples=7                    |
|                                       | #run #sample x[mg] y[mg] z[mg]                   |
|                                       | 00 00000 -0405.600 +0210.600 -1006.200           |
|                                       | 00 00001 -0405.600 +0210.600 -1029.600           |
|                                       | 00 00002 -0397.800 +0218.400 -1021.800           |
|                                       | 00 00003 -0405.600 +0210.600 -1014.000           |
|                                       | 00 00004 -0397.800 +0187.200 -1014.000           |
|                                       | 00 00005 -0390.000 +0226.200 -1021.800           |
|                                       | 00 00006 -0390.000 +0210.600 -1021.800           |
|                                       | Sampling Finished at sample 7                    |
|                                       | Device Setup: {'rate': 'ODR3200', 'range': 'G4', |
|                                       | 'scale': 'FULL_RES_4MG_LSB', 'version': '0.1.1'} |
|                                       | Sampling Stopped                                 |
|                                       | run 00: processed 7 samples in 0.010278s         |
|                                       | (3158.1 samples/s; 227383.7 baud)                |
+------------------------------------------------------------------------------------------+
```

Getting Started
===============

Create Environment
------------------

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

# list discovered devices
controller_cli.py device --list
```

With Initialized Environment
----------------------------

```bash
cd host-api/python
poetry shell
# list discovered devices
controller_cli.py device --list
```

For all available CLI scripts refer to [Commandline Scripts](https://3dp-accelerometer.github.io/py3dpaxxel/index.html).
