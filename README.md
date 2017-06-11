# termcube
Termcube is a Rubik's cube timer and simulator that can simulate the 
Skewb and cubic twistypuzzles with arbitrary side lengths > 0. 

Or at least it was.

##I levelled everything!

Before a long hiatus from working on this project, I made a few commits
that broke a lot of things. Looking back, the project was so poorly made
that I feel like restructuring everything is a better idea. I will be
reorganizing code from the master repo into this repo with a few goals.

* Restructure the project to avoid spaghetti dependencies
* Move important classes out of out of __init__.py files
* Package this project properly so that it can be put on PyPI without shame

When I feel that I've reached these goals, I will pull all of the changes
into the master branch. In the meantime, neither really works too well.
So good luck with that.
