from .cube import Cube

from queue import Queue
from threading import Thread

class ScrambleGenerator():
    def __init__(self, puzzle = None, random = True, length = None, capacity = 10):
        self.puzzle = puzzle if puzzle else Cube(3)
        self.queue = Queue(max((capacity, 1)))
        self.random = random
        self.length = length
        self.thread = Thread(target=self.enqueue_scramble)
        self.stopped = False
        self.thread.start()

    def enqueue_scramble(self):
        """Fill a given Queue with scramble until it is either full or a given capacity has been reached"""
        while not self.stopped:
            if not self.queue.full():
                self.queue.put(self.puzzle.get_scramble(self.random, self.length))

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
