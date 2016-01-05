# term-cube
Term-cube can simulate a cubic twistypuzzles with arbitrary side lengths 
and implements a cube timer in terminal. The cube simulator has a lot of
the same functionality as PyCuber <https://github.com/adrianliaw/PyCuber>
in that it can simulate a 3x3x3 and can reverse an algorithm. The timer
has a Two-Phase Algorithm solver, random state scrambling for 3x3x3, an 
interactive mode, a timer, and works with cubes of any side length > 1. 

It uses random-state scrambles for the 3x3x3 by default. Solves and 
scrambles no longer take a godawful amount of time thanks to threading,
but beware of CPU usage. When using the timer, scrambles are generated 
in the background, making them available almost immediately after 
initialization. On slower computers, this might not be the case, 
but they can be disabled at startup, fixing the lag and the CPU usage.

##Demonstration
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

##turn.py
This module has two classes, Turn and TurnSequence. A Turn represents a 
single move that can be used to manipulate a cube with any arbitrary 
side length > 1. A TurnSequence is a list object that specifically holds 
Turn objects and can produce their own inverses, i.e., a given TurnSequence 
A can return a TurnSequence B that undoes A. They can also produce
random turn scrambles.

##cube.py
This module has one class, Cube, which takes a given side length > 1 and
simulates a cube. It can apply an arbitrary Turn object to itself (as 
long as its depth is less than its side length). It implements __str__()
that uses ANSI color codes to represent colors. Orange is represented by
purple here because there is no orange ANSI color code.

The interact method works repl style. You can input a given sequence of 
cube notation (WCA or SiGN will both work equally) and it will be 
applied to the cube and print itself. Try it, it's very fun.

##term-usr.py
This module is a timer. By default it generates random 3x3x3 scrambles,
prints what a cube would look like after applying the scramble, counts 
down inspection until stopped, then counts up until stopped, and repeats
until stopped. Once stopped, it prints the average.

##web-usr.py
This module puts random cubes on a webpage on localhost:8000 using 
visualcube. <http://cube.crider.co.uk/visualcube.php>

##solve.py
This module has one real function which solves a cube from a given 
sticker string using muodov's implementation of kociemba's two phase 
algorithm. Description of the cube string and source for muodov's python
port of two-phase can be found at <https://github.com/muodov/kociemba>.

##scramble.py
This module is adapted from muodov's solve.py. It generates a cube in a
randomly assembled but solvable state, solves it with Kociemba's
algorithm, then returns the inverse of the solution. 

If anyone has any suggestions for speeding up the solver I would be
very happy to know.
