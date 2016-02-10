#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import time
import sys

from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from termcube import cube, skewb, simulator, TurnSequence 
from termcube.termusr import prompt_number, prompt_int, prompt_ln, timer
from termcube.scrambler import ScrambleGenerator

epilog_text = \
"""possible behaviours:
timer           - cube timer
simulator       - simulate a cube of any side length > 0
demo-kociemba   - random-state scramble then solve a cube with
                  Kociemba's two-phase algorithm, turn by turn
random-turns    - Start from solved, then apply random turns until solved
"""

parser = ArgumentParser(epilog = epilog_text, formatter_class = RawDescriptionHelpFormatter)

parser.add_argument('behaviour', nargs='?', default='timer', type=str,
            help='timer, simulator, demo-kociemba, random-turns')

parser.add_argument('puzzle', nargs='?', default='3', type=str,
            help="Puzzle type -- either 'skewb' or a cube side length (default 3)")

parser.add_argument('--inspection', '-i', default=15.0, type=float,
            help='The number of seconds to inspect (default 15)')

parser.add_argument('--unofficial', '-u', nargs='?', type=int, default=None, const=-1,
            help='Use a low CPU alternative to official style scrambles')

parser.add_argument('--nocurses', '-n', action='store_true',
            help='Low-dependency alternative to the usual display settings')

def prompt_args():
    print('1. Timer')
    print('2. Simulator Interactive Mode')
    print('3. Kociemba Two-Phase Algorithm demonstration')
    print('4. Random Turn Cube Demonstration')

    usr = prompt_int("Select and option by its number: ", condition=lambda n: 1 <= n <= 4)

    options = Namespace()

    if usr != 3:
        options.puzzle = prompt_ln("Puzzle type -- either 'skewb' or a cube side length (default 3): ")

    else:
        options.puzzle = cube.Cube(3)

    if usr == 1:
        options.behaviour = 'timer'
        options.inspection = prompt_number("Inspection time (default 15): ", 15.0)

        if hasattr(options.puzzle, 'random_scramble'):
            print('Use random state scrambles? This may lag on your computer. (default yes): ', end='')
            random = not input().startswith('n')

        if random:
            options.unofficial = None
        else:
            options.unofficial = prompt_int('How long should scrambles be? (default %d): '\
                    % turn.TurnSequence.default_moves(options.size),
                    default=-1)

    elif usr == 2:
        options.behaviour = 'simulator'
    elif usr == 3:
        options.behaviour = 'demo-kociemba'
    elif usr == 4:
        options.behaviour = 'random-turns'

    #Set defaults

    
    if usr == 1 or usr == 2:
        options.nocurses = not prompt_ln("Use curses? (y/n) (default yes): ", default='y').startswith('y')
    
    options.inspection = 15.0
    options.unofficial = -1
    return options

def main():
    print("Term Cube: Timer and Simulator")
    if len(sys.argv) <= 1:
        print("Run `termcube --help` to see how to skip these prompts")
        print()
        options = prompt_args()
    else:
        options = parser.parse_args()

    if options.puzzle.lower() == 'skewb':
        options.puzzle = skewb.Skewb()
    else:
        try:
            options.puzzle = cube.Cube(int(options.puzzle))
        except:
            print("Puzzle type %s not applicable. Exiting." % options.puzzle)
            sys.exit(0)
    
    """Regarding the value of options.unofficial:
    if using a random state scramble, options.unofficial is None
    if using a random turn scramble of default length, options.unofficial is -1
    if using a random turn scramble with a specific length, option.unofficial is that length
    """
    if options.behaviour == 'timer':
        timer(options.puzzle, 
              options.inspection, 
              random = options.unofficial == None,
              length = options.unofficial if options.unofficial else -1,
              nocurses = options.nocurses)
    elif options.behaviour == 'simulator':
        simulator.simulate(options.puzzle, options.nocurses)
    elif options.behaviour == 'demo-kociemba':
        print('Initializing...')
        with ScrambleGenerator(options.puzzle) as scrambler:
            while True:
                options.puzzle.apply(next(scrambler))
                print(options.puzzle)
                for t in TurnSequence(options.puzzle.solution()[0]):
                    options.puzzle.apply(t)
                    print(options.puzzle)
                    time.sleep(.1)
                time.sleep(1)
    elif options.behaviour == 'random-turns':
        while True:
            s = options.puzzle.random_turn()
            options.puzzle.apply(s)
            print(s)
            print(r)
            time.sleep(.5)
            if r.is_solved():
                break
        print('WOAH')
    else:
        parser.print_help()

if __name__=='__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
