#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 sel2vtk.py                            # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng. 
# 
# Date: Oct 27, 2015
#
# Purpose: Script designed to convert *.slf file to *.vtk. As the old
# slf2vtk.f90 did, it writes a text based file for each time record.
# The script uses pure python to write files, which can be a bit slow
# for large models with many time steps. 
#
# So far, works only for 2D output files.
#
# Modified: Dec 17, 2015 
# Made to work on trimmed down version of HRW's selafin io utilities 
#
# Using: Python2.7.9, Matplotlib v1.4.2, Numpy v1.8.2
#
# Example: python sel2vtk.py -i results.slf -o results.vtk
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import numpy             as np
from ppmodules.selafin_io import *
from ppmodules.ProgressBar import *

def read_selafin():
	# Openning the selafin file
	# This gives the name of the variables, and their index number
	#
	slf = SELAFIN(input_file)
	# Getting coordinates
	x       = slf.MESHX
	y       = slf.MESHY
	# Getting Variables
	#print 'Variables in '+input_file+' are:'
	#for i in range(len(slf.VARNAMES)):
		#print '    ',i, '-->', slf.VARNAMES[i]
	
	#for i,name in enumerate(slf.VARNAMES):
	#	print '    ',i, ' - ',name
	# Get IKLE for mesh regularization
	ikle     = np.array(slf.IKLE2)
	
	# total number of variables in the input file
	numvars = len(slf.VARNAMES)
	
	# total number of time records in the file 
	nrecs = len(slf.tags["times"])
	
	# an array of size nrecs with values of time steps in the input file
	times = slf.tags["times"]
	#print "number of records in input file : " + str(nrecs)
	#print "Available time steps to choose from: "
	#for i in range(len(times)):
	#	print str(times[i])
	
	#
	return slf,x,y,ikle,numvars,nrecs,times

def get_var_names_and_units():
	# two empty lists
	variables = []
	units = []
	for var_names in slf.VARNAMES[0:numvars]:
		#print var_names
		variables.append(var_names)
	for unit_names in slf.VARUNITS[0:numvars]:
		units.append(unit_names)
	return variables, units

def get_values(t):
	VARIABLES = {} # do this as dictionary
	for i, n in enumerate(slf.VARNAMES[0:len(variables)]):
		#print "Reading ", n, " for time index ",t
		values = slf.getVALUES(t)
		VARIABLES[i] = values[i]
	return VARIABLES
	
def read_all_variables(t):
	var_out = [] # do this as a list
	# i is the counter, n is the item
	for i, n in enumerate(slf.VARNAMES[0:len(variables)]):
		#print "Reading ", n, " for time index ",t
		values = slf.getVALUES(t)
		var_out.append(values[i])
	return var_out

if len(sys.argv) != 5:
	print 'Wrong number of Arguments, stopping now...'
	print 'Usage:'
	print 'python sel2vtk.py -i results.slf -o results.vtk'
	sys.exit()

dummy1 = sys.argv[1]
input_file = sys.argv[2]
dummy2 = sys.argv[3]
output_file = sys.argv[4]

# we are going to have one file per time record in the slf file

# create the output file
#fout = open(output_file, "w")

# Read the header of the selafin result file and get geometry and
# variable names and units
slf,x,y,ikle,numvars,nrecs,times = read_selafin()
variables, units = get_var_names_and_units()

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
	master_results = read_all_variables(count)
	# vtk header file
	file_out[count].write('# vtk DataFile Version 3.0' + '\n')
	file_out[count].write('Created with pputils' + '\n')
	file_out[count].write('ASCII' + '\n')
	file_out[count].write('' + '\n')
	file_out[count].write('DATASET UNSTRUCTURED_GRID' + '\n')
	file_out[count].write('POINTS ' + str(len(x)) + ' float' + '\n')

	# to write the node coordinates
	for i in range(len(x)):
		file_out[count].write(str("{:.3f}".format(x[i])) + ' ' + 
			str("{:.3f}".format(y[i])) + ' ' + str("{:.3f}".format(0.0)) + 
			'\n')
		
	# to write the node connectivity table
	file_out[count].write('CELLS ' + str(len(ikle)) + ' ' + str(len(ikle)*4) + '\n')

	for i in range(len(ikle)):
		file_out[count].write('3 ' + str(ikle[i][0]) + ' ' + str(ikle[i][1]) + ' ' + 
			str(ikle[i][2]) + '\n')
		
	# to write the cell types
	file_out[count].write('CELL_TYPES ' + str(len(ikle)) + '\n')
	for i in range(len(ikle)):
		file_out[count].write('5' + '\n')
	
	# write the empty line
	file_out[count].write('' + '\n')

	# write the data
	file_out[count].write('POINT_DATA ' + str(len(x)) + '\n')

	idx_written = list()
	idx_vel_u = -1000
	idx_vel_v = -1000

	# from the list of variables, find v and u
	for i in range(len(variables)):
		if (variables[i].find('VELOCITY U') > -1):
			idx_vel_u = i
		elif (variables[i].find('VELOCITY V') > -1):
			idx_vel_v = i
		
		# in case the variables are in french
		if (variables[i].find('VITESSE U') > -1):
			idx_vel_u = i
		elif (variables[i].find('VITESSE V') > -1):
			idx_vel_v = i
			
	if ( (idx_vel_u > -1000) and (idx_vel_v > -1000) ):
		idx_written.append(idx_vel_u)
		idx_written.append(idx_vel_v)
		# write velocity vectors data 
		file_out[count].write('VECTORS Velocity float' + '\n')
	
		for i in range(len(x)):
			file_out[count].write(str("{:.4f}".format(master_results[idx_vel_u][i])) + ' ' + 
				str("{:.4f}".format(master_results[idx_vel_v][i])) + ' 0.0' + '\n')
			
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
	
