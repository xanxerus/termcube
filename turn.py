#!/usr/bin/python3
# -*- coding: utf-8 -*-

from random import randrange, choice

class Turn():
	"""Represent an arbitrary Turn with a given face, direction, and
	depth.
	"""
	directions = ('', '2', '\'')
	faces = ('F', 'R', 'U', 'D', 'L', 'B')
	axes = ('x', 'y', 'z')
	slices = ('M', 'S', 'E')
	moves = faces + axes + slices
	lower_faces = map(str.lower, faces)
	
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
		else:
			if len(set(move) & set(Turn.lower_faces)) or 'w' in move:
				move = move.replace('w', '')
				move = move.upper()
				depth = 2
			
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
	def random_turn(x = 3):
		"""Return a Turn with a random face, direction, and depth 
		less than or equal to half the given cube dimension.
		"""
		return Turn(choice(Turn.faces), choice(Turn.directions), randrange(x//2)+1)
	
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

class TurnSequence(list):
	"""Represent a sequence of Turns.
	"""
	def __init__(self, iterable=None):
		"""Initilize self with a given iterable. If the iterable is a
		string, split it along whitespace and convert each to a Turn
		before initilizing.
		"""
		if isinstance(iterable, str):
			super(TurnSequence, self).__init__([Turn(s) for s in iterable.split()])
		elif isinstance(iterable, Turn):
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
	def get_scramble(x = 3, moves = None):
		"""Return a sequence of random turns whose depths are less than or
		equal to the given cube dimension.
		
		If a number of moves is specified, return that number of moves,
		else base it on the cube dimension as follows:
		Depth	Moves
		1-		0
		2		11
		3		25
		4		40
		5		60
		6		80
		7		100
		8+		120
		"""
		if moves == None:
			if x <= 1:
				moves = 0
			elif x <= 7:
				moves = {2:11, 3:25, 4:40, 5:60, 6:80, 7:100}[x]
			else:
				moves = 120
		
		ret = TurnSequence()
		
		last = Turn('F')
		turn = Turn('F')
		
		for lcv in range(moves):
			while turn.move == last.move or turn.opposite_face() == last.move:
				turn = Turn.random_turn(x)
			last = turn
			ret.append(turn)
			
		return ret
	
	def __str__(self):
		"""Return each Turn in notation as a single str."""
		return ' '.join(map(str, self))
	
	def __repr__(self):
		"""Return this TurnSequence unambiguously"""
		return 'TurnSequence(%s)' % ', '.join(map(str, self))
