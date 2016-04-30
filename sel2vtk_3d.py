#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 sel2vtk_3d.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng. 
# 
# Date: Apr 30, 2016
#
# Purpose: Same as my sel2vtk.py, but made to work specifically for 3d
# *.slf files. TODO: merge the 3d version in the sel2vtk.py script by adding
# appropriate conditional flags
#
# Using: Python 2 or 3, Matplotlib, Numpy
#
# Example: python sel2vtk_3d.py -i results.slf -o results.vtk
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import numpy as np
from ppmodules.selafin_io_pp import *
from progressbar import ProgressBar, Bar, Percentage, ETA

if len(sys.argv) != 5:
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python sel2vtk.py -i results.slf -o results.vtk')
	sys.exit()

dummy1 = sys.argv[1]
input_file = sys.argv[2]
dummy2 = sys.argv[3]
output_file = sys.argv[4]

# we are going to have one file per time record in the slf file

# use selafin_io_pp class ppSELAFIN
slf = ppSELAFIN(input_file)
slf.readHeader()
slf.readTimes()

# get times of the selafin file, and the variable names
times = slf.getTimes()
variables = slf.getVarNames()

#print(times)
#print(variables)

# gets some of the mesh properties from the *.slf file
NELEM, NPOIN, NDP, IKLE, IPOBO, x, y = slf.getMesh()

# the IKLE array starts at element 1, but matplotlib needs it to start
# at zero
IKLE[:,:] = IKLE[:,:] - 1

# to accomodate code pasting
ikle = IKLE

# to create a list of files
file_out = list()

# initialize the counter
count = 0

# create a list of filenames based on time records in the slf file
filenames = list()
for i in range(len(times)):
	filenames.append(output_file.split('.',1)[0] + "{:0>5d}".format(i) + '.vtk')

# to create the multiple output files
for item in filenames:
	file_out.append(item)
	file_out.append(item)
	file_out[count] = open(item,'w')
	
	# item is the actual file name, which corresponds to each time step
	slf.readVariables(count)
	
	# these are the results for all variables, for time step count
	master_results = slf.getVarValues() 
	
	# vtk header file
	file_out[count].write('# vtk DataFile Version 3.0' + '\n')
	file_out[count].write('Created with pputils' + '\n')
	file_out[count].write('ASCII' + '\n')
	file_out[count].write('' + '\n')
	file_out[count].write('DATASET UNSTRUCTURED_GRID' + '\n')
	file_out[count].write('POINTS ' + str(len(x)) + ' float' + '\n')

	# to write the node coordinates
	# this assumes the first variable in the 3d *.slf file is the 'ELEVATION' or 'COTE'
	for i in range(len(x)):
		file_out[count].write(str("{:.3f}".format(x[i])) + ' ' + 
			str("{:.3f}".format(y[i])) + ' ' + str("{:.3f}".format(master_results[0][i])) + 
			'\n')
		
	# to write the node connectivity table                         for 3d this is 7
	file_out[count].write('CELLS ' + str(len(ikle)) + ' ' + str(len(ikle)*7) + '\n')

	for i in range(len(ikle)):
		# for 3d this is how it has to go
		file_out[count].write('6 ' + str(ikle[i][0]) + ' ' + str(ikle[i][1]) + ' ' + 
			str(ikle[i][2]) + ' '+  str(ikle[i][3]) + ' ' + str(ikle[i][4]) + ' ' + 
			str(ikle[i][5]) + '\n')
		
	# to write the cell types
	file_out[count].write('CELL_TYPES ' + str(len(ikle)) + '\n')
	for i in range(len(ikle)):
		file_out[count].write('13' + '\n')
	
	# write the empty line
	file_out[count].write('' + '\n')

	# write the data
	file_out[count].write('POINT_DATA ' + str(len(x)) + '\n')

	idx_written = list()
	idx_vel_u = -1000
	idx_vel_v = -1000
	idx_vel_z = -1000

	# from the list of variables, find v and u
	for i in range(len(variables)):
		if (variables[i].find('VELOCITY U') > -1):
			idx_vel_u = i
		elif (variables[i].find('VELOCITY V') > -1):
			idx_vel_v = i
		elif (variables[i].find('VELOCITY W') > -1):
			idx_vel_z = i
		
		# in case the variables are in french
		if (variables[i].find('VITESSE U') > -1):
			idx_vel_u = i
		elif (variables[i].find('VITESSE V') > -1):
			idx_vel_v = i
		elif (variables[i].find('VITESSE W') > -1):
			idx_vel_z = i
			
	if ( (idx_vel_u > -1000) and (idx_vel_v > -1000) ):
		#idx_written.append(idx_vel_u)
		#idx_written.append(idx_vel_v)
		# write velocity vectors data 
		file_out[count].write('VECTORS Velocity float' + '\n')
	
		for i in range(len(x)):
			file_out[count].write(str("{:.4f}".format(master_results[idx_vel_u][i])) + ' ' + 
				str("{:.4f}".format(master_results[idx_vel_v][i])) + ' ' + 
				str("{:.4f}".format(master_results[idx_vel_z][i])) + '\n')
			
	# write the rest of the variables
	for i in range(len(variables)):
		#if (i != idx_written[0]) and (i != idx_written[1]):
		file_out[count].write('SCALARS ' + variables[i].replace(' ', '_') + '\n')
		file_out[count].write('float' + '\n')
		file_out[count].write('LOOKUP_TABLE default' + '\n')
		for j in range(len(x)):
			file_out[count].write(str("{:.3f}".format(master_results[i][j])) + '\n')
	
	file_out[count].close()
	count = count + 1
