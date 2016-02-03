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

    def __str__(self):
        """Return each Turn in notation as a single str."""
        return ' '.join(map(str, self))

    def __repr__(self):
        """Return this TurnSequence unambiguously"""
        return 'TurnSequence(%s)' % ', '.join(map(str, self))
