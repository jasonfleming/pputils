#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 remduplns.py                          # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Sept 2, 2015
#
# Modified: Feb 21, 2016
# Made it work for python 2 or 3
#
# Purpose: Script takes in a *.csv of the lines, and removes duplicate nodes
# from each line using OrderedDict from collections. Running this script
# automatically eliminates the last node from every closed line. This script
# ensures no zero length vertices in any one of the lines!
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python remduplns.py -i lines.csv -o lines_remdup.csv
# where:
# -i input lines file
# -o output lines file where duplicates are removed
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
	print('python remduplns.py -i lines.csv -o lines_remdup.csv')
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
id = nodes_data[0,:]
x = nodes_data[1,:]
y = nodes_data[2,:]
if (n_attr == 4):
	z = nodes_data[3,:]
else:
	z = np.zeros(len(x))
	
# crop all the points to three decimals only
id = id.astype(np.int32)
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

# previous and current line id
prev_id = mypoints[0][0]
cur_id = -999

# prints the lines with duplicate nodes removed
for i in range(n_rev):
	if (i == 1):
		cur_id = mypoints[i][0]
		prev_id = mypoints[i-1][0]
		if (cur_id == prev_id):
			fout.write(str(mypoints[0][0]) +',' + str(mypoints[0][1]) + ',' + str(mypoints[0][2]) + ',' + 
				str(mypoints[0][3]) + '\n')
			fout.write(str(mypoints[1][0]) +',' + str(mypoints[1][1]) + ',' + str(mypoints[1][2]) + ',' + 
				str(mypoints[1][3]) + '\n')	
	if (i > 1):
		cur_id = mypoints[i][0]
		prev_id = mypoints[i-1][0]
		if (cur_id == prev_id or cur_id == prev_id+1):
			fout.write(str(mypoints[i][0]) +',' + str(mypoints[i][1]) + ',' + str(mypoints[i][2]) + ',' + 
				str(mypoints[i][3]) + '\n')
