#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from termcube import cube, simulator, termusr, turn

help_text=''

epilog_text = \
"""possible behaviours:
timer           - cube timer
simulator       - simulate a cube of any side length > 0
demo-kociemba   - random-state scramble then solve a cube with  
                  Kociemba's two-phase algorithm, turn by turn
random-turns    - Start from solved, then apply random turns until solved
"""

parser = ArgumentParser(epilog=epilog_text, formatter_class=RawDescriptionHelpFormatter)
parser.add_argument('behaviour', nargs='?', default='timer', type=str,
            help='timer, simulator, demo-kociemba, random-turns')

parser.add_argument('dimension', nargs='?', default=3, type=int,
            help='Cube side length (default 3)')

parser.add_argument('--inspection', '-i', default=15.0, type=float,
            help='The number of seconds to inspect (default 15)')

parser.add_argument('--unofficial', '-u', nargs='?', type=int, default=None, const=-1,
            help='Use a low CPU alternative to official style scrambles')

parser.add_argument('--using-tags', '-t', action='store_true',
            help='Apply tags after each solve to sort')

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

def prompt_args():
    print('1. Timer')
    print('2. Simulator Interactive Mode')
    print('3. Kociemba Two-Phase Algorithm demonstration')
    print('4. Random Turn Cube Demonstration')
    
    usr = prompt_int("Select and option by its number: ", condition=lambda n: 1 <= n <= 4)
    
    options = Namespace()
    if usr == 1:
        options.behaviour = 'timer'
        
        options.dimension = prompt_int("Cube size (default 3): ", 3, lambda n: n > 0)
        options.inspection = prompt_number("Inspection time (default 15): ", 15.0)
        print('Use tags? (default no): ', end='')
        options.using_tags = input().startswith('y')
        
        random = None
        if options.dimension == 3:
            print('Use random state scrambles? This may lag on your computer. (default yes): ', end='')
            random = not input().startswith('n')
        
        if random:
            options.unofficial = None
        else:
            options.unofficial = prompt_int('How long should scrambles be? (default %d): '\
                    % turn.TurnSequence.default_moves(options.dimension), 
                    default=-1)
        
        return options
    
    elif usr == 2:
        options.behaviour = 'simulator'
    elif usr == 3:
        options.behaviour = 'demo-kociemba'
    elif usr == 4:
        options.behaviour = 'random-turns'
    
    #Set defaults
    if usr != 3:
        options.dimension = prompt_int("Choose a cube size (default 3): ", default=3, condition=lambda n: n > 1)
    else:
        options.dimension = 3
    options.inspection = 15.0
    options.unofficial = -1
    options.using_tags = False
    return options

def timer(cube_size=3, inspection_time=15, using_tags=True, using_random_state=True, scramble_length=-1):
    #Main application
    solves, times = termusr.get_times(cube_size, 
                                       inspection_time, 
                                       using_tags, 
                                       using_random_state, 
                                       scramble_length)

    #Exit
    total, d = termusr.stats(times)
    print("Session has ended. Statistics:")
    statstring = 'Average of %d: %.2f\n' % (solves, total)
    statstring += '\n'.join('%-10s %.2f' % (k, d[k]) for k in d)
    print(statstring)
    print('Export your times to a file?')
    if input().startswith('y'):
        print('Name of file to export to: ', end='')
        filename = input()
        termusr.export_times(filename, times)
        print("Export successful")


if __name__=='__main__':
    print("Term Cube: Timer and Simulator")
    if len(sys.argv) <= 1:
        print("Run `termcube --help` to see how to skip these prompts")
        print()
        options = prompt_args()
    else:
        options = parser.parse_args()
    
    """Regarding the value of options.unofficial:
    if using a random state scramble, options.unofficial is None
    if using a random turn scramble of default length, options.unofficial is -1
    if using a random turn scramble with a specific length, option.unofficial is that length
    """
    if options.behaviour == 'timer':
        timer(options.dimension, 
              options.inspection, 
              options.using_tags, 
              using_random_state = options.unofficial == None, 
              scramble_length = options.unofficial if options.unofficial else -1)
    elif options.behaviour == 'simulator':
        simulator.simulate(options.dimension)
    elif options.behaviour == 'demo-kociemba':
        cube.demo_kociemba();
    elif options.behaviour == 'random-turns':
        cube.demo_random_turns(options.dimension)
    else:
        parser.print_help()
