# Term Cube
Term Cube is a cube timer and simulator which can simulate cubic 
twistypuzzles with arbitrary side lengths. The cube simulator has a lot of
the same functionality as PyCuber <https://github.com/adrianliaw/PyCuber>
in that it can simulate a 3x3x3 and can reverse an algorithm. The timer
has a Two-Phase Algorithm solver, random state scrambling for 3x3x3, 
solve tagging for statistics, and works with cubes of any side length > 1. 

It uses random-state scrambles for the 3x3x3 by default. Solves and 
scrambles no longer take a godawful amount of time thanks to threading,
but beware of CPU usage. When using the timer, scrambles are generated 
in the background, making them available almost immediately after 
initialization. On slower computers, this might not be the case, 
but they can be disabled at startup, fixing the lag and the CPU usage.

##Simulator Demonstration
```python
>>> from cube import Cube
>>> r = Cube(4)
>>> r.interact()
4x4x4 Cube
```
![solved cube image](http://i.imgur.com/3NVC1c6.png)

```
R L f2 Uw2
4x4x4 Cube
```
![moved cube image](http://i.imgur.com/hboMCIf.png)

```
scramble
2Uw R D 2Rw2 2Fw2 R F R' 2Fw2 R2 2Bw' U 2Rw D' L' 2Uw' 2Rw 2Dw2 2Fw2 2Rw 2Dw2 F 2Dw 2Lw' U2 L' 2Fw2 2Rw2 2Fw2 2Dw2 2Lw 2Dw B2 L2 U' 2Lw 2Uw2 2Fw 2Dw2 R2
4x4x4 Cube
```
![scrambled cube image](http://i.imgur.com/IWLjDhg.png)

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

##turn.py
This module has two classes, Turn and TurnSequence. A Turn represents a 
single move that can be used to manipulate a cube with any arbitrary 
side length > 1. A TurnSequence is a list object that specifically holds 
Turn objects and can produce their own inverses, i.e., a given TurnSequence 
A can return a TurnSequence B that undoes A. They can also produce
random turn scrambles.

##cube.py
This module has two classes: ScrambleGenerator, which generates random state
scrambles in a separate thread and returns them when requested, and
Cube, which simulates a cube of any side length > 1. A Cube can apply an
arbitrary Turn object to itself (as long as its depth is less than its 
side length). It implements a __str__() that uses ANSI color codes to 
represent colors. Orange is represented by purple because there is no 
orange ANSI color code.

The interact method works repl style. You can input a given sequence of 
cube notation (WCA or SiGN will both work equally) and it will be 
applied to the cube and print itself. Try it, it's very fun.

##termusr.py
This module contains timer functions. By default it generates random state
3x3x3 scrambles, prints what a cube would look like after applying the 
scramble, counts down until inspections is stopped, then counts up until
stopped, and repeats until stopped.

It supports rudimentary exports to files, deleting times, adding penalties,
and also tagging a solve at the end of solve time so that each time can 
be sorted by attributes that interest the user.

##solve.py
This module has one real function which solves a cube from a given 
sticker string using muodov's implementation of kociemba's two phase 
algorithm. Description of the cube string and source for muodov's python
port of two-phase can be found at <https://github.com/muodov/kociemba>.

##scramble.py
This module is adapted from muodov's solve.py. It generates a cube in a
randomly assembled but solvable state, solves it with Kociemba's
algorithm, then returns the inverse of the solution.

Description and source for muodov's python port of two-phase can be 
found at <https://github.com/muodov/kociemba>.

Description of Kociemba's two-phase algorithm can be found at 
<http://kociemba.org/cube.htm>

If anyone has any suggestions for speeding up the solver I would be
very happy to know.
