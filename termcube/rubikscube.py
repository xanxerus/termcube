#!/usr/bin/env python3
from .puzzle import Puzzle, PuzzleTurn, interpret_sequence
from random import choice
import curses

class RubiksCubeTurn(PuzzleTurn):
	MOVES = {"F", "R", "U", "L", "D", "B", "x", "y", "z", "M", "S", "E"}

	def __init__(self, move, direction="", iswide=False):
		if direction not in ("", "'", "2"):
			raise ValueError("Invalid direction: %s" % direction)
		elif iswide not in (True, False):
			raise ValueError("Width must be boolean")
		elif iswide and move not in "FRUDLB":
			raise ValueError("Only face turns can be wide")
		
		#copy constructor
		elif isinstance(move, RubiksCubeTurn):
			self.move = move.move
			self.direction = move.direction
			self.iswide = move.iswide

		#non-string input
		elif not isinstance(move, str):
			raise TypeError("%s object is neither a str nor a RubiksCubeTurn" % type(move))

		#empty string input
		elif len(move) == 0:
			raise ValueError("Move cannot be empty string")

		#parse the string or copy args
		elif len(move) < 3 and move[0] in "FRUDLBxyzMSEfrudlb":
			self.move = move[0].upper()
			
			if len(move) > 1:
				if move[1] in "'2":
					self.direction = move[1]
				else:
					raise ValueError("String does not describe a valid RubiksCubeTurn")
			else:
				self.direction = direction
			
			self.iswide = move[0] != self.move
			if self.move in 'XYZ':
				self.move = self.move.lower()

		#bad input
		else:
			raise ValueError("String does not describe a valid RubiksCubeTurn")
	
	def inverse(self):
		ret = RubiksCubeTurn(self)
		
		if self.direction == "":
			ret.direction = "'"
		elif self.direction == "'":
			ret.direction = ""
		else:
			ret.direction = "2"
		
		return ret
	
	def decompose(self):
		if not self.iswide:
			return self
		
		if self.move in 'FBz':
			retmove = 'S'
		elif self.move in 'RLx':
			retmove = 'M'
		else: # self.move in 'UDy':
			retmove = 'E'
		
		if self.direction == 2:
			retdir = 2
		elif self.move in "BRUxy":
			retdir = "" if self.direction == "'" else "'"
		else:
			retdir = self.direction
		
		if self.move == "x":
			return RubiksCubeTurn(retmove, retdir),\
				   RubiksCubeTurn('R', self.direction),\
				   RubiksCubeTurn('L', '' if self.direction == "'" else "'" if self.direction == '' else self.direction)
		elif self.move == "y":
			return RubiksCubeTurn(retmove, retdir),\
				   RubiksCubeTurn('U', self.direction),\
				   RubiksCubeTurn('D', '' if self.direction == "'" else "'" if self.direction == '' else self.direction)
		elif self.move == "z":
			return RubiksCubeTurn(retmove, retdir),\
				   RubiksCubeTurn('F', self.direction),\
				   RubiksCubeTurn('B', '' if self.direction == "'" else "'" if self.direction == '' else self.direction)
		else:
			return RubiksCubeTurn(self.move, self.direction), RubiksCubeTurn(retmove, retdir)

	def __str__(self):
		if self.iswide:
			return self.move.lower() + self.direction
		else:
			return self.move + self.direction

	__repr__ = __str__

