#!/usr/bin/env python3
from abc import ABCMeta, abstractmethod

class Puzzle(metaclass=ABCMeta):
	@abstractmethod
	def reset(self):
		pass
	
	@abstractmethod
	def apply_turn(self, turn):
		pass

	@abstractmethod
	def apply(self, turns):
		pass
	
	@abstractmethod
	def scramble(self):
		pass
	
	def solve(self):
		return None
	
	@abstractmethod
	def draw(self, scr):
		pass

class PuzzleTurn(metaclass=ABCMeta):
	@abstractmethod
	def inverse(self):
		pass
	
	@staticmethod
	@abstractmethod
	def random_turn(cls):
		pass

def interpret_sequence(iterable, turntype):
	if not issubclass(turntype, PuzzleTurn):
		raise TypeError('%s object is not a subclass of Puzzle.Turn' % turntype);

	if isinstance(iterable, str): #they gave us a string
		return list(turntype(s) for s in iterable.split())
	elif hasattr(iter(iterable), '__next__'): #they gave us something iterable
		return [turntype(s) for s in iterable]
	else: #we did not get an iterable
		raise TypeError("%s object is not iterable" % type(iterable))

def invert_sequence(turnsequence):
	return [t.inverse() for t in reversed(turnsequence)]

def rotate_cw(face):
	"""Returns a clockwise rotated version of a given 2D list"""
	return [list(a) for a in zip(*face[::-1])]

def rotate_ccw(face):
	"""Returns a counterclockwise rotated version of a given 2D list"""
	return [list(a) for a in zip(*face)][::-1]

def rotate_2(face):
	"""Returns a 180 degree rotated version of a given 2D list"""
	return [a[::-1] for a in face[::-1]]
