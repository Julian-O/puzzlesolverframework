#!/usr/bin/env python

from distutils.core import setup

setup(
    name='Puzzle Solver Framework',
    version='3.0',
    description='Private Puzzle Solving Framework',
    author='Julian O.',
    author_email='puzzlesolvingframework@somethinkodd.com',
    #url='https://',
    py_modules=['gameframework', 'gameobjects', 'gameboard', 'commanddispatcher', 'views']
    )
