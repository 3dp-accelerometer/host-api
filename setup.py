# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py3dpaxxel',
 'py3dpaxxel.cli',
 'py3dpaxxel.controller',
 'py3dpaxxel.data_decomposition',
 'py3dpaxxel.gcode',
 'py3dpaxxel.log',
 'py3dpaxxel.octoprint',
 'py3dpaxxel.samples',
 'py3dpaxxel.sampling_tasks',
 'py3dpaxxel.scripts',
 'py3dpaxxel.storage']

package_data = \
{'': ['*'],
 'py3dpaxxel': ['test_data/.keep',
                'test_data/.keep',
                'test_data/.keep',
                'test_data/.keep',
                'test_data/.keep',
                'test_data/.keep',
                'test_data/.keep',
                'test_data/test-a81829a6-20231126-185307879-s000-ax-f010-z015.tsv',
                'test_data/test-a81829a6-20231126-185307879-s000-ax-f010-z015.tsv',
                'test_data/test-a81829a6-20231126-185307879-s000-ax-f010-z015.tsv',
                'test_data/test-a81829a6-20231126-185307879-s000-ax-f010-z015.tsv',
                'test_data/test-a81829a6-20231126-185307879-s000-ax-f010-z015.tsv',
                'test_data/test-a81829a6-20231126-185307879-s000-ax-f010-z015.tsv',
                'test_data/test-a81829a6-20231126-185307879-s000-ax-f010-z015.tsv',
                'test_data/test-a81829a6-20231126-185309467-s000-ax-f020-z015.tsv',
                'test_data/test-a81829a6-20231126-185309467-s000-ax-f020-z015.tsv',
                'test_data/test-a81829a6-20231126-185309467-s000-ax-f020-z015.tsv',
                'test_data/test-a81829a6-20231126-185309467-s000-ax-f020-z015.tsv',
                'test_data/test-a81829a6-20231126-185309467-s000-ax-f020-z015.tsv',
                'test_data/test-a81829a6-20231126-185309467-s000-ax-f020-z015.tsv',
                'test_data/test-a81829a6-20231126-185309467-s000-ax-f020-z015.tsv',
                'test_data/test-a81829a6-20231126-185310982-s000-ax-f030-z015.tsv',
                'test_data/test-a81829a6-20231126-185310982-s000-ax-f030-z015.tsv',
                'test_data/test-a81829a6-20231126-185310982-s000-ax-f030-z015.tsv',
                'test_data/test-a81829a6-20231126-185310982-s000-ax-f030-z015.tsv',
                'test_data/test-a81829a6-20231126-185310982-s000-ax-f030-z015.tsv',
                'test_data/test-a81829a6-20231126-185310982-s000-ax-f030-z015.tsv',
                'test_data/test-a81829a6-20231126-185310982-s000-ax-f030-z015.tsv',
                'test_data/test-a81829a6-20231126-185312497-s000-ax-f040-z015.tsv',
                'test_data/test-a81829a6-20231126-185312497-s000-ax-f040-z015.tsv',
                'test_data/test-a81829a6-20231126-185312497-s000-ax-f040-z015.tsv',
                'test_data/test-a81829a6-20231126-185312497-s000-ax-f040-z015.tsv',
                'test_data/test-a81829a6-20231126-185312497-s000-ax-f040-z015.tsv',
                'test_data/test-a81829a6-20231126-185312497-s000-ax-f040-z015.tsv',
                'test_data/test-a81829a6-20231126-185312497-s000-ax-f040-z015.tsv',
                'test_data/test-a81829a6-20231126-185314012-s000-ax-f050-z015.tsv',
                'test_data/test-a81829a6-20231126-185314012-s000-ax-f050-z015.tsv',
                'test_data/test-a81829a6-20231126-185314012-s000-ax-f050-z015.tsv',
                'test_data/test-a81829a6-20231126-185314012-s000-ax-f050-z015.tsv',
                'test_data/test-a81829a6-20231126-185314012-s000-ax-f050-z015.tsv',
                'test_data/test-a81829a6-20231126-185314012-s000-ax-f050-z015.tsv',
                'test_data/test-a81829a6-20231126-185314012-s000-ax-f050-z015.tsv',
                'test_data/test-a81829a6-20231126-185315527-s000-ax-f060-z015.tsv',
                'test_data/test-a81829a6-20231126-185315527-s000-ax-f060-z015.tsv',
                'test_data/test-a81829a6-20231126-185315527-s000-ax-f060-z015.tsv',
                'test_data/test-a81829a6-20231126-185315527-s000-ax-f060-z015.tsv',
                'test_data/test-a81829a6-20231126-185315527-s000-ax-f060-z015.tsv',
                'test_data/test-a81829a6-20231126-185315527-s000-ax-f060-z015.tsv',
                'test_data/test-a81829a6-20231126-185315527-s000-ax-f060-z015.tsv']}

