#!/usr/bin/env python3
from termcube.cube import Cube, ScrambleGenerator
from termcube.simulator import Simulator
from termcube.turn import TurnSequence

from collections import namedtuple, OrderedDict
from os.path import isfile
from sys import exit
from time import time
import curses
import datetime

class Solve():
	def __init__(self, time, penalty, scramble):
		self.time = time
		self.penalty = penalty
		self.tags = ''
		self.scramble = scramble
	
	def totaltime(self):
		if self.penalty == 'DNF':
			return self.time
		return self.time + self.penalty

	def __str__(self):
		timestr = Solve.formattime(self.time)
		if self.penalty == 0:
			return timestr
		elif self.penalty == 2:
			return '%s (+2)' % timestr
		elif self.penalty == 'DNF':
			return '%s (DNF)' % timestr

	def __repr__(self):
		ret = 'Solve: ' + str(self)
		ret += ' '
		if self.tags:
			ret += '#' + ' #'.join(self.tags.replace('#', ' ').split()) + ' '
		ret += str(self.scramble)
		return ret

	@staticmethod
	def formattime(time):
		if time == None:
			return None
		return '%.2f' % time if time < 60 else '%d:%05.2f' % divmod(time, 60)

	@staticmethod
	def avg5(arr):
		if len(arr) <= 0:
			return 0
		elif len(arr) < 5:
			return sum(s.totaltime() for s in arr)/len(arr)
		else:
			return sum(s.totaltime() for s in arr[-5::])/5

class Timer(Simulator):
	help_text = \
