from . import scramble
from . import solve
from .turn import Turn, TurnSequence

from queue import Queue
from sys import stderr
from time import sleep, time
from threading import Thread

help_text = \
"""Term Cube Simulator Interactive Mode

Manipulate a virtual cube using cube notation

Available commands:
-reset      - Reset the cube to a solved position
-solve      - Display a two-phase solution
-sexy       - Apply the sexy move (R U R' U')
-scramble   - Print a scramble apply it
-exit       - Exit interactive mode (change cube)
-help       - Access this help text"""

def rotate_cw(face):
    """Returns a clockwise rotated version of a given 2D list"""
    return [list(a) for a in zip(*face[::-1])]

def rotate_ccw(face):
    """Returns a counterclockwise rotated version of a given 2D list"""
    return [list(a) for a in zip(*face)][::-1]

def rotate_2(face):
    """Returns a 180 degree rotated version of a given 2D list"""
    return [a[::-1] for a in face[::-1]]


class Cube:
    """Represent a Cube with a given side length.
    Support turning of faces using Turn objects.
    Allow visualization using ANSI color codes in terminal or
    using the visualcube API.
    """
    sticker = {'F': '\033[47m  \033[0m',
               'R': '\033[41m  \033[0m',
               'U': '\033[44m  \033[0m',
               'D': '\033[42m  \033[0m',
               'L': '\033[45m  \033[0m',
               'B': '\033[43m  \033[0m'}

    color =   {'F': 'w',
               'R': 'r',
               'U': 'b',
               'D': 'g',
               'L': 'o',
               'B': 'y'}

    def __init__(self, size = 3):
        """Initialize a Cube with a given dimension in a solved state."""
        self.size = size
        self.reset()

    def reset(self):
        """Initialize all sides to unique solid colors."""
        self.faces = dict()

        for face in 'FRULDB':
            self.faces[face] = [[face]*self.size for q in range(self.size)]

    def scramble(self, random = True, moves = -1):
        """Generate, apply, and return a scramble."""
        s = self.get_scramble(random, moves)
        self.apply(s)
        return s

    def get_scramble(self, random = True, moves = -1):
        """Generate and return a scramble without applying."""
        if random and self.size == 3:
            return scramble.scramble()
        elif moves is not None and moves > 1:
            return TurnSequence.get_scramble(self.size, moves)
        else:
            return TurnSequence.get_scramble(self.size)

    def apply(self, sequence):
        """Apply a given TurnSequence to this Cube. If a str was given,
        convert to TurnSequence then apply.
        """
        for turn in TurnSequence(sequence):
            self.apply_turn(turn)
        return self

    def apply_turn(self, turn):
        """Apply a given Turn to this Cube. Does not convert strs."""
        for w in range(Turn.directions.index(turn.direction)+1):
            if turn.move == 'x':
                self.faces['F'], self.faces['U'], self.faces['B'], self.faces['D'] = \
                self.faces['D'], self.faces['F'], self.faces['U'], self.faces['B']
                self.faces['R'] = rotate_cw(self.faces['R'])
                self.faces['L'] = rotate_ccw(self.faces['L'])
            elif turn.move == 'y':
                self.faces['F'], self.faces['L'], self.faces['B'], self.faces['R'] = \
                self.faces['R'], self.faces['F'], rotate_2(self.faces['L']), rotate_2(self.faces['B'])
                self.faces['U'] = rotate_cw(self.faces['U'])
                self.faces['D'] = rotate_ccw(self.faces['D'])
            elif turn.move == 'z':
                self.faces['U'], self.faces['R'], self.faces['D'], self.faces['L'] = \
                map(rotate_cw, [self.faces['L'], self.faces['U'], self.faces['R'], self.faces['D']])
                self.faces['F'] = rotate_cw(self.faces['F'])
                self.faces['B'] = rotate_ccw(self.faces['B'])
            elif turn.move == 'M':
                self.apply("x' R L'")
            elif turn.move == 'E':
                self.apply("y' U D'")
            elif turn.move == 'S':
                self.apply("z B F'")

            if turn.move in Turn.faces:
                self.faces[turn.move] = rotate_cw(self.faces[turn.move])
                for g in range(1, turn.depth+1):
                    for q in range(self.size):
                        if turn.move == 'F':
                            (self.faces['D'][g-1][q],
                            self.faces['R'][-q-1][g-1],
                            self.faces['U'][self.size-g][-q-1],
                            self.faces['L'][q][self.size-g]) = \
                            (self.faces['R'][-q-1][g-1],
                            self.faces['U'][self.size-g][-q-1],
                            self.faces['L'][q][self.size-g],
                            self.faces['D'][g-1][q])
                        elif turn.move == 'U':
                            (self.faces['F'][g-1][q],
                            self.faces['R'][g-1][q],
                            self.faces['B'][self.size-g][-q-1],
                            self.faces['L'][g-1][q]) = \
                            (self.faces['R'][g-1][q],
                            self.faces['B'][self.size-g][-q-1],
                            self.faces['L'][g-1][q],
                            self.faces['F'][g-1][q])
                        elif turn.move == 'D':
                            (self.faces['B'][g-1][-q-1],
                            self.faces['R'][self.size-g][q],
                            self.faces['F'][self.size-g][q],
                            self.faces['L'][self.size-g][q]) = \
                            (self.faces['R'][self.size-g][q],
                            self.faces['F'][self.size-g][q],
                            self.faces['L'][self.size-g][q],
                            self.faces['B'][g-1][-q-1])
                        elif turn.move == 'B':
                            (self.faces['L'][q][g-1],
                            self.faces['U'][g-1][-q-1],
                            self.faces['R'][-q-1][self.size-g],
                            self.faces['D'][self.size-g][q]) = \
                            (self.faces['U'][g-1][-q-1],
                            self.faces['R'][-q-1][self.size-g],
                            self.faces['D'][self.size-g][q],
                            self.faces['L'][q][g-1])
                        elif turn.move == 'L':
                            (self.faces['B'][q][g-1],
                            self.faces['D'][q][g-1],
                            self.faces['F'][q][g-1],
                            self.faces['U'][q][g-1]) = \
                            (self.faces['D'][q][g-1],
                            self.faces['F'][q][g-1],
                            self.faces['U'][q][g-1],
                            self.faces['B'][q][g-1])
                        elif turn.move == 'R':
                            (self.faces['B'][q][self.size-g],
                            self.faces['U'][q][self.size-g],
                            self.faces['F'][q][self.size-g],
                            self.faces['D'][q][self.size-g]) = \
                            (self.faces['U'][q][self.size-g],
                            self.faces['F'][q][self.size-g],
                            self.faces['D'][q][self.size-g],
                            self.faces['B'][q][self.size-g])
        return self

    def __eq__(self, other):
        """Return true if all stickers match."""
        return self.faces == other.faces

    def __str__(self):
        """Return the type of cube and an ANSI color representation."""
        ret = ''
        for r in self.faces['U']:
            ret += '  '*self.size
            for c in r:
                ret += Cube.sticker[c]
            ret += '\n'

        for r in range(self.size):
            for c in self.faces['L'][r]:
                ret += Cube.sticker[c]
            for c in range(self.size):
                ret += Cube.sticker[self.faces['F'][r][c]]
            for c in self.faces['R'][r]:
                ret += Cube.sticker[c]
            ret += '\n'

        for r in self.faces['D'] + self.faces['B']:
            ret += '  '*self.size
            for c in r:
                ret += Cube.sticker[c]
            ret += '\n'

        return ret

    def kociemba_str(self):
        """Return this cube in kociemba-friendly sticker format."""
        ret  = ''.join(''.join(arr) for arr in self.faces['U'])
        ret += ''.join(''.join(arr) for arr in self.faces['R'])
        ret += ''.join(''.join(arr) for arr in self.faces['F'])
        ret += ''.join(''.join(arr) for arr in self.faces['D'])
        ret += ''.join(''.join(arr) for arr in self.faces['L'])
        ret += ''.join(''.join(arr) for arr in rotate_2(self.faces['B']))

        q = dict()
        for s in 'FRULDB':
            q[self.color[self.faces[s][1][1]]] = s

        return list(q[Cube.color[s]] for s in ret)

    def two_phase_solution(self):
        """Find a solution using Kociemba's two phase algoithm."""
        try:
            assert self.size == 3
        except:
            print('Cube must be a 3x3x3 to find a two phase solution', file=stderr)
        return solve.solve(self.kociemba_str())

    def __repr__(self):
        """Return an ANSI color representation of the cube."""
        return str(self)

    def is_solved(self):
        """Return true if all faces are a solid color."""
        for f in Turn.faces:
            w = self.faces[f][0][0]
            for r in self.faces[f]:
                if not all(map(lambda arg: arg == w, r)):
                    return False
        return True

    def visualize(self):
        """Return the visualcube URL for a gif of this cube."""
        facelet_colors = ''
        for q in 'URFDL':
            for r in self.faces[q]:
                for c in r:
                    facelet_colors += Cube.color[c]

        for r in rotate_2(self.faces['B']):
            for c in r:
                facelet_colors += Cube.color[c]

        return 'http://cube.crider.co.uk/visualcube.php?fmt=gif&pzl=%s&fc=%s' % (self.size, facelet_colors)

    def interact(self):
        """Read, evaluate, print, and loop commands. See help text."""
        while True:
            print(self)
            print()
            usr = input().strip()
            if usr == 'reset':
                self.reset()
            elif usr == 'solve':
                q = self.two_phase_solution()
                print(q[0])
                print('Solve time: %.2f seconds' % q[1])
                print('Apply this solution?')
                if input().startswith('y'):
                    for t in TurnSequence(q[0]):
                        self.apply(t)
                        print(self)
                        sleep(.1)
            elif usr == 'sexy':
                self.apply("R U R' U'")
            elif usr == 'scramble':
                print(self.scramble())
            elif usr == 'exit':
                break
            elif usr == 'help':
                print(help_text)
            else:
                try:
                    self.apply(TurnSequence(usr))
                except:
                    print('Invalid move: %s' % usr)

