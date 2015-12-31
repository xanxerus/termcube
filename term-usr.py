#!/usr/bin/python3
# -*- coding: utf-8 -*-

from time import time
from threading import Thread
from cube import Cube, ScrambleGenerator
from collections import namedtuple
from os.path import isfile
from queue import Queue

class Solve(namedtuple('Solve', ['time', 'penalty', 'tags', 'scramble'])):
	def totaltime(self):
		if self.penalty == 'DNF':
			return None
		else:
			return self.time + self.penalty

def mean(arr):
	return sum(arr)/len(arr)

def prompt_number(prompt = 'Enter a number: ', default = 15):
	"""Print a given prompt string and return the user's input as a float.
	If invalid or no input, return a given default.
	"""
	while True:
		print(prompt, end = '')
		usr = input()
		if usr:
			try:
				return float(usr)
			except:
				continue
		else:
			return float(default)

def count_down(inspection_time = 15.):
	"""Count down a given number of seconds or until interrupted by
	the enter key, then return a penalty corresponding to the time past 
	the allotted inspection time that the timer was stopped.
	
	Seconds over	Penalty
	0				0
	2 				2
	>2				"DNF"
	"""
	if inspection_time <= 0:
		return 0
	
	stop = []
	Thread(target=(lambda stop:stop.append(input())), args=(stop,)).start()
	start = time()
	while not stop:
		if inspection_time > time()-start:
			print('%-3.2f  ' % (inspection_time-time()+start), end='\r')
		elif inspection_time + 2 > time() - start:
			print('%-5s' % '+2', end='\r')
		else:
			print('%-5s' % 'DNF', end='\r')
	
	dt = time() - start - inspection_time
	
	return 0 if dt <= 0 else 2 if dt <= 2 else 'DNF'


def count_up():
	"""Start a timer counting up until interrupted with enter key.
	Return the time of the timer.
	"""
	stop = []
	Thread(target=(lambda stop:stop.append(input())), args=(stop,)).start()
	start = time()
	ret = 0
	while not stop:
		ret = time()-start
		print('%.2f    ' % ret, end='\r')
	print('%-10s' % '\r')
	return ret

def stats(arr):
	dic = {}
	for solve in arr:
		for tag in solve.tags.split():
			if tag in dic:
				dic[tag].append(solve.totaltime())
			else:
				dic[tag] = [solve.totaltime()]
	for k in dic:
		dic[k] = mean(dic[k])
	
	return sum(e.totaltime() for e in arr)/len(arr), dic

def export_times(filename, ret):
	p = ''
	total, d = stats(ret)
	p += ('%-10s %.2f' % ('All', total)) + '\n'
	for k in d:
		p += ('%-10s %.2f' % (k, d[k])) + '\n'
	p += ('\n'.join(('Time: %.2f\t Tags: %s\t Scramble: %s' % (s.totaltime(), s.tags, s.scramble)) for s in ret))
	with open(filename, 'w' if isfile(filename) else 'a') as o:
		o.write(p)

def avg_times(arr):
	"""Return the average of all times, applying penalties and throwing
	out DNFS. Also return the average removing best and worst after 
	applying penalites and throwing out DNFS.
	"""
	times = sorted([sum(a) for a in filter(lambda t : t[0] != 'DNF', arr)])
	l = len(times)
	return sum(times)/l if l > 0 else 0, sum(times[1:-1])/(l-2) if l > 2 else 0

def get_times(n=0, cube_size=3, inspection_time=15, using_tags=True, using_random_state=True):
	print('Initializing...')
	ret = []
	cube = Cube(cube_size)
	solve_number = 1
	with ScrambleGenerator(x=cube_size, random_state=using_random_state) as scrambler:
		while n <= 0 or solve_number <= n:
			cube.reset()
			cube.apply('x')
			scramble = next(scrambler)
			cube.apply(scramble)
			print('Solve %d' % solve_number)
			
			print(cube)
			print(scramble, end='')
			
			usr = input()
			while usr:
				if usr == 'end':
					return solve_number-1, ret 
				elif usr.startswith('stat'):
					total, d = stats(ret)
					print('%-10s %.2f' % ('All', total))
					for k in d:
						print('%-10s %.2f' % (k, d[k]))
				elif usr.startswith('export'):
					print('Name of file to export to: ', end='')
					filename = input()
					export_times(filename, ret)
					print("Export successful") 
				elif usr.startswith('del'):
					delete_index = prompt_number("Delete which scramble number? (default last): ", default=len(ret))-1
					try:
						t = ret[delete_index].totaltime()
						del ret[delete_index]
						print('Removed solve number %d: %.2f' % (delete_index, t))
					except:
						print('Unable to remove solve %d' % delete_index)
				usr = input()
			
			penalty = count_down(inspection_time)
			time = count_up()
			tags = ''
			
			while using_tags and not tags:
				print("Type your tag(s) or 'del' to forget this solve: ", end='')
				tags = input()
				if tags == 'del':
					break
				if not tags:
					continue
			else:
				solve_number += 1
				ret.append(Solve(time, penalty, tags, scramble))
				print()
	return solve_number-1, ret 

if __name__=='__main__':
	#Prompt session info
	inspection_time = prompt_number('Session inspection time (default 15s): ', 15.0)
	cube_size = int(prompt_number('Cube size (default 3): ', 3))
	print('Use tags? (default yes): ', end='')
	using_tags = not input().startswith('n')
	using_random_state = True
	if cube_size == 3:
		print('Use random state scrambles? This may lag on your computer. (default yes): ', end='')
		using_random_state = not input().startswith('n')
		
	#Main application
	get_times(cube_size=cube_size, inspection_time=inspection_time, using_tags=using_tags, using_random_state = using_random_state)

	#Exit
	print("Session has ended.")
	print("Statistics: ")
	total, d = stats(ret)
	print('%-10s %.2f' % ('All', total))
	for k in d:
		print('%-10s %.2f' % (k, d[k]))
