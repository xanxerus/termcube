from .pykociemba import search
from .. import TurnSequence

from time import time

errors = {
    'Error 1': 'There is not exactly one facelet of each colour',
    'Error 2': 'Not all 12 edges exist exactly once',
    'Error 3': 'Flip error: One edge has to be flipped',
    'Error 4': 'Not all corners exist exactly once',
    'Error 5': 'Twist error: One corner has to be twisted',
    'Error 6': 'Parity error: Two corners or two edges have to be exchanged',
    'Error 7': 'No solution exists for the given maxDepth',
    'Error 8': 'Timeout, no solution within given time'
}

def solve(facelets, maxDepth = 24, timeOut = 1000, useSeparator = False):
    t = time()
    res = search.Search().solution(facelets, maxDepth, timeOut, useSeparator).strip()
    if res in errors:
        return errors[res], time() - t
    else:
        return TurnSequence(res), time() - t
