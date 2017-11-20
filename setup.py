#! /usr/bin/python3

from setuptools import setup

setup(
    name = 'ensemble',
    version = '0.1.0',
    license = 'MIT',
    author="Daniel Filonik",
    author_email = 'daniel.filonik@qut.edu.au',
    description = 'High-level framework for distributed OpenGL rendering.',
    url = 'http://github.com/filonik/ensemble',
    packages = [
        'ensemble',
        'ensemble.mathematics',
    ],
)