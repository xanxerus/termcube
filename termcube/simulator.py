#!/usr/bin/env python3
from sys import exit
from .cube import Cube
from .turn import Turn, TurnSequence
from time import sleep

try:
    import curses
    nocurses = False
except:
    nocurses = True

class Simulator(Cube):
    help_text = \
"""Term Cube Simulator (Curses implementation)

Manipulate a virtual cube using cube notation!

Press F, R, U, L, D, B, M, E, S, X, Y, or Z to turn the cube.
Hold shift and press to do the reverse of that turn.

Press : to initiate a command or type a longer string of notation.

Available commands:
:reset      - Reset the cube to a solved position
:solve      - Display a two-phase solution
:sexy       - Apply the sexy move (R U R' U')
:scramble   - Print a scramble and apply it
:exit       - Exit interactive mode (change cube)
:help       - Access this help text"""
    
    def __init__(self, size = 3):
        super(Simulator, self).__init__(size)

    def __call__(self, scr, nocurses):
        self.initialize(scr)

        if nocurses:
            self.interact()
            return

        m = ''
        while m != chr(27):
            self.printcube(scr)
            m = chr(scr.getch())

            if m in ':1234567890':
                scr.addstr(0, 0, m)
                self.command(scr, m + self.getln(scr).strip())
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
                    self.apply(t)

    def command(self, scr, command):
        if command == ':reset':
            self.reset()
        elif command == ':solve':
            q = self.two_phase_solution()
            scr.addstr(0, 0, str(q[0]))
            scr.addstr(1, 0, 'Solve time: %.2f seconds' % q[1])
            scr.addstr(2, 0, 'Apply this solution? (y/n): ')
            if chr(scr.getch()) == 'y':
                scr.nodelay(1)
                for t in TurnSequence(q[0]):
                    self.apply_turn(t)
                    self.printcube(scr)
                    curses.napms(100)
                    scr.getch()
                scr.nodelay(0)
        elif command == ':sexy':
            self.apply("R U R' U'")
        elif command == ':scramble':
            scr.addstr(0, 0, str(self.scramble()))
        elif command == ':exit':
            exit(0)
        elif command == ':help':
            Simulator.cornerandwait(scr, self.helptext)
        else:
            try:
                self.apply(TurnSequence(command))
            except:
                scr.addstr(0, 0, 'Invalid move: %s' % command)

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

    def printcube(self, scr):
        maxy, maxx = scr.getmaxyx()
        assert not (maxx <= 3*self.size or maxy <= 3*self.size)

        scr.clear()
        xinit = (maxx - 6*self.size) // 2 - 1
        y = (maxy - 3*self.size) // 2 - 1

        for r in self.faces['U']:
            x = xinit + self.size*2
            for c in r:
                scr.addstr(y, x, '  ', curses.color_pair(ord(c) - 60))
                x += 2
            y += 1

        for r in range(self.size):
            x = xinit
            for c in self.faces['L'][r]:
                scr.addstr(y, x, '  ', curses.color_pair(ord(c) - 60))
                x += 2
            for c in self.faces['F'][r]:
                scr.addstr(y, x, '  ', curses.color_pair(ord(c) - 60))
                x += 2
            for c in self.faces['R'][r]:
                scr.addstr(y, x, '  ', curses.color_pair(ord(c) - 60))
                x += 2
            y += 1

        for r in self.faces['D'] + self.faces['B']:
            x = xinit + self.size*2
            for c in r:
                scr.addstr(y, x, '  ', curses.color_pair(ord(c) - 60))
                x += 2
            y += 1
        scr.move(maxy-1, maxx-1)

def simulate(size = 3, nocurses = False):
    curses.wrapper(Simulator(size), nocurses)