install_requires = \
['pyaml>=23.9.7,<24.0.0', 'pyserial>=3.5,<4.0']

extras_require = \
{'data-decomposition': ['numpy>=1.24.2,<2.0.0', 'scipy>=1.10.1,<2.0.0'],
 'data-visualization': ['numpy>=1.24.2,<2.0.0',
                        'scipy>=1.10.1,<2.0.0',
                        'matplotlib>=3.5.2,<4.0.0'],
 'octoprint-remote': ['requests>=2.28.1,<3.0.0']}

setup_kwargs = {
    'name': 'py3dpaxxel',
    'version': '0.1.9',
    'description': 'Python API for interacting with the 3DP Accelerometer controller and sensor data visualization.',
    'long_description': "Description\n===========\n\nPython host API for manipulating the acceleration controller.\nImplements binary communication with the microcontroller in CDC virtual com port mode.\n\n- stream decoding\n- stream recording\n- device configuration (writing and reading to/from device)\n\nExample\n=======\n\n```bash\n+----------------------------------------------------------------------------------------------------------------------------+\n| $ ./3dpaccel.py  set --range G16 |                                                                                         |\n| $ ./3dpaccel.py  get --all       |                                                                                         |\n| INFO:root:odr=ODR3200            |                                                                                         |\n| INFO:root:scale=FULL_RES_4MG_LSB |                                                                                         |\n| INFO:root:range=G16              |                                                                                         |\n|                                  | $ ./3dpaccel.py decode -                                                                |\n| $ ./3dpaccel.py stream --start 7 |                                                                                         |\n|                                  | INFO:root:decode stream to stdout                                                       |\n|                                  | INFO:root:Sampling Started maxSamples=7                                                 |\n|                                  | INFO:root:#run #sample x[mg] y[mg] z[mg]                                                |\n|                                  | INFO:root:00 00000 -0405.600 +0210.600 -1006.200                                        |\n|                                  | INFO:root:00 00001 -0405.600 +0210.600 -1029.600                                        |\n|                                  | INFO:root:00 00002 -0397.800 +0218.400 -1021.800                                        |\n|                                  | INFO:root:00 00003 -0405.600 +0210.600 -1014.000                                        |\n|                                  | INFO:root:00 00004 -0397.800 +0187.200 -1014.000                                        |\n|                                  | INFO:root:00 00005 -0390.000 +0226.200 -1021.800```                                     |\n|                                  | INFO:root:00 00006 -0390.000 +0210.600 -1021.800- WIP: many features not working yet    |\n|                                  | INFO:root:Sampling Finished at sample 7                                                 |\n|                                  | INFO:root:Device Setup: {'rate': 'ODR3200', 'range': 'G4', 'scale': 'FULL_RES_4MG_LSB'} |\n|                                  | INFO:root:Sampling Stopped                                                              |\n|                                  | INFO:root:run 00: processed 7 samples in 0.010278 s (3158.1 samples/s; 227383.7 baud)   |\n+----------------------------------------------------------------------------------------------------------------------------+\n```\n\nGetting Started\n===============\n\n### Create Environment\n\n```bash\nsudo apt install python3-poetry\n# alternatively apply script from install.python-poetry.org as \n# described in https://github.com/python-poetry/poetry#documentation\ncd host-api/python\npoetry shell\n\n# minimal installation to run controller_cli.py\npoetry install\n\n# for datavis.py, record_step.py and record_step_series.py  \npoetry install --all-extras\n\n# for development (full installation)\npoetry install --all-extras --with dev --with doc\n\n# list discovered devices\ncontroller_cli.py device --list\n\n# retrieve device settings\ncontroller_cli.py get --all\n```\n\n### With Initialized Environment\n\n```bash\ncd host-api/python\npoetry shell\n\n# list discovered devices\ncontroller_cli.py device --list\n```\n\n**Read the Docs** at [3dp-accelerometer.github.io](https://3dp-accelerometer.github.io/py3dpaxxel)\n",
    'author': 'Raoul Rubien',
    'author_email': 'rubienr@sbox.tugraz.at',
    'maintainer': 'Raoul Rubien',
    'maintainer_email': 'rubienr@sbox.tugraz.at',
    'url': 'https://github.com/3dp-accelerometer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<3.13',
}
from py3dpaxxel.scripts.update_setup import *
build(setup_kwargs)

setup(**setup_kwargs)