class ScrambleGenerator():
    def __init__(self, size = 3, random = True, length = -1, capacity = 10):
        self.cube = Cube(size)
        self.queue = Queue(max((capacity, 0)))
        self.random = random
        self.length = length
        self.thread = Thread(target=self.enqueue_scramble)
        self.stopped = False
        self.thread.start()

    def enqueue_scramble(self):
        """Fill a given Queue with scramble until it is either full or a given capacity has been reached"""
        while not self.stopped:
            if not self.queue.full():
                self.queue.put(self.cube.get_scramble(self.random, self.length))

    def __next__(self):
        """Remove and return the next scramble in the queue"""
        return self.queue.get()

    def __enter__(self):
        """Start the scramble generating thread"""
        if self.stopped:
            self.stopped = False
            self.thread.start()
        return self

    def __exit__(self, type = None, value = None, traceback = None):
        """Stop the scramble generating thread"""
        if not self.stopped:
            self.stopped = True
            self.thread.join()

    def __iter__(self):
        """Make this generator iterable by return itself"""
        return self

    start, stop = __enter__, __exit__


def demo_random_turns(n = 3):
    from time import sleep
    r = Cube(n)
    while True:
        s = Turn.random_turn(n)
        r.apply_turn(s)
        print(s)
        print(r)
        sleep(.5)
        if r.is_solved():
            break
    print('WOAH')

def demo_kociemba():
    print('Initializing...')
    r = Cube(3)
    with ScrambleGenerator() as scrambler:
        while True:
            r.apply(next(scrambler))
            print(r)
            for t in TurnSequence(r.two_phase_solution()[0]):
                r.apply(t)
                print(r)
                sleep(.1)
            sleep(1)
