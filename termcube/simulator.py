#!/usr/bin/env python3
from sys import exit
from . import TurnSequence
from .cube import Cube
from .skewb import Skewb
from time import sleep
import re

try:
    import curses
    nocurses = False
except:
    nocurses = True

class Simulator():
    help_text = \
"""Term Cube Simulator (Curses implementation)

Manipulate a virtual cube using cube notation!

Press a letter key the corresponding turn.
Hold shift and press to do the reverse of that turn.
Start with a number to start deep-layered turns

Press : to initiate a command or type a longer string of notation.

Available commands:
:reset      - Reset the cube to a solved position
:solve      - Display a two-phase solution
:sexy       - Apply the sexy move (R U R' U')
:scramble   - Print a scramble and apply it
:exit       - Exit interactive mode (change cube)
:help       - Access this help text"""
    
    def __init__(self, puzzle = None):
        self.puzzle = puzzle if puzzle else Cube(3)
        self.turn = self.puzzle.turn_type

    def __call__(self, scr, nocurses):
        self.initialize(scr)

        if nocurses:
            self.puzzle.interact()
            return

        m = ''
        while m != chr(27):
            self.printpuzzle(scr)
            m = chr(scr.getch())

            if m in ':1234567890':
                scr.addstr(0, 0, m)
                self.command(scr, m + self.getln(scr).strip())
            else:
                u = m.upper()
                l = m.lower()

                if u in self.turn.moves or l in self.turn.moves:
                    if u in self.turn.moves:
                        t = self.turn(u)
                    else:
                        t = self.turn(l)
                    if m == u:
                        t = t.inverse()
                    self.puzzle.apply(t)

    def command(self, scr, command):
        if command == ':reset':
            self.puzzle.reset()
        elif command == ':solve':
            if hasattr(self.puzzle, 'solution'):
                q = self.puzzle.solution()
                scr.addstr(0, 0, str(q[0]))
                scr.addstr(1, 0, 'Solve time: %.2f seconds' % q[1])
                scr.addstr(2, 0, 'Apply this solution? (y/n): ')
                if chr(scr.getch()) == 'y':
                    scr.nodelay(1)
                    for t in TurnSequence(q[0]):
                        self.puzzle.apply_turn(t)
                        self.printpuzzle(scr)
                        curses.napms(100)
                        scr.getch()
                    scr.nodelay(0)
            else:
                addcenter(scr, 'This puzzle has no solver as of yet')
                scr.nodelay(1)
                scr.getch()
                scr.nodelay(0)
        elif command == ':scramble':
            scr.addstr(0, 0, str(self.puzzle.scramble()))
        elif command == ':exit':
            exit(0)
        elif command == ':help':
            Simulator.cornerandwait(scr, Simulator.help_text)
        else:
            try:
                self.puzzle.apply(TurnSequence(command[1:], self.puzzle.turn_type))
            except Exception as e:
                scr.addstr(0, 0, '%s -- %s' % (e, command[1:]))
                scr.refresh()
                scr.getch()

    @staticmethod
    def cornerandwait(scr, msg):
        scr.clear()
        try:
            scr.addstr(0, 0, msg)
        except:
            pass
        while scr.getch() == curses.KEY_RESIZE:
            pass

    def initialize(self, scr):
        self.scr = scr
        if not curses.has_colors():
            global nocurses
            nocurses = True
            return

        curses.init_pair(ord('F') - 60, curses.COLOR_WHITE, curses.COLOR_WHITE)
        curses.init_pair(ord('R') - 60, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(ord('U') - 60, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(ord('L') - 60, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
        curses.init_pair(ord('D') - 60, curses.COLOR_WHITE, curses.COLOR_GREEN)
        curses.init_pair(ord('B') - 60, curses.COLOR_WHITE, curses.COLOR_YELLOW)
        scr.leaveok(0)
        curses.noecho()

        try:
            curses.curs_set(0)
        except:
            pass

    @staticmethod
    def getln(scr, delimiter = '\n'):
        try:
            curses.curs_set(2)
        except:
            pass

        curses.echo()

        if hasattr(delimiter, '__call__'):
            exitcondition = delimiter
        elif isinstance(delimiter, str):
            exitcondition = lambda c: c == delimiter
        else:
            exitcondition = lambda c: c == chr(delimiter)

        ret = ''
        while True:
            c = chr(scr.getch())
            if exitcondition(c):
                break
            elif c == chr(curses.KEY_BACKSPACE):
                ret = ret[:-1]
            else:
                ret += c

        try:
            curses.curs_set(0)
        except:
            pass
        curses.noecho()

        return ret

    def printpuzzle(self, scr):
        maxy, maxx = scr.getmaxyx()
        scr.clear()
        y = (maxy - 3*self.puzzle.size) // 2 - 1
        xinit = (maxx - 6*self.puzzle.size) // 2 - 1
        
        for line in self.puzzle.simulatorstr().split('\n'):
            x = xinit
            for c in line:
                if c != ' ':
                    scr.addstr(y, x, ' ', curses.color_pair(ord(c) - 60))
                x += 1
            y += 1
        
        scr.move(maxy-1, maxx-1)

def addcenter(scr, msg, starty = None, startx = None, clear = True):
    if clear:
        scr.clear()
    maxy, maxx = scr.getmaxyx()
    msg = str(msg)
    if maxy > 1:
        scr.addstr(maxy//2 - 1 if starty is None else starty, (maxx - len(msg))//2 if startx is None else startx, msg)
    else:
        scr.addstr(maxy//2 if starty is None else starty, (maxx - len(msg))//2 if startx is None else startx, msg)
    if clear:
        scr.refresh()

def simulate(size = 3, nocurses = False):
    curses.wrapper(Simulator(size), nocurses)
