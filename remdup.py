#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 remdup.py                             # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: July 23, 2015
#
# Updated: Feb 21, 2016
# Made it work under python 2 or 3
#
# Purpose: Script takes in a *.csv of the nodes, and removes duplicates
# using OrderedDict from collections.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python remdup.py -i nodes.csv -o nodes_remdup.csv
# where:
# -i input nodes file
# -o output nodes file where duplicates are removed
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import numpy as np
from collections import OrderedDict
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
# I/O
if len(sys.argv) != 5 :
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python remdup.py -i nodes.csv -o nodes_remdup.csv')
	sys.exit()
dummy1 =  sys.argv[1]
input_file = sys.argv[2]
dummy2 =  sys.argv[3]
output_file = sys.argv[4]

# find out if the nodes file is x,y,z or x,y,x,size
with open(input_file, 'r') as f:
  line = next(f) # read 1 line
  n_attr = len(line.split(','))
  
# to create the output file
fout = open(output_file,"w")

# use numpy to read the file
nodes_data = np.loadtxt(input_file, delimiter=',',skiprows=0,unpack=True)

# master nodes in the file (from the input file)
x = nodes_data[0,:]
y = nodes_data[1,:]
z = nodes_data[2,:]
if (n_attr == 4):
	size = nodes_data[3,:]
else:
	size = np.zeros(len(x))
	
# crop all the points to three decimals only
x = np.around(x,decimals=3)
y = np.around(y,decimals=3)
z = np.around(z,decimals=3)

n = len(x)

# this piece of code uses OrderedDict to remove duplicate nodes
# source "http://stackoverflow.com/questions/12698987"
# ###################################################################
tmp = OrderedDict()
for point in zip(x, y, z, size):
  tmp.setdefault(point[:2], point)

# in python 3 tmp.values() is a view object that needs to be 
# converted to a list
mypoints = list(tmp.values()) 
# ###################################################################

n_rev = len(mypoints)

# prints the nodes that have duplicates removed
for i in range(n_rev):
	fout.write(str(mypoints[i][0]) + ',' + str(mypoints[i][1]) + ',' + 
		str("{:.3f}".format(mypoints[i][2])) + '\n')
