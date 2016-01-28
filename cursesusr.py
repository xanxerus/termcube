#!/usr/bin/env python3
from termcube.cube import Cube, ScrambleGenerator
from termcube.simulator import Simulator
from termcube.turn import TurnSequence

from collections import namedtuple
from sys import exit
from time import time
import curses
import datetime

class Solve(namedtuple('Solve', ['time', 'penalty', 'tags', 'scramble'])):
	def totaltime(self):
		return self.time + self.penalty

class Timer(Simulator):
	def __init__(self, size = 3, inspection=15, tags=True, random=True, length=-1):
		super(Timer, self).__init__(size)
		self.inpection = inspection
		self.tags = tags
		self.random = random
		self.length = length if not random else None
	
	def __call__(self, scr):
		self.initialize(scr)
		solves = []
		solvenumber = 0
		qy, qx = self.q.getmaxyx()
		self.q.addstr(qy//2 -1, (qx - len("Initializing..."))//2, "Initializing...")
		self.q.refresh()
		
		with ScrambleGenerator(self.size, random_state=False) as scrambler:
			while True:
				solvenumber+=1
				#Scramble
				self.reset()
				self.apply('x')
				scramble = next(scrambler)
				self.apply(scramble)

				#Print Cube and Scramble
				self.printcube(self.w)
				self.w.refresh()
				qy, qx = self.q.getmaxyx()
				self.q.addstr(qy//2 - 1, (qx - len(str(scramble)))//2, str(scramble))

				#Inspect
				self.q.nodelay(0)
				self.q.getch()
				self.q.nodelay(1)
				penalty = self.countdown(self.q)
				
				#Solve
				time = self.countup(self.q)
				solves.append(Solve(time, penalty, 'Untagged', scramble))
				self.q.getch()
				
				#Print solve times
				self.e.clear()
				for i in range(min(solvenumber, self.e.getmaxyx()[0])):
					total = solves[-i-1].totaltime()
					self.e.addstr(i, 0, ('Solve %d: ' % (solvenumber - i)) + ('%.2f' % total if total < 60 else '%d:%05.2f' % divmod(total, 60)))
				self.e.refresh()

	def countdown(self, scr, inspection = 15.0):
		scr.clear()
		maxqy, maxqx = scr.getmaxyx()
		
		ret = 0
		start = time()
		c = -1
		while c < 0 or c == curses.KEY_RESIZE:
			delta = inspection + start - time()
			if delta < inspection:
				s = '%.2f' % delta
			elif delta < inspection + 2:
				s = '+2'
				ret = 2
			else:
				s = 'DNF'
				ret = None
			
			scr.addstr(maxqy//2 - 1, (maxqx - len(s))//2, s)
			scr.refresh()
			c = scr.getch()
			curses.napms(10)
		curses.beep()
		
		return ret

	def countup(self, scr):
		scr.clear()
		#~ self.recolor(curses.color_pair(ord('D')-60))
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
			s = '%.2f' % total if total < 60 else '%d:%05.2f' % divmod(total, 60)
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
	
	def resize(self):
		maxy, maxx = self.scr.getmaxyx()
		height = maxy//5
		self.q = curses.newwin(height, maxx, 0, 0)
		self.w = curses.newwin(4*height, maxx//2, height, 0)
		self.e = curses.newwin(4*height, maxx//2, height, maxx//2)
		self.printcube(self.w)
		self.refresh()
	
	def refresh(self):
		for s in [self.q, self.w, self.e]:
			s.refresh()
	
	def recolor(self, color):
		for s in [self.q, self.w, self.e]:
			s.bkgd(color)
			s.bkgdset(color)
			s.refresh()

def main(scr):
	Timer()(scr)
curses.wrapper(main)
#~ for i in sorted('FRULDB'):
	#~ print('%s %2d %2d' % (i, ord(i) - 60, ord(i) - 61))