class RubiksCube(Puzzle):
	TURN_TYPE = RubiksCubeTurn
	IS_SOLVABLE = False

	_MOVE_CORNERS = {'U': (3, 2, 1, 0),
					 'D': (4, 5, 6, 7),
					 'R': (1, 2, 6, 5),
					 'L': (4, 7, 3, 0),
					 'F': (0, 1, 5, 4),
					 'B': (2, 3, 7, 6)}

	_MOVE_EDGES = {'U': (3, 2, 1, 0),
				   'D': (8, 9, 10, 11),
				   'R': (1, 5, 9, 4),
				   'L': (7, 11, 6, 3),
				   'F': (0, 4, 8, 7),
				   'B': (2, 6, 10, 5),
				   'M': (0, 8, 10, 2),
				   'E': (4, 5, 6, 7),
				   'S': (3, 1, 9, 11)}

	_MOVE_CENTERS = {'M': (0, 3, 5, 1),
					 'S': (0, 2, 5, 4),
					 'E': (1, 4, 3, 2)}

	_CORNER_PLACEMENT = [((2, 3), (3, 3), (3, 2)),
						 ((2, 5), (3, 6), (3, 5)),
						 ((0, 5), (11, 5), (3, 8)),
						 ((0, 3), (3, 0), (11, 3)),
						 ((6, 3), (5, 2), (5, 3)),
						 ((6, 5), (5, 5), (5, 6)),
						 ((8, 5), (5, 8), (9, 5)),
						 ((8, 3), (9, 3), (5, 0))]

	_EDGE_PLACEMENT = [((2, 4), (3, 4)),
					   ((1, 5), (3, 7)),
					   ((0, 4), (11, 4)),
					   ((1, 3), (3, 1)),
					   ((4, 5), (4, 6)),
					   ((10, 5), (4, 8)),
					   ((10, 3), (4, 0)),
					   ((4, 3), (4, 2)),
					   ((6, 4), (5, 4)),
					   ((7, 5), (5, 7)),
					   ((8, 4), (9, 4)),
					   ((7, 3), (5, 1))]

	_CENTER_PLACEMENT = [(1, 4), (10, 4), (4, 7), (4, 4), (4, 1), (7, 4)]

	_CORNER_COLORS = [(0, 3, 4),
					 (0, 2, 3),
					 (0, 1, 2),
					 (0, 4, 1),
					 (5, 4, 3),
					 (5, 3, 2),
					 (5, 2, 1),
					 (5, 1, 4)]

	_EDGE_COLORS = [(0, 3),
					(0, 2),
					(0, 1),
					(0, 4),
					(3, 2),
					(1, 2),
					(1, 4),
					(3, 4),
					(5, 3),
					(5, 2),
					(5, 1),
					(5, 4)]

	_DECODE_COLORS = ['W', 'B', 'R', 'G', 'O', 'Y']

	def __init__(self):
		self.reset()

	def reset(self):
		self.ep = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
		self.cp = [0, 1, 2, 3, 4, 5, 6, 7]
		self.eo = [0]*12
		self.co = [0]*8
		self.mp = [0, 1, 2, 3, 4, 5]
	
	def apply_turn(self, turn):
		#wide turns
		if turn.iswide:
			for t in turn.decompose():
				self.apply_turn(t)
			return
		
		#edge orientation
		if turn.direction != "2" and turn.move in "FBMSE":
			for edge in RubiksCube._MOVE_EDGES[turn.move]:
				self.eo[edge] = 0 if self.eo[edge] else 1

		#corner orientation
		if turn.direction != "2" and turn.move in 'RLFB':
			#cp order is -1, 1, -1, 1 for both turns
			pos = False
			for corner in RubiksCube._MOVE_CORNERS[turn.move]:
				if pos:
					self.co[corner] = (self.co[corner] + 1) % 3
				else:
					self.co[corner] = (self.co[corner] - 1) % 3
				pos = not pos
		
		#permutations
		if turn.direction == "":
			reassign_cw(self.ep, RubiksCube._MOVE_EDGES.get(turn.move, None))
			reassign_cw(self.cp, RubiksCube._MOVE_CORNERS.get(turn.move, None))
			reassign_cw(self.eo, RubiksCube._MOVE_EDGES.get(turn.move, None))
			reassign_cw(self.co, RubiksCube._MOVE_CORNERS.get(turn.move, None))
			reassign_cw(self.mp, RubiksCube._MOVE_CENTERS.get(turn.move, None))
		elif turn.direction == "'":
			reassign_ccw(self.ep, RubiksCube._MOVE_EDGES.get(turn.move, None))
			reassign_ccw(self.cp, RubiksCube._MOVE_CORNERS.get(turn.move, None))
			reassign_ccw(self.eo, RubiksCube._MOVE_EDGES.get(turn.move, None))
			reassign_ccw(self.co, RubiksCube._MOVE_CORNERS.get(turn.move, None))
			reassign_ccw(self.mp, RubiksCube._MOVE_CENTERS.get(turn.move, None))
		elif turn.direction == "2":
			reassign_2(self.ep, RubiksCube._MOVE_EDGES.get(turn.move, None))
			reassign_2(self.cp, RubiksCube._MOVE_CORNERS.get(turn.move, None))
			reassign_2(self.eo, RubiksCube._MOVE_EDGES.get(turn.move, None))
			reassign_2(self.co, RubiksCube._MOVE_CORNERS.get(turn.move, None))
			reassign_2(self.mp, RubiksCube._MOVE_CENTERS.get(turn.move, None))


	def apply(self, turns):
		if isinstance(turns, RubiksCubeTurn):
			self.apply_turn(turns)
		elif hasattr(iter(turns), '__next__'):
			for turn in interpret_sequence(turns, RubiksCubeTurn):
				self.apply_turn(turn)
	
	def scramble(self):
		ret = []
		opposite = {'F':'B', 'B':'F', 'U':'D', 'D':'U', 'L':'R', 'R':'L', '':''}
		chosen_face = ''
		for _ in range(20):
			chosen_face = choice("FRUDLB".replace(chosen_face, '').replace(opposite[chosen_face], ''))
			ret.append(RubiksCubeTurn(chosen_face, choice(("", "'", "2"))))

		return ret
	
	def solve(self):
		return None
	
	def draw(self, scr):
		maxy, maxx = scr.getmaxyx()
		yinit = maxy // 2 - 6 
		xinit = maxx // 2 - 9
		scr.clear()
		
		#will not fit.
		if xinit < 0 or yinit < 0:
			return False
		
		#corners
		for i in range(8):
			for j in range(3):
				r, c = RubiksCube._CORNER_PLACEMENT[i][j]
				color = RubiksCube._DECODE_COLORS[RubiksCube._CORNER_COLORS[self.cp[i]][(j + self.co[i])%3]]
				scr.addstr(r+yinit, c+xinit, ' ', curses.color_pair(ord(color) - 60))
		
		#edges
		for i in range(12):
			for j in range(2):
				r, c = RubiksCube._EDGE_PLACEMENT[i][j]
				color = RubiksCube._DECODE_COLORS[RubiksCube._EDGE_COLORS[self.ep[i]][(j + self.eo[i])%2]]
				scr.addstr(r+yinit, c+xinit, ' ', curses.color_pair(ord(color) - 60))
		
		#centers
		for i in range(6):
			r, c = RubiksCube._CENTER_PLACEMENT[i]
			color = RubiksCube._DECODE_COLORS[self.mp[i]]
			scr.addstr(r+yinit, c+xinit, ' ', curses.color_pair(ord(color) - 60))
		
		scr.move(maxy-1, maxx-1)

	def __str__(self):
		return 'eo: %s\nep: %s\nco: %s\ncp: %s\n' % (self.eo, self.ep, self.co, self.cp)
	
	__repr__ = __str__

def reassign_cw(arr, indices):
	if indices and len(indices) == 4:
		arr[indices[0]], arr[indices[1]], arr[indices[2]], arr[indices[3]] = \
			arr[indices[3]], arr[indices[0]], arr[indices[1]], arr[indices[2]]

def reassign_ccw(arr, indices):
	if indices and len(indices) == 4:
		arr[indices[0]], arr[indices[1]], arr[indices[2]], arr[indices[3]] = \
			arr[indices[1]], arr[indices[2]], arr[indices[3]], arr[indices[0]]

def reassign_2(arr, indices):
	if indices and len(indices) == 4:
		arr[indices[0]], arr[indices[1]], arr[indices[2]], arr[indices[3]] = \
			arr[indices[2]], arr[indices[3]], arr[indices[0]], arr[indices[1]]