"""Term Cube Timer (Curses implementation)

Once a scramble appears, press any key to start inspection.
During inspection, press any key to start the solve time.
Repeat.

Before inspection, it is possible to enter a command by pressing ':'
or tag the previous solve by pressing '#'

Available commands:
#tagname    - Tag the previous solve with the given tagname
:exit       - End this timer session (you will be able to export after)
:merge      - Rename one tag or merge multiple together
:export     - Export your times to a file
:del        - Delete a solve (default last)
:help       - Display this help text"""

	def __init__(self, size = 3, inspection = 15, random = True, length = -1):
		super(Timer, self).__init__(size)
		self.inspection = inspection
		self.random = random
		self.length = length if not random else None
		self.solvenumber = 1
		self.best = self.worst = self.sessionavg = self.curravg5 = self.bestavg5 = None
		self.solves = []

	def __call__(self, scr):
		self.initialize(scr)
		Timer.addcenter(self.q, "Initializing...")

		with ScrambleGenerator(self.size, self.random, self.length) as scrambler:
			while True:
				#Print statistics
				self.printstats(self.r)

				#Scramble
				self.reset()
				self.apply('x')
				scramble = next(scrambler)
				self.apply(scramble)

				#Throw out key presses during scramble wait
				self.q.nodelay(1)
				while self.q.getch() >= 0:
					pass
				self.q.nodelay(0)

				#Print Cube and Scramble
				self.printcube(self.w)
				self.w.refresh()
				Timer.addcenter(self.q, scramble)

				#Command
				usr = chr(self.q.getch())
				while usr in ":#":
					Timer.addcenter(self.q, usr, startx = 0) 
					line = Timer.getln(self.q)
					
					self.command(self.q, usr + line)
					Timer.addcenter(self.q, scramble)
					usr = chr(self.q.getch())

				self.q.nodelay(1)

				#Inspect
				penalty = self.countdown(self.q, self.inspection)

				#Solve
				time = self.countup(self.q)
				self.solves.append(Solve(time, penalty, scramble))
				self.q.getch()
				
				#Update statistics
				if self.best == None:
					self.best = self.worst = time
					self.sessionavg = 1
				if time < self.best:
					self.best = time
				if time > self.worst:
					self.worst = time
				self.sessionavg = (self.sessionavg*(self.solvenumber - 1) + time) / self.solvenumber
				if self.solvenumber >= 5:
					self.curravg5 = Solve.avg5(self.solves)
					if self.bestavg5 == None or self.curravg5 < self.bestavg5:
						self.bestavg5 = self.curravg5
				self.solvenumber += 1

				#Print solve times
				self.printtimes(self.e)

	def printstats(self, scr):
		stats = ["Solve number : %d" % self.solvenumber,
				 "Best : %s" % Solve.formattime(self.best),
				 "Worst : %s" % Solve.formattime(self.worst),
				 "Session Avg : %s" % Solve.formattime(self.sessionavg),
				 "Current Avg 5 : %s" % Solve.formattime(self.curravg5),
				 "Best Avg 5 : %s" % Solve.formattime(self.bestavg5)]
		scr.clear()
		maxy, maxx = scr.getmaxyx()
		for i in range(min(len(stats), maxy)):
			Timer.addcenter(scr, stats[i], starty = i, clear = False)
		scr.refresh()

	def printtimes(self, scr):
		self.e.clear()
		for i in range(min(self.solvenumber - 1, self.e.getmaxyx()[0])):
			timestr = 'Solve %d: %s' % (self.solvenumber-i-1 , self.solves[-i-1])
			Timer.addcenter(self.e, timestr, starty = i, clear = False)
		self.e.refresh()

	def recalculate(self):
		self.best = self.worst = self.sessionavg = self.curravg5 = self.bestavg5 = None
		self.solvenumber = 1
		
		sum = 0
		for solve in self.solves:
			time = solve.totaltime()
			sum += time
			if self.best is None or time < self.best:
				self.best = time
			if self.worst is None or time > self.worst:
				self.worst = time
			if self.solvenumber >= 5:
				self.curravg5 = Solve.avg5(self.solves[:solvenumber])
				if self.bestavg5 is None or self.curravg5 < self.bestavg5:
					self.bestavg5 = self.curravg5
			self.solvenumber += 1
		if self.solvenumber > 1:
			self.sessionavg = sum/(self.solvenumber-1)

	@staticmethod
	def tagsort(arr):
		tags = OrderedDict()
		for solve in arr:
			for tag in solve.tags.split():
				if tag in tags:
					tags[tag].append(solve)
				else:
					tags[tag] = [solve]
		return tags

	@staticmethod
	def addcenter(scr, msg, starty = None, startx = None, clear = True):
		if clear:
			scr.clear()
		maxy, maxx = scr.getmaxyx()
		msg = str(msg)
		if maxy > 1:
			scr.addstr(maxy//2 - 1 if starty is None else starty, (maxx - len(msg))//2 if startx is None else startx, msg)
		else:
			scr.addstr(maxy//2 if starty is None else starty, (maxx - len(msg))//2 if startx is None else startx, msg)

	def command(self, scr, command):
		scr.clear()
		maxy, maxx = scr.getmaxyx() 

		if command == ':exit':
			exit(0)
		elif command.startswith("#"):
			try:
				if self.solves[-1].tags:
					self.solves[-1].tags += ' ' + command[1:]
				else:
					self.solves[-1].tags = command[1:]
			except:
				Timer.addcenter(scr, 'Tag failed')
				scr.getch()
		elif command.startswith(':del'):
			Timer.addcenter(scr, 'Delete which solve? (default last): ', startx = 0)
			index = Timer.getln(scr)
			#~ try:
			index = int(index) if index else self.solvenumber - 1
			t = self.solves[index - 1]
			del self.solves[index - 1]
			self.solvenumber -= 1
			Timer.addcenter(scr, 'Removed solve number %d: %s' % (index, t))
			self.printstats(self.r)
			self.printtimes(self.e)
			self.recalculate()
			scr.getch()
			#~ except Exception as e:
				#~ Timer.addcenter(scr, '%s %s' % (e, index))
				#~ scr.getch()
		elif command.startswith(':merge'):
			mergetags, newtag = '', ''
			while mergetags == '':
				Timer.addcenter(scr, 'List of tag(s) to merge/rename: ', startx = 0)
				mergetags = Timer.getln(scr)
			while newtag == '':
				Timer.addcenter(scr, 'New tag name: ', startx = 0)
				newtag = Timer.getln(scr)
			for solve in self.solves:
				for target in mergetags:
					solve.tags = solve.tags.replace(target, newtag)
				Timer.addcenter(scr, 'Success')
				scr.getch()
		elif command.startswith(':export'):
			Timer.addcenter(scr, 'Name of file to export to: ', startx = 0)
			self.exporttimes(Timer.getln(scr))
			Timer.addcenter(scr, 'Export successful')
			scr.getch()
		else:
			self.cornerandwait(self.scr, self.help_text)
			self.refresh()
	
	def exporttimes(self, filename):
		p = ''
		p += "Average of %d: %.2f" % (self.solvenumber-1, self.sessionavg) + '\n'
		p += "Best : %s" % Solve.formattime(self.best) + '\n'
		p += "Worst : %s" % Solve.formattime(self.worst) + '\n'
		p += "Session Avg : %s" % Solve.formattime(self.sessionavg) + '\n'
		p += "Current Avg 5 : %s" % Solve.formattime(self.curravg5) + '\n'
		p += "Best Avg 5 : %s" % Solve.formattime(self.bestavg5) + '\n'
		p += '\n'
		
		tags = Timer.tagsort(self.solves) 
		for tag in tags:
			solves = tags[tag]
			best = worst = sessionavg = curravg5 = bestavg5 = None
			solvenumber = 1
			
			sum = 0
			for solve in solves:
				time = solve.totaltime()
				sum += time
				if best is None or time < best:
					best = time
				if worst is None or time > worst:
					worst = time
				if solvenumber >= 5:
					curravg5 = Solve.avg5(solves[:solvenumber])
					if bestavg5 is None or curravg5 < bestavg5:
						bestavg5 = curravg5
				solvenumber += 1
			if solvenumber > 1:
				tagavg = sum/(solvenumber-1)
				
			p += 'Solves with the tag: #' + tag.replace('#', '') + '\n'
			p += "Average of %d: %.2f" % (solvenumber-1, tagavg) + '\n'
			p += "Best : %s" % Solve.formattime(best) + '\n'
			p += "Worst : %s" % Solve.formattime(worst) + '\n'
			p += "Session Avg : %s" % Solve.formattime(sessionavg) + '\n'
			p += "Current Avg 5 : %s" % Solve.formattime(curravg5) + '\n'
			p += "Best Avg 5 : %s" % Solve.formattime(bestavg5) + '\n'
			p += '\n' 
			p += '\n'.join(map(repr, solves))
			p += '\n'*3
		
		p += "All solves: \n" + '\n'.join(map(repr, self.solves))
		with open(filename, 'w' if isfile(filename) else 'a') as o:
			o.write(p)
		
		


	def countdown(self, scr, inspection = 15.0):
		scr.clear()
		maxqy, maxqx = scr.getmaxyx()

		ret = 0
		start = time()
		c = -1
		while c < 0 or c == curses.KEY_RESIZE:
			scr.clear()
			delta = inspection + start - time()
			if delta > 0:
				s = '%.2f' % delta
			elif delta > -2:
				s = '+2'
				ret = 2
			else:
				s = 'DNF'
				ret = 'DNF'

			scr.addstr(maxqy//2 - 1, (maxqx - len(s))//2, s)
			scr.refresh()
			c = scr.getch()
			curses.napms(10)
		curses.beep()

		return ret

	def countup(self, scr):
		scr.clear()
		maxqy, maxqx = scr.getmaxyx()

		start = time()
		c = -1
		while True:
			if c == curses.KEY_RESIZE:
				self.resize()
			elif c == 27:
				return -1
			elif c > 0:
				break

			total = time() - start
			s = Solve.formattime(total)
			scr.addstr(maxqy//2 - 1, (maxqx - len(s))//2, s)
			scr.refresh()
			c = scr.getch()
			curses.napms(10)

		return time() - start

	def initialize(self, scr):
		super(Timer, self).initialize(scr)
		self.resize()
		self.q.nodelay(1)
		self.w.nodelay(1)
		self.e.nodelay(1)
		self.r.nodelay(1)

	def resize(self):
		maxy, maxx = self.scr.getmaxyx()
		height = maxy//5
		self.q = curses.newwin(height, maxx, 0, 0)
		self.w = curses.newwin(4*height, maxx//2, height, 0)
		self.e = curses.newwin(2*height, maxx//2, 3*height, maxx//2)
		self.r = curses.newwin(2*height, maxx//2, height, maxx//2)
		self.printcube(self.w)
		self.refresh()

	def refresh(self):
		for s in [self.q, self.w, self.e, self.r]:
			s.redrawwin()
			s.refresh()

	def recolor(self, color):
		for s in [self.q, self.w, self.e, self.r]:
			s.bkgd(color)
			s.bkgdset(color)
			s.refresh()

from sys import argv
def main(scr, size = 3, inspection = 15, random = True, length = -1):
	Timer(size, inspection, random, length)(scr)

curses.wrapper(main, 3 if len(argv) < 2 else argv[1], random=False)#, size, inspection, random, length)
