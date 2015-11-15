#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 sel2avtk.py                           # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng. 
# 
# Date: Oct 27, 2015
#
# Purpose: Script designed to convert *.slf file to *.vtk
#
# Using: Python2.7.9, Matplotlib v1.4.2, Numpy v1.8.2
#
# Example: python sel2vtk.py -i results.slf -o results.vtk
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                                 # system parameters
from os import path
import matplotlib.tri    as mtri           # matplotlib triangulations
import numpy             as np             # numpy
from numpy import linspace, dtype          # Writing netcdf files
import math # for the ceil function
#from math import sqrt, pi, sin, cos, tan, atan2 as arctan2  # math objects for coord trans
# Importing pytel tools for SELAFIN parser
pytel = os.getcwd()
#pytel = '/home/user/opentelemac/v7p0r1/scripts/python27/'
sys.path.append(path.join(path.dirname(sys.argv[0]),pytel))
from parsers.parserSELAFIN import SELAFIN  
#
#
#{{{
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def read_selafin():
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	# Openning the selafin file
	# This gives the name of the variables, and their index number
	#
	slf = SELAFIN(input_file)
	# Getting coordinates
	x       = slf.MESHX
	y       = slf.MESHY
	# Getting Variables
	print 'Variables in '+input_file+' are:'
	for i in range(len(slf.VARNAMES)):
		print '    ',i, '-->', slf.VARNAMES[i]
	
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
	print "number of records in input file : " + str(nrecs)
	#print "Available time steps to choose from: "
	#for i in range(len(times)):
	#	print str(times[i])
	
	#
	return slf,x,y,ikle,numvars,nrecs,times
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# End of the Function
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def get_var_names_and_units():
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	# two empty lists
	variables = []
	units = []
	for var_names in slf.VARNAMES[0:numvars]:
		#print var_names
		variables.append(var_names)
	for unit_names in slf.VARUNITS[0:numvars]:
		units.append(unit_names)
	return variables, units
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# End of the Function
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
#
def get_values(t):
	VARIABLES = {} # do this as dictionary
	for i, n in enumerate(slf.VARNAMES[0:len(variables)]):
		print "Reading ", n, " for time index ",t
		values = slf.getVALUES(t)
		VARIABLES[i] = values[i]
	return VARIABLES
	
def read_all_variables(t):
	var_out = [] # do this as a list
	# i is the counter, n is the item
	for i, n in enumerate(slf.VARNAMES[0:len(variables)]):
		print "Reading ", n, " for time index ",t
		values = slf.getVALUES(t)
		var_out.append(values[i])
	return var_out
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# End of the Function
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#}}}
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MAIN
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
if len(sys.argv) != 5:
	print 'Wrong number of Arguments, stopping now...'
	print 'Usage:'
	print 'python sel2vtk.py -i results.slf -o results.vtk'
	sys.exit()
# I/O

dummy1 = sys.argv[1]
input_file = sys.argv[2]
dummy2 = sys.argv[3]
output_file = sys.argv[4]

# create the output file
fout = open(output_file, "w")
#
# Read the header of the selafin result file and get geometry and
# variable names and units
slf,x,y,ikle,numvars,nrecs,times = read_selafin()
variables, units = get_var_names_and_units()

# reads all variables for time desired
master_results = read_all_variables(1)

# to write the vtk file for one variable

# vtk header file
fout.write('# vtk DataFile Version 3.0' + '\n')
fout.write('Created with pputils' + '\n')
fout.write('ASCII' + '\n')
fout.write('' + '\n')
fout.write('DATASET UNSTRUCTURED_GRID' + '\n')
fout.write('POINTS ' + str(len(x)) + ' float' + '\n')

# to write the node coordinates
for i in range(len(x)):
	fout.write(str("{:.3f}".format(x[i])) + ' ' + 
		str("{:.3f}".format(y[i])) + ' ' + str("{:.3f}".format(0.0)) + 
		'\n')
		
# to write the node connectivity table
fout.write('CELLS ' + str(len(ikle)) + ' ' + str(len(ikle)*4) + '\n')

for i in range(len(ikle)):
	fout.write('3 ' + str(ikle[i][0]) + ' ' + str(ikle[i][1]) + ' ' + 
		str(ikle[i][2]) + '\n')
		
# to write the cell types
fout.write('CELL_TYPES ' + str(len(ikle)) + '\n')
for i in range(len(ikle)):
	fout.write('5' + '\n')
	
# write the empty line
fout.write('' + '\n')

# write the data
fout.write('POINT_DATA ' + str(len(x)) + '\n')

idx_written = list()
idx_vel_u = -1000
idx_vel_v = -1000

# from the list of variables, find v and u
for i in range(len(variables)):
	if (variables[i].find('VELOCITY U') > -1):
		idx_vel_u = i
	elif (variables[i].find('VELOCITY V') > -1):
		idx_vel_v = i

if ( (idx_vel_u > -1000) and (idx_vel_v > -1000) ):
	idx_written.append(idx_vel_u)
	idx_written.append(idx_vel_v)
	# write velocity vectors data 
	fout.write('VECTORS Velocity float' + '\n')
	
	for i in range(len(x)):
		fout.write(str(master_results[idx_vel_u][i]) + ' ' + 
			str(master_results[idx_vel_v][i]) + ' 0.0' + '\n')
			
# write the rest of the variables
for i in range(len(variables)):
	if (i != idx_written[0]) and (i != idx_written[1]):
		fout.write('SCALARS ' + variables[i].replace(' ', '_') + '\n')
		fout.write('float' + '\n')
		fout.write('LOOKUP_TABLE default' + '\n')
		for j in range(len(x)):
			fout.write(str(master_results[i][j]) + '\n')
		
	
	
			






