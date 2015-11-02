# cube
Not the best documented thing in the world I know. The name leaves much to be desired as well.

This repo is for a project I did for a few days in my free time. 

This project can simulate a cubic twistypuzzle with any given side length greater than 1 and also implements a cube
timer in terminal.

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
