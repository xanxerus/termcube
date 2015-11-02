# term-cube
Not the best documented thing in the world I know. The name leaves much to be desired as well.

This repo is for a project I did for a few days in my free time. 

Term-cube can simulate a cubic twistypuzzle with any given side length greater than 1 and also implements a cube
timer in terminal. It has a lot of the same functionality as PyCuber <https://github.com/adrianliaw/PyCuber>
in that it can simulate a 3x3x3 and can reverse an algorithm. It lacks a solver and the ability to reflect an 
algorithm, but has an interactive mode, a timer, and works with cubes of any side length > 1.

##Demonstration
```python
>>> from cube import Cube
>>> r = Cube(4)
>>> r.interact()
4x4x4 Cube
```
![solved cube image](http://i.imgur.com/3NVC1c6.png)

```
R L f2 Bw2
4x4x4 Cube
```
![moved cube image](http://i.imgur.com/LcZ0cLY.png)

```
scramble
2Uw R D 2Rw2 2Fw2 R F R' 2Fw2 R2 2Bw' U 2Rw D' L' 2Uw' 2Rw 2Dw2 2Fw2 2Rw 2Dw2 F 2Dw 2Lw' U2 L' 2Fw2 2Rw2 2Fw2 2Dw2 2Lw 2Dw B2 L2 U' 2Lw 2Uw2 2Fw 2Dw2 R2
4x4x4 Cube
```
![scrambled cube image](http://i.imgur.com/IWLjDhg.png)

##turn.py
This module has two classes, Turn and TurnSequence. A Turn represents a single move that can be used to manipulate
a cube with any arbitrary side length > 1. A TurnSequence is a list object that specifically holds Turn objects and
can produce the inverse of itself, i.e., a given TurnSequence A can return a TurnSequence B that undoes A.

##cube.py
This module has one class, Cube, which takes a given side length > 1 and simulates a cube. It can apply an arbitrary
Turn object to itself (as long as its depth is less than its side length). It implements __str__() that uses ANSI
color codes to represent colors. Orange is represented by purple here because there is no orange ANSI color code.

The interact method works repl style. You can input a given sequence of cube notation (WCA or SiGN will both work
equally) and it will be applied to the cube and print itself. Try it, it's very fun.

##term-usr.py
This module is a timer. By default it generates random 3x3x3 scrambles, prints what a cube would look like after
applying the scramble, counts down inspection until stopped, then counts up until stopped, and repeats until stopped.
Once stopped, it prints the average.

##web-usr.py
This module puts random cubes on a webpage on localhost:8000 using visualcube 
<http://cube.crider.co.uk/visualcube.php>
