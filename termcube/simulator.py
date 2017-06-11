import curses

from .puzzle import interpret_sequence, join_sequence

class Simulator():
	help_text = \
"""Term Cube Simulator (Curses implementation)

Manipulate a virtual cube using cube notation!

Press a letter keys to turn the corresponding face clockwise.
Hold shift while pressing that key to turn counterclockwise.

Press a number key to begin typing deep-layered turns.

Press : to initiate a command or type a longer string of notation.

Available commands:
:reset      - Reset the puzzle to a solved position
:solve      - Display a solution (when available)
:scramble   - Print a scramble and apply it
:exit       - Exit the simulator
:help       - View this help text"""
	
	def __init__(self, puzzle):
		self.puzzle = puzzle

	def __call__(self, scr):
		self.initialize(scr)

		#loop until escape is pressed
		usr = ''
		while usr != chr(27):
			self.puzzle.draw(scr)
			usr = chr(scr.getch())

			if usr in ':1234567890':
				scr.addstr(0, 0, usr)
				if self.command(scr, usr + self.getln(scr, 0, 1).strip()) < 0:
					break
			else:
				moveset = {usr.lower(), usr.upper()} & self.puzzle.TURN_TYPE.MOVES
				if moveset:
					t = self.puzzle.TURN_TYPE(moveset.pop())
					if usr == usr.upper():
						t = t.inverse()
					self.puzzle.apply(t)

	def command(self, scr, command):
		if command == ':reset':
			self.puzzle.reset()
		elif command == ':solve':
			if self.puzzle.IS_SOLVABLE:
				q = self.puzzle.solve()
				scr.addstr(0, 0, str(q[0]))
				scr.addstr(1, 0, 'Solve time: %.2f seconds' % q[1])
				scr.addstr(2, 0, 'Apply this solution? (y/n): ')
				if chr(scr.getch()) == 'y':
					scr.nodelay(1)
					for t in interpret_sequence(q[0], self.puzzle.TURN_TYPE):
						self.puzzle.apply_turn(t)
						self.printpuzzle(scr)
						curses.napms(100)
						scr.getch()
					scr.nodelay(0)
			else:
				addcenter(scr, 'This puzzle has no solver as of yet', starty = 0, clear = False)
				scr.getch()
		elif command == ':scramble':
			scramble = self.puzzle.scramble()
			self.puzzle.apply(scramble)
			self.puzzle.draw(scr)
			addcenter(scr, join_sequence(scramble), starty = 0, clear = False)
			scr.getch()
		elif command == ':exit':
			return -1
		elif command == ':help':
			Simulator.cornerandwait(scr, Simulator.help_text)
		else:
			try:
				self.puzzle.apply(interpret_sequence(command[1:], self.puzzle.TURN_TYPE))
			except Exception as e:
				scr.addstr(0, 0, '%s -- %s' % (e, command[1:]))
				scr.refresh()
				scr.getch()
		return 0

	@staticmethod
	def cornerandwait(scr, msg):
		scr.clear()
		try:
			scr.addstr(0, 0, msg)
		except:
			pass
		while scr.getch() == curses.KEY_RESIZE:
			pass

	def initialize(self, scr):
		self.scr = scr
		if not curses.has_colors():
			raise NoCursesException(self.puzzle)

		curses.init_pair(ord('F') - 60, curses.COLOR_WHITE, curses.COLOR_WHITE)
		curses.init_pair(ord('R') - 60, curses.COLOR_WHITE, curses.COLOR_RED)
		curses.init_pair(ord('U') - 60, curses.COLOR_WHITE, curses.COLOR_BLUE)
		curses.init_pair(ord('L') - 60, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
		curses.init_pair(ord('D') - 60, curses.COLOR_WHITE, curses.COLOR_GREEN)
		curses.init_pair(ord('B') - 60, curses.COLOR_WHITE, curses.COLOR_YELLOW)
		scr.leaveok(0)
		curses.noecho()

		try:
			curses.curs_set(0)
		except:
			pass

	@staticmethod
	def getln(scr, y, x):
		try:
			curses.curs_set(2)
		except:
			pass

		curses.echo()
		ret = scr.getstr(y, x).decode('utf-8')
		curses.noecho()

		try:
			curses.curs_set(0)
		except:
			pass

		return ret

def addcenter(scr, msg, starty = None, startx = None, clear = True):
	if clear:
		scr.clear()
	maxy, maxx = scr.getmaxyx()
	msg = str(msg)
	if maxy > 1:
		scr.addstr(maxy//2 - 1 if starty is None else starty, max(0, (maxx - len(msg))//2) if startx is None else startx, msg)
	else:
		scr.addstr(maxy//2 if starty is None else starty, max(0, (maxx - len(msg))//2) if startx is None else startx, msg)
	if clear:
		scr.refresh()

def simulate(puzzle):
	curses.wrapper(Simulator(puzzle))
