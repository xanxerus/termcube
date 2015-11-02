#!/usr/bin/python3
# -*- coding: utf-8 -*-

from time import time
from threading import Thread
from cube import Cube

def prompt_inspection(default = 15, prompt = 'Session inspection time (default 15s): '):
	"""Print a given prompt string and return the user's input as a float.
	If invalid or no input, return a given default.
	"""
	print(prompt, end = '')
	try:
		return float(input())
	except:
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

def get_times(n = 0, cube_size = 3, inspection_time = 15):
	"""Provide a scramble, inspect for a given time, then count up until
	stopped. Loop n times or until stopped by typing "end".
	Return a list of all the times.
	"""
	ret = []
	x = 0
	r = Cube(cube_size)
	
	while n <= 0 or x <= n:
		print('Solve %d - Current mean: %.2f  Current wca average: %.2f' % ((x+1,) + avg_times(ret)))
		
		r.reset()
		r.apply("x")
		print(r.scramble())
		print(r, end='')
		
		usr = input()
		while usr:
			if usr == 'end':
				break
			elif usr.startswith('del'):
				try:
					q = int(usr.split()[1])
				except:
					q = x-1
				try:
					print('Removing solve number %d: %.2f' % (q, ret[q][1]))
					arr[q] = str(arr[q]) + ' - Removed'
				except:
					print('Unable to delete solve number %d' % q)
		
		if usr=='end':
			break
		
		penalty = count_down(inspection_time)
		time = count_up()
		ret.append((penalty, time))
		x+=1

def avg_times(arr):
	"""Return the average of all times, applying penalties and throwing
	out DNFS. Also return the average removing best and worst after 
	applying penalites and throwing out DNFS.
	"""
	print(arr)
	times = sorted([sum(a) for a in filter(lambda t : t[0] == 'DNF', arr)])
	l = len(times)
	return sum(times)/l if l > 0 else 0, sum(times[1:-1])/(l-2) if l > 2 else 0

if __name__=='__main__':
	get_times(inspection_time=prompt_inspection())
