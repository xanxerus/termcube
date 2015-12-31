#!/usr/bin/python3
# -*- coding: utf-8 -*-

from turn import Turn, TurnSequence
from time import time, sleep
from sys import stderr
from threading import Thread
import scramble
from queue import Queue
import solve

#~ from solve import _solve

help_text = '''Cube interactive mode
Manipulate a virtual cube
Available commands:
-reset		- Reset the cube to a solved position
-solve		- Display a two-phase solution
-optimal	- Display the optimal solution (will take a long time)
-sexy		- Apply the sexy move (R U R' U')
-scramble	- Print a random Turn Sequence and apply it
-solved?	- Print if the cube is solved
-exit		- Exit interactive mode
-help		- Access this help text'''

def rotate_cw(face):
	"""Returns a clockwise rotated version of a given 2D list"""
	return [list(a) for a in zip(*face[::-1])]

def rotate_ccw(face):
	"""Returns a counterclockwise rotated version of a given 2D list"""
	return [list(a) for a in zip(*face)][::-1]

def rotate_2(face):
	"""Returns a 180 degree rotated version of a given 2D list"""
	return rotate_cw(rotate_cw(face))


class Cube:
	"""Represent a Cube with a given side length.
	Support turning of faces using Turn objects.
	Allow visualization using ANSI color codes in terminal or 
	using the visualcube API.
	"""
	sticker = {'F': '\033[47m \033[0m',
			   'R': '\033[41m \033[0m',
			   'U': '\033[44m \033[0m',
			   'D': '\033[42m \033[0m',
			   'L': '\033[45m \033[0m',
			   'B': '\033[43m \033[0m'}
	
	color =   {'F': 'w',
			   'R': 'r',
			   'U': 'b',
			   'D': 'g',
			   'L': 'o',
			   'B': 'y'}
	
	def __init__(self, x = 3, wca = None):
		"""Initialize a Cube with a given dimension in a solved state."""
		self.x = x
		self.reset()
	
	def reset(self):
		"""Initialize all sides to unique solid colors."""
		self.faces = {'F' : [['F']*self.x for q in range(self.x)],
					  'R' : [['R']*self.x for q in range(self.x)],
					  'U' : [['U']*self.x for q in range(self.x)],
					  'D' : [['D']*self.x for q in range(self.x)],
					  'L' : [['L']*self.x for q in range(self.x)],
					  'B' : [['B']*self.x for q in range(self.x)]}
	
	def scramble(self, random_state=True, moves=-1):
		"""Generate, apply, and return a scramble."""
		s = self.get_scramble(random_state, moves)
		self.apply(s)
		return s
	
	def get_scramble(self, random_state=True, moves=-1):
		"""Generate and return a scramble without applying."""
		if random_state and self.x == 3:
			return scramble.scramble()
		elif moves > 1:
			return TurnSequence.get_scramble(self.x, moves)
		else:
			return TurnSequence.get_scramble(self.x)
	
	def apply(self, seq):
		"""Apply a given TurnSequence to this Cube. If a str was given,
		convert to TurnSequence then apply.
		"""
		for turn in TurnSequence(seq):
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
					for q in range(self.x):
						if turn.move == 'F':
							(self.faces['D'][g-1][q], 
							self.faces['R'][-q-1][g-1], 
							self.faces['U'][self.x-g][-q-1], 
							self.faces['L'][q][self.x-g]) = \
							(self.faces['R'][-q-1][g-1],
							self.faces['U'][self.x-g][-q-1],
							self.faces['L'][q][self.x-g],
							self.faces['D'][g-1][q])
						elif turn.move == 'U':
							(self.faces['F'][g-1][q],
							self.faces['R'][g-1][q],
							self.faces['B'][self.x-g][-q-1],
							self.faces['L'][g-1][q]) = \
							(self.faces['R'][g-1][q],
							self.faces['B'][self.x-g][-q-1],
							self.faces['L'][g-1][q],
							self.faces['F'][g-1][q])
						elif turn.move == 'D':
							(self.faces['B'][g-1][-q-1],
							self.faces['R'][self.x-g][q],
							self.faces['F'][self.x-g][q],
							self.faces['L'][self.x-g][q]) = \
							(self.faces['R'][self.x-g][q],
							self.faces['F'][self.x-g][q],
							self.faces['L'][self.x-g][q],
							self.faces['B'][g-1][-q-1])
						elif turn.move == 'B':
							(self.faces['L'][q][g-1],
							self.faces['U'][g-1][-q-1],
							self.faces['R'][-q-1][self.x-g],
							self.faces['D'][self.x-g][q]) = \
							(self.faces['U'][g-1][-q-1],
							self.faces['R'][-q-1][self.x-g],
							self.faces['D'][self.x-g][q],
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
							(self.faces['B'][q][self.x-g],
							self.faces['U'][q][self.x-g],
							self.faces['F'][q][self.x-g],
							self.faces['D'][q][self.x-g]) = \
							(self.faces['U'][q][self.x-g],
							self.faces['F'][q][self.x-g],
							self.faces['D'][q][self.x-g],
							self.faces['B'][q][self.x-g])
		return self
	
	def __eq__(self, other):
		"""Return true if all stickers match."""
		return self.faces == other.faces
	
	def __str__(self):
		"""Return the type of cube and an ANSI color representation."""
		ret = '{0}x{0}x{0} Cube'.format(self.x) + '\n'
		for r in self.faces['U']:
			ret += ' '*self.x
			for c in r:
				ret += Cube.sticker[c]
			ret += '\n'
		
		for r in range(self.x):
			for c in self.faces['L'][r]:
				ret += Cube.sticker[c]
			for c in range(self.x):
				ret += Cube.sticker[self.faces['F'][r][c]]
			for c in self.faces['R'][r]:
				ret += Cube.sticker[c]
			ret += '\n'
		
		for r in self.faces['D']:
			ret += ' '*self.x
			for c in r:
				ret += Cube.sticker[c]
			ret += '\n'
		
		for r in self.faces['B']:
			ret += ' '*self.x
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
		return ret
	
	def two_phase_solution(self):
		"""Find a solution using Kociemba's two phase algoithm."""
		try:
			assert self.x == 3
		except:
			print('Cube must be a 3x3x3 to find a two phase solution', file=stderr)
		return solve.solve(self.kociemba_str())
	
	def optimal_solution(self, verbose = False):
		"""Attempt to find an optimal solution using two-phase. Slow"""
		try:
			assert self.x == 3
		except:
			print('Cube must be a 3x3x3 to find a two phase solution', file=stderr)
		return solve.solve_optimal_from_bottom(self.kociemba_str(), verbose)
	
	def __repr__(self):
		"""Return the type of cube and an ANSI color representation."""
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
		
		return 'http://cube.crider.co.uk/visualcube.php?fmt=gif&pzl=%s&fc=%s' % (self.x, facelet_colors)
	
	def interact(self):
		"""Read, evaluate, print, and loop commands. See help text."""
		while True:
			print(self)
			print()
			usr = input()
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
			elif usr == 'optimal':
				q = self.optimal_solution(verbose = True)
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
			elif usr == 'solved?':
				print(self.is_solved())
			elif usr == 'exit':
				break
			elif usr == 'help':
				print(help_text)
			else:
				self.apply(TurnSequence(usr))

class ScrambleGenerator():
	def __init__(self, x = 3, capacity = 10, random_state = True, moves = -1):
		self.cube = Cube(x)
		self.queue = Queue(max((capacity, 0)))
		self.random_state = random_state
		self.moves = moves
		self.thread = Thread(target=self.enqueue_scramble)
		self.stopped = False
		self.thread.start()

	def enqueue_scramble(self):
		"""Fill a given Queue with scramble until it is either full or a given capacity has been reached"""
		while not self.stopped:
			if not self.queue.full():
				self.queue.put(self.cube.get_scramble(self.random_state, self.moves))

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

if __name__=="__main__":
	#~ Cube(3).interact()
	demo_kociemba()
	
