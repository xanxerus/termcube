#!/usr/bin/env python3
import sys
from .cube import Cube 
from .turn import Turn, TurnSequence
from time import sleep

try:
    import curses
    noncurses = False
except:
    noncurses = True

help_text = \
"""Term Cube Simulator (Curses implementation)

Manipulate a virtual cube using cube notation!

Press F, R, U, L, D, B, M, E, S, X, Y, or Z to turn the cube.
Hold shift and press to do the reverse of that turn.

Press : to initiate a command or type a longer string of notation.

Available commands:
-reset      - Reset the cube to a solved position
-solve      - Display a two-phase solution
-sexy       - Apply the sexy move (R U R' U')
-scramble   - Print a scramble and apply it
-exit       - Exit interactive mode (change cube)
-help       - Access this help text"""

class Simulator:
    def __init__(self, cube_size = 3):
        self.cube = Cube(cube_size)
    
    def __call__(self, scr):
        self.initialize(scr)
        m = ''
        while m != chr(27):
            self.printcube(scr)
            m = chr(scr.getch())
            
            if m == ':':
                scr.addstr(0, 0, ':')
                self.command(scr, self.getln(scr).strip())
            else:
                u = m.upper()
                l = m.lower()
                
                if u in Turn.moves or l in Turn.moves:
                    if u in Turn.moves:
                        t = Turn(u)
                    else:
                        t = Turn(l)
                    if m == u:
                        t = t.inverse()
                    self.cube.apply(t)

    def command(self, scr, command):
        if command == 'reset':
            self.cube.reset()
        elif command == 'solve':
            q = self.cube.two_phase_solution()
            scr.addstr(0, 0, str(q[0]))
            scr.addstr(1, 0, 'Solve time: %.2f seconds' % q[1])
            scr.addstr(2, 0, 'Apply this solution? (y/n): ')
            if chr(scr.getch()) == 'y':
                scr.nodelay(1)
                for t in TurnSequence(q[0]):
                    self.cube.apply_turn(t)
                    self.printcube(scr)
                    curses.napms(100)
                    scr.getch()
                scr.nodelay(0)
        elif command == 'sexy':
            self.cube.apply("R U R' U'")
        elif command == 'scramble':
            scr.addstr(0, 0, str(self.cube.scramble()))
        elif command == 'solved?':
            scr.addstr(0, 0, str(self.cube.is_solved()))
        elif command == 'exit':
            self.exit()
        elif command == 'help':
            self.help(scr)
        else:
            try:
                self.cube.apply(TurnSequence(command))
            except:
                scr.addstr(0, 0, 'Invalid move: %s' % command)
    
    def exit(self):
        raise Exception()
    
    def help(self, scr):
        scr.clear()
        try:
            scr.addstr(0, 0, help_text)
        except:
            pass
        while scr.getch() == curses.KEY_RESIZE:
            pass

    def initialize(self, scr):
        if not curses.has_colors():
            print('Terminal cannot display color. So sad. Exiting.', file=sys.stderr)
            sys.exit(1)
        
        curses.init_pair(ord('F')-60, curses.COLOR_CYAN, curses.COLOR_WHITE)
        curses.init_pair(ord('R')-60, curses.COLOR_CYAN, curses.COLOR_RED)
        curses.init_pair(ord('U')-60, curses.COLOR_CYAN, curses.COLOR_BLUE)
        curses.init_pair(ord('L')-60, curses.COLOR_CYAN, curses.COLOR_MAGENTA)
        curses.init_pair(ord('D')-60, curses.COLOR_CYAN, curses.COLOR_GREEN)
        curses.init_pair(ord('B')-60, curses.COLOR_CYAN, curses.COLOR_YELLOW)
        scr.leaveok(0)
        curses.curs_set(0)

    def getln(self, scr, delimiter='\n'):
        try:
            curses.curs_set(2)
        except:
            pass
        
        delimiter = delimiter if isinstance(delimiter, str) else chr(delimiter)
        curses.echo()
        
        ret = ''
        while True:
            c = chr(scr.getch())
            if c == delimiter:
                break
            elif c == chr(curses.KEY_BACKSPACE):
                ret = ret[:-1]
            else:
                ret += c
        
        try:
            curses.curs_set(0)
        except:
            pass
        
        return str(ret)

    def printcube(self, scr):
        maxy, maxx = scr.getmaxyx()
        assert not (maxx < 3*self.cube.x or maxy < 3*self.cube.x)
        scr.clear()
        xinit = (maxx - 6*self.cube.x) // 2 - 1
        y = (maxy - 3*self.cube.x) // 2 - 1
        
        for r in self.cube.faces['U']:
            x = xinit + self.cube.x*2
            for c in r:
                scr.addstr(y, x, '  ', curses.color_pair(ord(c)-60))
                x += 2
            y += 1
        
        for r in range(self.cube.x):
            x = xinit
            for c in self.cube.faces['L'][r]:
                scr.addstr(y, x, '  ', curses.color_pair(ord(c)-60))
                x += 2
            for c in range(self.cube.x):
                scr.addstr(y, x, '  ', curses.color_pair(ord(self.cube.faces['F'][r][c])-60))
                x += 2
            for c in self.cube.faces['R'][r]:
                scr.addstr(y, x, '  ', curses.color_pair(ord(c)-60))
                x += 2
            y += 1

        for r in self.cube.faces['D'] + self.cube.faces['B']:
            x = xinit + self.cube.x*2
            for c in r:
                scr.addstr(y, x, '  ', curses.color_pair(ord(c)-60))
                x += 2
            y += 1
        scr.move(maxy-1, maxx-1)

def simulate(cube_size = 3):
    if noncurses:
        Cube(cube_size).interact()
    else:
        try:
            curses.wrapper(Simulator(cube_size))
        except:
            pass
