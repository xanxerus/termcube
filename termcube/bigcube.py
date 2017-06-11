#!/usr/bin/env python3
from .puzzle import Puzzle, PuzzleTurn, interpret_sequence, \
					invert_sequence, rotate_cw, rotate_ccw, rotate_2
from random import choice, randrange
import curses

class BigCubeTurn(PuzzleTurn):
	MOVES = {"F", "R", "U", "L", "D", "B", "x", "y", "z", "M", "S", "E"}
	
	def __init__(self, move, direction = "", depth = 0):
		if direction not in ("", "'", "2"):
			raise ValueError("Invalid direction: %s" % direction)
		elif depth < 0:
			raise ValueError("Depth must be nonnegative")
		
		#copy constructor
		elif isinstance(move, BigCubeTurn):
			self.direction = move.direction
			self.move = move.move
			self.depth = move.depth

		#non-string input
		elif not isinstance(move, str):
			raise TypeError("%s object is neither a str nor a BigCubeTurn" % type(move))

		#empty string input
		elif len(move) == 0:
			raise ValueError("Move cannot be empty string")

		#copy the args
		elif len(move) == 1 and move in "FRUDLBxyzMSE":
			self.move, self.direction = move, direction
			if move in "FRUDLB":
				self.depth = depth or 1
			else:
				self.depth = 0

		#parse the string
		else:
			wide = any(s in move for s in "frudlbw")
			
			if wide:
				move = move.replace('w', '')
				move = move.upper()

			face = list(set(move) & set("FRUDLB" if wide else "FRULDBxyzMSE"))
			if face:
				face = face[0]
			else:
				raise ValueError("String does not describe a valid BigCubeTurn")
			suffix = move[move.index(face)+1:]
			prefix = move[:move.index(face)]

			if prefix and face not in "FRUDLB":
				raise ValueError("String does not describe a valid BigCubeTurn")

			if suffix == "2'" or suffix == "'2":
				suffix = '2'

			self.move = face
			
			if suffix in ("", "'", "2"):
				self.direction = suffix
			else:
				raise ValueError("String does not describe a valid BigCubeTurn")
			
			if prefix:
				try:
					self.depth = int(prefix)
					if self.depth <= 0:
						raise ValueError("String does not describe a valid BigCubeTurn")
				except:
					raise ValueError("String does not describe a valid BigCubeTurn")
			else:
				self.depth = 2 if wide else 1 if self.move in "FRUDLB" else 0

	def inverse(self):
		if self.direction == "":
			opposite_direction = "'"
		elif self.direction == "'":
			opposite_direction = ""
		else:
			opposite_direction = "2"
		
		return BigCubeTurn(self.move, opposite_direction, self.depth)
	
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

	__repr__ = __str__

class BigCube(Puzzle):
	TURN_TYPE = BigCubeTurn

	def __init__(self, size=3):
		self.size = size
		self.reset()
	
	def reset(self):
		self.faces = dict()
		for face in 'FRULDB':
			self.faces[face] = [[face]*self.size for q in range(self.size)]

	def apply_turn(self, turn):
		if turn.depth > self.size:
			raise ValueError("Turn is deeper than puzzle side length")
		
		for w in range(1 + ("", "2", "'").index(turn.direction)):
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

			if turn.move in "FRUDLB":
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

	def apply(self, turns):
		if isinstance(turns, BigCubeTurn):
			self.apply_turn(turns)
		elif hasattr(iter(turns), '__next__'):
			for turn in interpret_sequence(turns, BigCubeTurn):
				self.apply_turn(turn)
	
	def scramble(self):
		ret = []
		opposite = {'F':'B', 'B':'F', 'U':'D', 'D':'U', 'L':'R', 'R':'L', '':''}
		chosen_face = ''
		for _ in range(20):
			chosen_face = choice("FRUDLB".replace(chosen_face, '').replace(opposite[chosen_face], ''))
			ret.append(BigCubeTurn(chosen_face, choice(("", "'", "2")), randrange(1, 1 + self.size//2)))

		return ret
	
	def simulatorstr(self):
		ret = ''
		for r in self.faces['U']:
			ret += '  '*self.size
			for c in r:
				ret += c*2
			ret += '\n'

		for r in range(self.size):
			for c in self.faces['L'][r]:
				ret += c*2
			for c in self.faces['F'][r]:
				ret += c*2
			for c in self.faces['R'][r]:
				ret += c*2
			ret += '\n'

		for r in self.faces['D'] + self.faces['B']:
			ret += '  '*self.size
			for c in r:
				ret += c*2
			ret += '\n'

		return ret

	def draw(self, scr):
		maxy, maxx = scr.getmaxyx()
		scr.clear()
		y = (maxy - 3*self.size) // 2 - 1
		xinit = (maxx - 6*self.size) // 2 - 1
		
		for line in self.simulatorstr().split('\n'):
			x = xinit
			for c in line:
				if c != ' ':
					scr.addstr(y, x, ' ', curses.color_pair(ord(c) - 60))
				x += 1
			y += 1
		
		scr.move(maxy-1, maxx-1)
