'''
##termusr.py
This module contains timer functions. By default it generates random state
3x3x3 scrambles, prints what a cube would look like after applying the 
scramble, counts down until inspections is stopped, then counts up until
stopped, and repeats until stopped.

It supports rudimentary exports to files, deleting times, adding penalties,
and also tagging a solve at the end of solve time so that each time can 
be sorted by attributes that interest the user.
'''

from .cube import Cube
from .scrambler import ScrambleGenerator
from .simulator import Simulator, addcenter
from . import TurnSequence

from os.path import isfile
from sys import exit
from threading import Thread
from time import time

try:
    import curses
    nocurses = False
except ImportError:
    nocurses = True

###General timer functions

def formattime(time):
    if time == None:
        return None
    return '%.2f' % time if time < 60 else '%d:%05.2f' % divmod(time, 60)

def solvesmean(arr):
    """Return the mean of all solves. 0 if no solves given"""
    try:
        return sum(s.totaltime() for s in arr)/len(arr)
    except:
        return 0

def avg5(arr):
    """Return the average of the last five solves removing best and worst.
    If fewer than five solves, return the mean of those.
    If no solves given, return 0
    """
    if len(arr) <= 0:
        return 0
    elif len(arr) < 5:
        return sum(s.totaltime() for s in arr)/len(arr)
    else:
        return sum(s.totaltime() for s in arr[-5::])/5

def tagsort(arr):
    tags = dict()
    for solve in arr:
        for tag in solve.tags.split():
            if tag in tags:
                tags[tag].append(solve)
            else:
                tags[tag] = [solve]
    return tags

def stats(arr):
    best = worst = tagavg = curravg5 = bestavg5 = None
    solvenumber = 1
    
    sum = 0
    for solve in arr:
        time = solve.totaltime()
        sum += time
        if best is None or time < best:
            best = time
        if worst is None or time > worst:
            worst = time
        if solvenumber >= 5:
            curravg5 = avg5(arr[:solvenumber])
            if bestavg5 is None or curravg5 < bestavg5:
                bestavg5 = curravg5
        solvenumber += 1
    if solvenumber > 1:
        tagavg = sum/(solvenumber-1)

    return solvenumber, best, worst, tagavg, curravg5, bestavg5

def exporttimes(filename, solves):
    p = ''
    
    tags = tagsort(solves)
    
    for tag in ['All'] + list(tags):
        solvenumber, best, worst, tagavg, curravg5, bestavg5 =\
            stats(tags[tag] if tag != 'All' else solves)
        
        if tag != 'All':
            p += 'Solves with the tag: #' + tag.replace('#', '') + '\n'
        else:
            p += 'Statistics for all solves:' + '\n'
        p += "Average of %d: %.2f" % (solvenumber-1, tagavg) + '\n'
        p += "Best : %s" % formattime(best) + '\n'
        p += "Worst : %s" % formattime(worst) + '\n'
        p += "Current Avg 5 : %s" % formattime(curravg5) + '\n'
        p += "Best Avg 5 : %s" % formattime(bestavg5) + '\n'
        p += '\n' 
        p += '\n'.join(map(repr, tags[tag] if tag != 'All' else solves))
        p += '\n'*3
    
    p += "All solves: \n" + '\n'.join(map(repr, solves)) + '\n'
    with open(filename, 'w' if isfile(filename) else 'a') as o:
        o.write(p)

###CLI functions

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

def prompt_ln(prompt = "Apply which tag(s)?: ", default = None, condition = None):
    while True:
        print(prompt, end='')
        usr = input()
        if usr:
            try:
                if not condition or condition(usr):
                    return usr
            except:
                continue
        elif default != None:
            return default

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
        timestr = formattime(self.time)
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

class CLITimer:
    help_text = \
