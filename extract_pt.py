#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 extract_pt.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: May 2, 2016
#
# Purpose: Script takes in a *.slf file, and x,y node coordinates, and
# extracts all values for that node, for all time steps in the file. Works
# equally well for *.slf 2d and 3d files.
#
# Revised: Jun 21, 2016
# Added a method in selafin_io_pp.py that significantly improves the 
# speed of data extraction at a single point.
#
# Uses: Python 2 or 3, Matplotlib, Numpy
#
# Example:
#
# python extract_pt.py -i in.slf -x 100.0 -y 200.0 -o out.txt
# where:
# -i input *.slf file
# -x, y coordinates of the node for which to extract data
# -o output text file
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
from scipy import spatial
import numpy as np
from ppmodules.selafin_io_pp import *
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 9 :
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python extract_pt.py -i in.slf -x 100.0 -y 200.0 -o out.txt')
	sys.exit()

input_file = sys.argv[2]
xu = float(sys.argv[4])
yu = float(sys.argv[6])
output_file = sys.argv[8]

# the output file
fout = open(output_file, 'w')

# reads the *.slf file
slf = ppSELAFIN(input_file)
slf.readHeader()
slf.readTimes()

# get times of the selafin file, and the variable names
times = slf.getTimes()
variables = slf.getVarNames()
units = slf.getVarUnits()

# number of variables
NVAR = len(variables)

# to remove duplicate spaces from variables and units
for i in range(NVAR):
	variables[i] = ' '.join(variables[i].split())
	units[i] = ' '.join(units[i].split())

# gets some of the mesh properties from the *.slf file
NELEM, NPOIN, NDP, IKLE, IPOBO, x, y = slf.getMesh()

# determine if the *.slf file is 2d or 3d by reading how many planes it has
NPLAN = slf.getNPLAN()

fout.write('The file has ' + str(NPLAN) + ' planes' + '\n')

# store just the x and y coords
x2d = x[0:len(x)/NPLAN]
y2d = y[0:len(x)/NPLAN]

# create a KDTree object
source = np.column_stack((x2d,y2d))
tree = spatial.KDTree(source)

# find the index of the node the user is seeking
d, idx = tree.query((xu,yu), k = 1)

# now we need this index for all planes
idx_all = np.zeros(NPLAN,dtype=np.int32)

# the first plane
idx_all[0] = idx

# start at second plane and go to the end
for i in range(1,NPLAN,1):
	idx_all[i] = idx_all[i-1] + (NPOIN / NPLAN)

# now we are ready to output the results
# to write the header of the output file
fout.write('TIME, ')
for i in range(NVAR):
	fout.write(variables[i] + ', ')
fout.write('\n')

fout.write('S, ')
for i in range(NVAR):
	fout.write(units[i] + ', ')
fout.write('\n')

########################################################################
# extract results for every plane (if there are multiple planes that is)
for p in range(NPLAN):
	slf.readVariablesAtNode(idx_all[p])
	results = slf.getVarValuesAtNode()

	# outputs the results
	for i in range(len(times)):
		fout.write(str("{:.3f}").format(times[i]) + ', ')
		for j in range(NVAR):
			fout.write(str("{:.4f}").format(results[i][j]) + ', ')
		fout.write('\n')
########################################################################


# below is what I had previously
# it has a more logical output for 3d files
# if wanting to rely on previous, uncomment between ### and replace with
# code below

'''
# read the results for all variables, for all times
for t in range(len(times)):
	# read variable
	slf.readVariables(t)
	
	# these are the results for all variables, for time step count
	master_results = slf.getVarValues() 
	
	# to store the extracted results in an array of its own
	extracted_results = np.zeros((NVAR,NPLAN))
	
	for i in range(NVAR):
		for j in range(len(idx_all)):
			extracted_results[i][j] = master_results[i][idx_all[j]]
	
	# transpose the extracted_results 
	extracted_results_tr = np.transpose(extracted_results)
	
	
	for i in range(NPLAN):
		fout.write(str("{:.3f}").format(times[t]) + ', ')
		for j in range(NVAR):
			fout.write(str("{:.4f}").format(extracted_results_tr[i][j]) + ', ')
		fout.write('\n')
'''

