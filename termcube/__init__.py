class TurnSequence(list):
    """Represent a sequence of Turns.
    """
    def __init__(self, iterable=None, turntype=None):
        """Initilize self with a given iterable. If the iterable is a
        string, split it along whitespace and convert each to a Turn
        before initilizing.
        """
        if isinstance(iterable, str):
            super(TurnSequence, self).__init__([turntype(s) for s in iterable.split()])
        elif hasattr(iterable, 'random_turn'):
            super(TurnSequence, self).__init__([iterable])
        elif iterable:
            super(TurnSequence, self).__init__(iterable)
        else:
            super(TurnSequence, self).__init__()

    def inverse(self):
        """Return the TurnSequence that undoes this TurnSequence."""
        return TurnSequence([t.inverse() for t in self][::-1])

    def visualize(self):
        """Return the visualcube image of this TurnSequence"""
        return 'http://cube.crider.co.uk/visualcube.php?fmt=gif&size=200&alg=%s' % self.html_safe_str()

    def html_safe_str(self):
        """Return an HTML safe representation of this TurnSequence"""
        return map(''.join(self).replace('\'', '%27'))

    @staticmethod
    def default_moves(size):
        """Return the default number of moves in a scramble for a cube
        with a given dimension
        Depth   Moves
        1-      0
        2       11
        3       25
        4       40
        5       60
        6       80
        7       100
        8+      120
        """
        if size <= 1:
            return 0
        elif size <= 7:
            return {2:11, 3:25, 4:40, 5:60, 6:80, 7:100}[size]
        else:
            return 120

    @staticmethod
    def get_scramble(size = 3, moves = None):
        """Return a sequence of random turns whose depths are less than or
        equal to the given cube dimension.

        If a number of moves is specified, return that number of moves,
        otherwise, use the value returned by default_moves
        """
        if moves == None:
            moves = TurnSequence.default_moves(size)

        ret = TurnSequence()

        last = Turn('F')
        turn = Turn('F')

        for lcv in range(moves):
            while turn.move == last.move or turn.opposite_face() == last.move:
                turn = Turn.random_turn(size)
            last = turn
            ret.append(turn)

        return ret

    def __str__(self):
        """Return each Turn in notation as a single str."""
        return ' '.join(map(str, self))

    def __repr__(self):
        """Return this TurnSequence unambiguously"""
        return 'TurnSequence(%s)' % ', '.join(map(str, self))
