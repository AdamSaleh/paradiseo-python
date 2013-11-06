# -*- coding: utf-8 -*-
import logging

logging.basicConfig(filename='evolve.log',level=logging.DEBUG)

def nObjectives():
	return 2

def minimumBounds(i):
	return 0.0

def maximumBounds(i):
	return 5.0
def nParams():
	return 1

def report(inp,rep):
    print rep

#def popeval(pop):
#  return [[x[0]**2,(x[0]-2)**2] for x in pop]