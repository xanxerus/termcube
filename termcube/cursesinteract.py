import curses, sys
from .cube import Cube 
from .turn import Turn

class Simulator:
    def __init__(self, cube_size = 3):
        self.cube = Cube(cube_size)
    
    
    def __call__(self, scr):
        self.initialize(scr)
        m = ''
        while m != chr(27):
            self.printcube(scr)
            m = chr(scr.getch())
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

    def printcube(self, scr):
        maxy, maxx = scr.getmaxyx()
        assert not (maxx < 3*self.cube.x or maxy < 3*self.cube.x)
        scr.clear()
        scr.addstr(0, 0, str(self.cube.x))
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
    curses.wrapper(Simulator(cube_size))
