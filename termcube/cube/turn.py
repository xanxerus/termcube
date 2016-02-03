from random import choice, randrange

class Turn():
    """Represent an arbitrary Turn with a given face, direction, and
    depth.
    """
    directions = ('', '2', '\'')
    faces = ('F', 'R', 'U', 'D', 'L', 'B')
    axes = ('x', 'y', 'z')
    slices = ('M', 'S', 'E')
    moves = faces + axes + slices
    lower_faces = [s.lower() for s in faces]

    def __init__(self, move, direction = '', depth = 0):
        """Initialize a Turn with a given move, direction, and depth.
        If a string of notation is given instead of a move,
        initialize the Turn based on the notation.
        """
        if move in Turn.moves:
            self.move, self.direction = move, direction

            if move in Turn.faces:
                self.depth = depth if depth else 1
            else:
                self.depth = 0
        elif any(s in Turn.lower_faces for s in move) or 'w' in move:
            move = move.replace('w', '')
            move = move.upper()

            face = list(set(move) & set(Turn.moves))[0]
            suffix = move[move.index(face)+1:]
            prefix = move[:move.index(face)]

            if suffix == "2'" or suffix == "'2":
                suffix = '2'

            self.move = face
            self.direction = suffix if suffix in Turn.directions else ''
            self.depth = int(prefix) if len(prefix) else 2
        else:
            face = list(set(move) & set(Turn.moves))[0]
            suffix = move[move.index(face)+1:]
            prefix = move[:move.index(face)]

            if suffix == "2'" or suffix == "'2":
                suffix = '2'

            self.move = face
            self.direction = suffix if suffix in Turn.directions else ''
            self.depth = int(prefix) if len(prefix) else 1

    def __eq__(self, other):
        """Return true if the given Turns have the same move,
        direction, and depth.
        """
        return str(self) == str(other)

    def opposite_face(self):
        """Return the face opposite the face of this Turn.
        If the Turn is a slice or rotation, return its own move.
        """
        if self.move in Turn.faces:
            return Turn.faces[-Turn.faces.index(self.move) - 1]
        else:
            return self.move

    def opposite_direction(self):
        """Return the face opposite direction of this Turn."""
        return Turn.directions[-Turn.directions.index(self.direction)-1]

    def inverse(self):
        """Return the Turn that undoes this one."""
        return Turn(self.move, self.opposite_direction(), self.depth)

    @staticmethod
    def random_turn(size = 3):
        """Return a Turn with a random face, direction, and depth
        less than or equal to half the given cube dimension.
        """
        return Turn(choice(Turn.faces), choice(Turn.directions), randrange(size//2)+1)

    def __str__(self):
        """Return this turn using WCA notation."""
        ret = ''
        if self.depth >= 2:
            ret += str(self.depth)
        ret += self.move
        if self.depth >= 2:
            ret += 'w'
        ret += self.direction

        return ret

    def __repr__(self):
        """Return the move, direction, and depth of this Turn clearly
        defined and separated.
        """
        return 'Turn(move=%s, direction=%s, depth=%s)' % (self.move, self.direction, self.depth)

