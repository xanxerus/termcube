from .. import TurnSequence
from random import choice

class SkewbTurn():
    faces = ('R', 'U', 'L', 'B')
    axes = ('x', 'y', 'z')
    directions = ('', '2', '\'')
    moves = faces + axes
    lower_faces = [s.lower() for s in faces]

    def __init__(self, move, direction = ''):
        """Initialize a Turn with a given move and direction.
        If a string of notation is given instead of a move,
        initialize the Turn based on the notation.
        """
        if move in SkewbTurn.moves:
            self.move, self.direction = move, direction
        else:
            self.move, self.direction =  move[0], move[1:]
            if self.direction == "2'" or self.direction == "'2":
                self.direction = '2'
            if self.move in SkewbTurn.faces and self.direction == '2':
                self.direction = "'"

    def __eq__(self, other):
        """Return true if the given Turns have the same move,
        direction, and depth.
        """
        return str(self) == str(other)

    def opposite_face(self):
        """If the given turn has an opposite face, return it."""
        if self.move in 'UB':
            return 'UB'.replace(self.move, '')
        return None

    def opposite_direction(self):
        """Return the face opposite direction of this Turn."""
        return SkewbTurn.directions[-SkewbTurn.directions.index(self.direction)-1]

    def inverse(self):
        """Return the Turn that undoes this one."""
        return SkewbTurn(self.move, self.opposite_direction())

    @staticmethod
    def random_turn():
        """Return a Turn with a random face, direction, and depth
        less than or equal to half the given cube dimension.
        """
        return SkewbTurn(choice(SkewbTurn.faces), choice(SkewbTurn.directions))

    def __str__(self):
        """Return this turn using WCA notation."""
        return self.move + self.direction

    def __repr__(self):
        """Return the move and direction of this SkewbTurn clearly
        defined and separated.
        """
        return 'SkewbTurn(move=%s, direction=%s)' % (self.move, self.direction)