"""Term Cube Timer

After scrambles, type a command or just press enter to start inspection.
Once inspected, press enter again to start the solve. Hurry! Penalties apply.
Once solving, press enter again to end the solve.
If tags are enabled, enter your tags separated by space (not commas) or
type "del" to delete that solve.
Repeat.

Available commands:
#tagname    - Tag the previous solve with the given tagname
-exit       - End this timer session (you will be able to export after)
-stat       - Display this session's statistics so far
-merge      - Rename one tag or merge multiple together
-export     - Export your times to a file
-del        - Delete a solve
-help       - Display this help text"""

    def __init__(self, puzzle = None, inspection = 15, random = True, length = -1):
        self.puzzle = puzzle if puzzle else Cube(3)
        self.inspection = inspection
        self.random = random
        self.length = length
        
        self.solves = []
        self.solvenumber = 1

    @staticmethod
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

    @staticmethod
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
            timestr = '%-10s' % formattime(ret)
            print(timestr, end='\r')
        print('%-10s' % '\r')
        return ret

    def command(self, command):
        if command == 'exit':
            exit(0)
        elif command.startswith("#"):
            try:
                if self.solves[-1].tags:
                    self.solves[-1].tags += ' ' + command[1:]
                else:
                    self.solves[-1].tags = command[1:]
            except:
                print('Tag failed')
        elif command.startswith('stat'):
            print('%-10s: Average of %d: %.2f' % ('All', self.solvenumber-1, solvesmean(self.solves)))
            d = tagsort(self.solves)
            for k in d:
                print('#%-9s: Average of %d: %.2f' % (k, len(d[k]), solvesmean(d[k])))
        elif command.startswith('merge'):
            mergetags, newtag = '', ''
            while mergetags == '':
                print('List of tag(s) to merge/rename: ')
                mergetags = input().replace('#', ' ').split()
            while newtag == '':
                print('New tag name: ')
                newtag = input()
            for solve in self.solves:
                for target in mergetags:
                    solve.tags = solve.tags.replace(target, newtag)
            print('Success')
        elif command.startswith('export'):
            print('Name of file to export to: ', end='')
            exporttimes(input(), self.solves)
            print("Export successful")
        elif command.startswith('del'):
            index = prompt_int("Delete which scramble number? (default last): ",
                                        default = self.solvenumber-1,
                                        condition = lambda n: 0 < n < self.solvenumber)-1
            try:
                t = self.solves[index]
                del self.solves[index]
                self.solvenumber -= 1
                print('Removed solve number %d: %s' % (index+1, t))
            except:
                print('Unable to remove solve %d' % (index+1))
        else:
            print(CLITimer.help_text)

    def __call__(self):
        print('Initializing...')
        with ScrambleGenerator(self.puzzle, self.random, self.length) as scrambler:
            while True:
                self.puzzle.reset()
                self.puzzle.apply('x')
                scramble = next(scrambler)
                self.puzzle.apply(scramble)
                print('Solve %d' % self.solvenumber)
                print(self.puzzle)
                print(scramble, end=' ')

                usr = input()
                while usr:
                    self.command(usr)
                    usr = input()

                penalty = CLITimer.count_down(self.inspection)
                time = CLITimer.count_up()

                if penalty == 'DNF':
                    print('DNF penalties are ignored')

                self.solvenumber += 1
                self.solves.append(Solve(time, penalty, scramble))
                print()
        return self.solves

class CursesTimer(Simulator):
    help_text = \
