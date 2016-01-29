from .cube import Cube, ScrambleGenerator
from .turn import TurnSequence

from argparse import ArgumentParser, Namespace
from collections import namedtuple
from os.path import isfile
from queue import Queue
from sys import argv
from threading import Thread
from time import time


help_text = \
"""Term Cube Timer

After scrambles, type a command or just press enter to start inspection.
Once inspected, press enter again to start the solve. Hurry! Penalties apply.
Once solving, press enter again to end the solve.
If tags are enabled, enter your tags separated by space (not commas) or
type "del" to delete that solve.
Repeat.

Available commands:
-exit       - End this timer session (you will be able to export after)
-stat       - Display this session's statistics so far
-merge      - Rename one tag or merge multiple together
-export     - Export your times to a file
-del        - Delete a solve
-help       - Display this help text"""

def prompt_number(prompt = 'Enter a number: ', default = None, condition = None):
    """Print a given prompt string and return the user's input as a float.
    If invalid or no input, return a given default.
    """
    while True:
        print(prompt, end = '')
        usr = input()
        if usr:
            try:
                if not condition or condition(float(usr)):
                    return float(usr)
            except:
                continue
        elif default != None:
            return default

def prompt_int(prompt = 'Enter a number: ', default = None, condition = None):
    """Print a given prompt string and return the user's input as a float.
    If invalid or no input, return a given default.
    """
    while True:
        print(prompt, end = '')
        usr = input()
        if usr:
            try:
                if not condition or condition(int(usr)):
                    return int(usr)
            except:
                continue
        elif default != None:
            return default

class Solve(namedtuple('Solve', ['time', 'penalty', 'tags', 'scramble'])):
	def totaltime(self):
		if self.penalty == 'DNF':
			return self.time
		return self.time + self.penalty
	
	@staticmethod
	def formattime(time):
		return '%.2f' % time if time < 60 else '%d:%05.2f' % divmod(time, 60)
	
	def __str__(self):
		timestr = Solve.formattime(self.time)
		if self.penalty == 0:
			return timestr
		elif self.penalty == 2:
			return '%s (+2)' % timestr
		elif self.penalty == 'DNF':
			return '%s (DNF)' % timestr

def mean(arr):
    try:
        return sum(arr)/len(arr)
    except:
        return 0
    
def count_down(inspection = 15.0):
    """Count down a given number of seconds or until interrupted by
    the enter key, then return a penalty corresponding to the time past
    the allotted inspection time that the timer was stopped.

    Seconds over    Penalty
    0               0
    2               2
    >2              "DNF"
    """
    if inspection <= 0:
        return 0

    stop = []
    Thread(target = lambda stop : stop.append(input()), args=(stop,)).start()
    start = time()
    while not stop:
        if inspection > time() - start:
            print('%-3.2f  ' % (inspection - time() + start), end='\r')
        elif inspection + 2 > time() - start:
            print('%-5s' % '+2', end='\r')
        else:
            print('%-5s' % 'DNF', end='\r')

    dt = time() - start - inspection
    
    if dt <= 0:
        return 0
    elif dt <= 2:
        return 2
    else:
        return 'DNF'

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
        timestr = Solve.formattime(ret)
        print(timestr, end='\r')
    print('%-10s' % '\r')
    return ret

def stats(arr):
    tags = dict()
    for solve in arr:
        if solve.tags:
            for tag in solve.tags.split():
                if tag in tags:
                    tags[tag].append(solve.totaltime())
                else:
                    tags[tag] = [solve.totaltime()]

    for key in tags:
        tags[key] = mean(tags[key])

    return sum(e.totaltime() for e in arr)/len(arr), tags

def export_times(filename, ret):
    total, d = stats(ret)
    p = 'Average of %d: %.2f\n' % (len(ret), total)
    p += '\n'.join('%-10s %.2f' % (k, d[k]) for k in d)
    p += '\n'*4
    p += ('\n'.join(('Time: %.2f\t Tags: %s\t Scramble: %s' % (s.totaltime(), s.tags, s.scramble)) for s in ret))
    with open(filename, 'w' if isfile(filename) else 'a') as o:
        o.write(p)

def command(usr, solve_number, solves):
    if usr == 'exit':
        return solve_number - 1, solves
    elif usr.startswith('stat'):
        total, d = stats(solves)
        print('%-10s %.2f' % ('All', total))
        for k in d:
            print('%-10s %.2f' % (k, d[k]))
    elif usr.startswith('merge'):
        merge_tags, new_tag = '', ''
        while merge_tags == '':
            print('List of tag(s) to merge/rename: ')
            merge_tags = input().split()
        while new_tag == '':
            print('New tag name: ')
            new_tag = input()
        for solve in solves:
            for target in merge_tags:
                solve.tags = solve.tags.replace(target, new_tag)
            print('Success')
    elif usr.startswith('export'):
        print('Name of file to export to: ', end='')
        filename = input()
        export_times(filename, solves)
        print("Export successful")
    elif usr.startswith('del'):
        delete_index = prompt_int("Delete which scramble number? (default last): ", 
                                  default = solve_number-1, 
                                  condition = lambda n: 0 < n < solve_number)-1
        try:
            t = solves[delete_index]
            del solves[delete_index]
            print('Removed solve number %d: %s' % (delete_index+1, t))
            return -1
        except:
            print('Unable to remove solve %d' % (delete_index+1))
    else:
        print(help_text)

def prompt_tags():
    while True:
        print("Type your tag(s) or 'del' to forget this solve: ", end='')
        tags = input()
        if tags:
            return tags

def get_times(size = 3, inspection = 15, usingtags = False, random = True, length = -1):
    print('Initializing...')
    solves = []
    cube = Cube(size)
    solvenumber = 1
    with ScrambleGenerator(size, random, length) as scrambler:
        while True:
            cube.reset()
            cube.apply('x')
            scramble = next(scrambler)
            cube.apply(scramble)
            print('Solve %d' % solvenumber)
            print(cube)
            print(scramble, end=' ')
            
            usr = input()
            while usr:
                q = command(usr, solvenumber, solves)
                if q == -1:
                    solvenumber -= 1
                elif q is not None:
                    return q
                usr = input()
            
            penalty = count_down(inspection)
            time = count_up()
            tags = prompt_tags() if usingtags else None

            if tags == 'del':
                continue

            if penalty == 'DNF':
                print('DNF penalties are ignored')

            solvenumber += 1
            solves.append(Solve(time, penalty, tags, scramble))
            print()
    return solvenumber - 1, solves