class Skewb():
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

    turn_type = SkewbTurn

    def __init__(self):
        """Initialize a Skewb in a solved state."""
        self.reset()
        self.size = 3
        self.default_moves = 25
    
    def reset(self):
        """Initialize all sides to unique solid colors."""
        self.faces = dict()

        for face in 'FRULDB':
            self.faces[face] = [face]*5

    def scramble(self, random = False, moves = 25):
        """Generate, apply, and return a scramble."""
        s = self.get_scramble(random, moves)
        self.apply(s)
        return s

    def get_scramble(self, random = False, moves = None):
        """Generate and return a scramble without applying."""
        if moves is None or moves <= 0:
            moves = self.default_moves

        ret = TurnSequence()

        last = SkewbTurn('R')
        turn = SkewbTurn('R')

        for lcv in range(moves if moves else 25):
            while turn.move == last.move or turn.opposite_face() == last.move:
                turn = SkewbTurn.random_turn()
            last = turn
            ret.append(turn)
        return ret

    def apply(self, sequence):
        """Apply a given TurnSequence to this Skewb. If a str was given,
        convert to TurnSequence then apply.
        """
        for turn in TurnSequence(sequence, SkewbTurn):
            self.apply_turn(turn)
        return self

    def apply_turn(self, turn):
        """Apply a given Turn to this Cube. Does not convert strs."""
        ###Rotations
        for i in range(1 + SkewbTurn.directions.index(turn.direction)):
            if turn.move == 'x':
                self.faces['F'], self.faces['U'], self.faces['B'], self.faces['D'] = \
                self.faces['D'], self.faces['F'], self.faces['U'], self.faces['B']
                self.faces['R'] = Skewb.rotate_cw(self.faces['R'])
                self.faces['L'] = Skewb.rotate_ccw(self.faces['L'])
            elif turn.move == 'y':
                self.faces['F'], self.faces['L'], self.faces['B'], self.faces['R'] = \
                self.faces['R'], self.faces['F'], Skewb.rotate_2(self.faces['L']), Skewb.rotate_2(self.faces['B'])
                self.faces['U'] = Skewb.rotate_cw(self.faces['U'])
                self.faces['D'] = Skewb.rotate_ccw(self.faces['D'])
            elif turn.move == 'z':
                self.faces['U'], self.faces['R'], self.faces['D'], self.faces['L'] = \
                map(Skewb.rotate_cw, [self.faces['L'], self.faces['U'], self.faces['R'], self.faces['D']])
                self.faces['F'] = Skewb.rotate_cw(self.faces['F'])
                self.faces['B'] = Skewb.rotate_ccw(self.faces['B'])

        ###Axis turns
        for i in range(2 if turn.direction else 1):
            if turn.move == 'U':
                (self.faces['U'][0], self.faces['R'][0], self.faces['F'][0],
                self.faces['U'][2], self.faces['R'][3], self.faces['F'][1],
                self.faces['U'][4], self.faces['R'][1], self.faces['F'][2],
                self.faces['U'][3], self.faces['R'][2], self.faces['F'][4]) = \
                    (self.faces['F'][0], self.faces['U'][0], self.faces['R'][0],
                    self.faces['F'][1], self.faces['U'][2], self.faces['R'][3],
                    self.faces['F'][2], self.faces['U'][4], self.faces['R'][1],
                    self.faces['F'][4], self.faces['U'][3], self.faces['R'][2])
            elif turn.move == 'R':
                (self.faces['B'][0], self.faces['D'][0], self.faces['R'][0],
                self.faces['B'][4], self.faces['D'][2], self.faces['R'][2],
                self.faces['B'][1], self.faces['D'][3], self.faces['R'][3],
                self.faces['B'][3], self.faces['D'][4], self.faces['R'][4]) = \
                    (self.faces['R'][0], self.faces['B'][0], self.faces['D'][0],
                    self.faces['R'][2], self.faces['B'][4], self.faces['D'][2],
                    self.faces['R'][3], self.faces['B'][1], self.faces['D'][3],
                    self.faces['R'][4], self.faces['B'][3], self.faces['D'][4])
            elif turn.move == 'L':
                (self.faces['D'][0], self.faces['L'][0], self.faces['F'][0],
                self.faces['D'][2], self.faces['L'][3], self.faces['F'][1],
                self.faces['D'][1], self.faces['L'][4], self.faces['F'][3],
                self.faces['D'][3], self.faces['L'][2], self.faces['F'][4]) = \
                    (self.faces['F'][0], self.faces['D'][0], self.faces['L'][0],
                    self.faces['F'][1], self.faces['D'][2], self.faces['L'][3],
                    self.faces['F'][3], self.faces['D'][1], self.faces['L'][4],
                    self.faces['F'][4], self.faces['D'][3], self.faces['L'][2])
            elif turn.move == 'B':
                (self.faces['L'][0], self.faces['D'][0], self.faces['B'][0],
                self.faces['L'][4], self.faces['D'][4], self.faces['B'][2],
                self.faces['L'][1], self.faces['D'][1], self.faces['B'][3],
                self.faces['L'][3], self.faces['D'][3], self.faces['B'][4]) = \
                    (self.faces['B'][0], self.faces['L'][0], self.faces['D'][0],
                    self.faces['B'][2], self.faces['L'][4], self.faces['D'][4],
                    self.faces['B'][3], self.faces['L'][1], self.faces['D'][1],
                    self.faces['B'][4], self.faces['L'][3], self.faces['D'][3])
    
    def __eq__(self, other):
        """Return true if all stickers match."""
        return self.faces == other.faces
    
    def simulatorstr(self):
        ret = ''
        def halp(* faces):
            for arr in [[1, 0, 2], [0, 0, 0], [3, 0, 4]]:
                ret = ''
                for face in faces:
                    ret += ''.join(face[i]*2 for i in arr)
                yield ret
        
        for line in halp(self.faces['U']):
            ret += '  '*self.size + line + '\n'
        
        for line in halp(self.faces['L'], self.faces['F'], self.faces['R']):
            ret += line + '\n'
        
        for line in halp(self.faces['D']):
            ret += '  '*self.size + line + '\n'

        for line in halp(Skewb.rotate_2(self.faces['B'])):
            ret += '  '*self.size + line + '\n'
        
        return ret
    
    def __str__(self):
        """Return an ANSI color representation of this Skewb.
        A face within the array is defined as:
            102
            000
            304
        where each digit is the sticker's index in its face array.
        """
        ret = self.simulatorstr()
        for f in self.faces:
            ret.replace(f, Skewb.sticker[f])
        
        return ret

    __repr__ = __str__
    
    def is_solved(self):
        """Return true if all faces are a solid color."""
        for f in self.faces:
            w = self.faces[f][0]
            for r in self.faces[f]:
                if not all(map(lambda arg: arg == w, r)):
                    return False
        return True

    @staticmethod
    def rotate_cw(face):
        """Returns a clockwise rotated version of a given 2D list"""
        return list(face[i] for i in [0, 3, 1, 4, 2])

    @staticmethod
    def rotate_ccw(face):
        """Returns a counterclockwise rotated version of a given 2D list"""
        return list(face[i] for i in [0, 2, 4, 1, 3])

    @staticmethod
    def rotate_2(face):
        """Returns a 180 degree rotated version of a given 2D list"""
        return list(face[i] for i in [0, 4, 3, 2, 1])

    def interact(self):
        """Read, evaluate, print, and loop commands. See help text."""
        while True:
            print(self)
            print()
            usr = input().strip()
            if usr == 'reset' or usr == 'solve':
                self.reset()
            elif usr == 'scramble':
                print(self.scramble())
            elif usr == 'exit':
                break
            elif usr == 'help':
                print(help_text)
            else:
                try:
                    self.apply(TurnSequence(usr))
                except Exception as e:
                    print('%s\nInvalid move: %s' % (e, usr))
