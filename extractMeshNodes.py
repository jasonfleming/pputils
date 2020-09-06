#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 extractMeshNodes.py                   # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: December 1, 2015
#
# Modified: Feb 20, 2016
# Made it work for python 2 and 3
#
# Purpose: Script takes in a an ADCIRC mesh and extracts the nodes as
# a *.txt file.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python extractMeshNodes.py -i out.grd -o nodes.txt
# where:
# -i mesh in ADCIRC format
# -o nodes file (x,y,z)
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sys
import numpy             as np             # numpy
from ppmodules.readMesh import *           # to get all readMesh functions
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
#
# I/O
if len(sys.argv) != 5 :
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python extractMeshNodes.py -i out.grd -o nodes.txt')
	sys.exit()

dummy1 =  sys.argv[1]
input_file = sys.argv[2]
dummy2 =  sys.argv[3]
output_file = sys.argv[4]

# read the adcirc mesh file
n,e,x,y,z,ikle = readAdcirc(input_file)

fout = open(output_file, "w")

# writes the nodes
for i in range(n):
	fout.write(str("{:.3f}".format(x[i])) + " " + 
		str("{:.3f}".format(y[i])) + "\n")
'''		
for i in range(n):
	fout.write(str("{:.3f}".format(x[i])) + " " + 
		str("{:.3f}".format(y[i])) + " " + 
		str("{:.3f}".format(z[i])) + "\n")
'''



