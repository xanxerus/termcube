#!/usr/bin/env python3
from .puzzle import Puzzle, PuzzleTurn

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
	
	def wide_slice(self):
		if not self.iswide:
			return None
		
		if self.move in 'FB':
			retmove = 'S'
		elif self.move in 'RL':
			retmove = 'M'
		else: # self.move in 'UD':
			retmove = 'E'
		
		if self.direction == 2:
			retdir = 2
		elif self.move in "FLU":
			retdir = "" if self.direction == "'" else "'"
		else:
			retdir = self.direction
		
		return RubiksCubeTurn(retmove, retdir)

	def __str__(self):
		if iswide:
			return self.move.lower() + self.direction
		else:
			return self.move + self.direction

	__repr__ = __str__

class RubiksCube(Puzzle):
	TURN_TYPE = RubiksCubeTurn
	IS_SOLVABLE = False

	_MOVE_EDGES = {'U': (3, 2, 1, 0),
				'D': (8, 9, 10, 11),
				'R': (1, 5, 9, 4),
				'L': (7, 11, 6, 3),
				'F': (0, 4, 8, 7),
				'B': (2, 6, 10, 5),
				'M': (0, 8, 10, 2),
				'E': (4, 5, 6, 7),
				'S': (3, 1, 9, 11)}

	_MOVE_CORNERS = {'U': (3, 2, 1, 0),
					 'D': (4, 5, 6, 7),
					 'R': (1, 2, 6, 5),
					 'L': (4, 7, 3, 0),
					 'F': (0, 1, 5, 4),
					 'B': (2, 3, 7, 6)}

	def __init__(self):
		self.reset()

	def reset(self):
		self.ep = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
		self.cp = [0, 1, 2, 3, 4, 5, 6, 7]
		self.eo = [0]*12
		self.co = [0]*8
	
	def apply_turn(self, turn):
		#edge orientation
		if turn.direction != "2" and turn.move in "FBMSE":
			for edge in self._MOVE_EDGES[turn.move]:
				self.eo[edge] = 0 if self.eo[edge] else 1

		#corner orientation
		if turn.direction != "2" and turn.move in 'RLFB':
			#cp order is -1, 1, -1, 1 for cw and the reverse for ccw turns
			pos = turn.direction == "'"
			for corner in self._MOVE_CORNERS[turn.move]:
				if pos:
					self.co[corner] = (self.co[corner] + 1) % 3
				else:
					self.co[corner] = (self.co[corner] - 1) % 3
				pos = not pos
		
		#permutations
		if turn.direction == "":
			reassign_cw(self.ep, _MOVE_EDGES[turn.move])
			reassign_cw(self.cp, _MOVE_CORNERS[turn.move])
		elif turn.direction == "'":
			reassign_ccw(self.ep, _MOVE_EDGES[turn.move])
			reassign_ccw(self.cp, _MOVE_CORNERS[turn.move])
		elif turn.direction == "2":
			reassign_2(self.ep, _MOVE_EDGES[turn.move])
			reassign_2(self.cp, _MOVE_CORNERS[turn.move])

		#wide turns
		if turn.iswide:
			self.apply_turn(turn.wide_slice())

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
			ret.append(BigCubeTurn(chosen_face, choice(("", "'", "2"))))

		return ret
	
	def solve(self):
		return None
	
	def draw(self, scr):
		pass

def reassign_cw(arr, indices):
	assert len(indices) == 4
	arr[indices[0]], arr[indices[1]], arr[indices[2]], arr[indices[3]] = \
		arr[indices[3]], arr[indices[0]], arr[indices[1]], arr[indices[2]]

def reassign_ccw(arr, indices):
	assert len(indices) == 4
	arr[indices[0]], arr[indices[1]], arr[indices[2]], arr[indices[3]] = \
		arr[indices[1]], arr[indices[2]], arr[indices[3]], arr[indices[0]]

def reassign_2(arr, indices):
	assert len(indices) == 4
	arr[indices[0]], arr[indices[1]], arr[indices[2]], arr[indices[3]] = \
		arr[indices[2]], arr[indices[3]], arr[indices[0]], arr[indices[1]]
