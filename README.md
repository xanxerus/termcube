# Term Cube
Term Cube is a cube timer and simulator that can simulate the Skewb and
cubic twistypuzzles with arbitrary side lengths > 0.

The cube simulator has a lot of the same functionality as PyCuber 
<https://github.com/adrianliaw/PyCuber> in that it can simulate a 3x3x3 
and can reverse an algorithm. but it can also simulate cubes of other
dimensions and the Skewb. 

The timer has random state scrambling for 3x3x3 and Skewb, solve tagging
for statistics, and works with any puzzle it can simulate.

It uses random-state scrambles for the 3x3x3 and Skewb by default. This
will sometimes cause the timer to lag in initialization, but should not
have many issues in normal use beyond that besides CPU usage. On slower
computers, this might be an issue, so random state can be disabled at
startup using the -u flag.

##Optional Setup
This module uses `setuptools` to hopefully make things easier. 

Recommended workflow:

1. Set up a virtualenv (protip: use `virtualenvwrapper`)
1. Activate said virtualenv
1. Navigate to the top of this repo
1. Assuming you already have `setuptools` installed, run `python setup.py develop`.

This will create symlinks from this repo to a python package, such that other 
programs can use the `termcube` module. This procedure also utilizes the entrypoint 
feature of `setuptools`, creating a global script `termcube` with various features.

##Usage
For basic usage, run termcube.py in python3. The script takes care of the rest!

--help will explain how to use command line arguments to skip the beginning prompts.

##termcube.py
This script is the only script that can and should be executed. Others
should only be imported from or run interactively.

It contains the front end to all other scripts, i.e., run this script to
access the timer, simulator, or any demonstrations.

Here is the help text:

Term Cube: Timer and Simulator
usage: termcube [-h] [--inspection INSPECTION] [--unofficial [UNOFFICIAL]]
                [--using-tags]
                [behaviour] [dimension]

positional arguments:
  behaviour             timer, simulator, demo-kociemba, random-turns
  dimension             Cube side length (default 3)

optional arguments:
  -h, --help            show this help message and exit
  --inspection INSPECTION, -i INSPECTION
                        The number of seconds to inspect (default 15)
  --unofficial [UNOFFICIAL], -u [UNOFFICIAL]
                        Use a low CPU alternative to official style scrambles
  --using-tags, -t      Apply tags after each solve to sort

possible behaviours:
timer           - cube timer
simulator       - simulate a cube of amy side length > 0
demo-kociemba   - random-state scramble then solve a cube with  
                  Kociemba's two-phase algorithm, turn by turn
random-turns    - Start from solved, then apply random turns until solved