"""Term Cube CursesTimer (Curses implementation)

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

    def __init__(self, puzzle, inspection = 15, random = True, length = None):
        super(CursesTimer, self).__init__(puzzle)
        self.inspection = inspection
        self.random = random
        self.length = length if not random else None
        self.solvenumber = 1
        self.best = self.worst = self.sessionavg = self.curravg5 = self.bestavg5 = None
        self.solves = []

    def __call__(self, scr, nocurses = False):
        self.initialize(scr)
        
        if nocurses:
            return CLITimer(self.puzzle, self.inspection, self.random, self.length).__call__(nocurses)

        with ScrambleGenerator(self.puzzle, self.random, self.length) as scrambler:
            addcenter(self.q, 'Term Cube Timer -- Press any key to start')
            addcenter(self.r, 'Confused? Try typing ":help"')
            self.q.nodelay(0)
            self.q.getch()
            self.q.nodelay(1)
            self.q.clear()
            addcenter(self.q, "Initializing...")
            self.q.refresh()
            while True:
                #Print statistics
                self.printstats(self.r)

                #Scramble
                self.puzzle.reset()
                self.puzzle.apply('x')
                scramble = next(scrambler)
                self.puzzle.apply(scramble)

                #Print Cube and Scramble
                self.printpuzzle(self.w)
                self.w.refresh()
                addcenter(self.q, scramble)

                #Throw out key presses during scramble wait
                self.q.nodelay(1)
                while self.q.getch() >= 0:
                    pass
                self.q.nodelay(0)

                #Command
                usr = chr(self.q.getch())
                while usr in ":#":
                    addcenter(self.q, usr, startx = 0) 
                    line = CursesTimer.getln(self.q)
                    
                    self.command(self.q, usr + line)
                    addcenter(self.q, scramble)
                    usr = chr(self.q.getch())

                self.q.nodelay(1)

                #Inspect
                if self.inspection > 0:
                    penalty = self.countdown(self.q, self.inspection)
                else:
                    penalty = 0

                #Solve
                time = self.countup(self.q)
                self.solves.append(Solve(time, penalty, scramble))
                self.q.getch()
                
                if time < 0:
                    addcenter(self.q, 'Time deleted')
                    self.q.nodelay(0)
                    self.q.getch()
                    self.q.nodelay(1)
                    continue
                
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
                    self.curravg5 = avg5(self.solves)
                    if self.bestavg5 == None or self.curravg5 < self.bestavg5:
                        self.bestavg5 = self.curravg5
                self.solvenumber += 1

                #Print solve times
                self.printtimes(self.e)

    def printstats(self, scr):
        stats = ["Solve number : %d" % self.solvenumber,
                 "Best : %s" % formattime(self.best),
                 "Worst : %s" % formattime(self.worst),
                 "Session Avg : %s" % formattime(self.sessionavg),
                 "Current Avg 5 : %s" % formattime(self.curravg5),
                 "Best Avg 5 : %s" % formattime(self.bestavg5)]
        scr.clear()
        maxy, maxx = scr.getmaxyx()
        for i in range(min(len(stats), maxy)):
            addcenter(scr, stats[i], starty = i, clear = False)
        scr.refresh()

    def printtimes(self, scr):
        self.e.clear()
        for i in range(min(self.solvenumber - 1, self.e.getmaxyx()[0])):
            timestr = 'Solve %d: %s' % (self.solvenumber-i-1 , self.solves[-i-1])
            addcenter(self.e, timestr, starty = i, clear = False)
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
                self.curravg5 = avg5(self.solves[:solvenumber])
                if self.bestavg5 is None or self.curravg5 < self.bestavg5:
                    self.bestavg5 = self.curravg5
            self.solvenumber += 1
        if self.solvenumber > 1:
            self.sessionavg = sum/(self.solvenumber-1)

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
                addcenter(scr, 'Tag failed')
                scr.getch()
        elif command.startswith(':del'):
            addcenter(scr, 'Delete which solve? (default last): ', startx = 0)
            index = CursesTimer.getln(scr)
            try:
                index = int(index) if index else self.solvenumber - 1
                t = self.solves[index - 1]
                del self.solves[index - 1]
                self.solvenumber -= 1
                addcenter(scr, 'Removed solve number %d: %s' % (index, t))
                self.recalculate()
                self.printstats(self.r)
                self.printtimes(self.e)
                scr.getch()
            except Exception as e:
                addcenter(scr, '%s %s' % (e, index))
                scr.getch()
        elif command.startswith(':merge'):
            mergetags, newtag = '', ''
            while mergetags == '':
                addcenter(scr, 'List of tag(s) to merge/rename: ', startx = 0)
                mergetags = CursesTimer.getln(scr)
            while newtag == '':
                addcenter(scr, 'New tag name: ', startx = 0)
                newtag = CursesTimer.getln(scr)
            for solve in self.solves:
                for target in mergetags:
                    solve.tags = solve.tags.replace(target, newtag)
                addcenter(scr, 'Success')
                scr.getch()
        elif command.startswith(':export'):
            addcenter(scr, 'Name of file to export to: ', startx = 0)
            exporttimes(CursesTimer.getln(scr), self.solves)
            addcenter(scr, 'Export successful')
            scr.getch()
        else:
            self.cornerandwait(self.scr, self.help_text)
            self.refresh()
    
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
            s = formattime(total)
            scr.addstr(maxqy//2 - 1, (maxqx - len(s))//2, s)
            scr.refresh()
            c = scr.getch()
            curses.napms(10)

        return time() - start

    def initialize(self, scr):
        super(CursesTimer, self).initialize(scr)
        
        if not curses.has_colors():
            global nocurses
            nocurses = True
            return
        
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
        self.e = curses.newwin(maxy - height - 10, maxx//2, height + 8, maxx//2)
        self.r = curses.newwin(8, maxx//2, height, maxx//2)
        self.printpuzzle(self.w)
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

#Main timer function
def timer(puzzle = None, inspection = 15, random = True, length = -1, nocurses = False):
    puzzle = puzzle if puzzle else Cube(3)
    #Main application
    if nocurses:
        solves = CLITimer(puzzle, inspection, random, length).__call__()
    else:
        solves = curses.wrapper(CursesTimer(puzzle, inspection, random, length))

    #Exit
    print("Session has ended.")
    if solves != 0:
        print('Export your times to a file?')
        if input().startswith('y'):
            print('Name of file to export to: ', end='')
            filename = input()
            termusr.export_times(filename, times)
            print("Export successful")

