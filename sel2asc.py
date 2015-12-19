#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 sel2asc.py                           # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng. 
# 
# Date: May 27, 2015
#
# Purpose: Script designed to open 2D telemac binary file, read the
# the desired output to an ESRI *.asc file for use in displaying within a
# GIS environment
# 
# Script based on sel2ncdf.py by Caio Eadi Stringari, and 
# sel2ncdf_2014-09-12-2.py by Alex Goater.
#
# Using: Python2.7.9, Matplotlib v1.4.2, Numpy v1.8.2
#
# Example: python sel2asc.py -i input.slf -v 4 -t 0 -s 2.0 -o output.asc
# 
# where:
#       --> -i is the *.slf file from which to extract data
#
#       --> -v is the index of the variable to extract; see probe.py for 
#                        index codes of the variables
#
#       --> -t is the index of the time step to extract; see probl.py for
#                        index codes of the time steps
#
#       --> -o is the *.asc output file
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
from os import path
import matplotlib.tri    as mtri           # matplotlib triangulations
import numpy             as np             # numpy
from numpy import linspace, dtype          
import math                                # for the ceil function
from ppmodules.selafin_io import *
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
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def tri2reg(triang,xi,yi,z,method,t,var):
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	# Interpolator
	if method == 'Linear':
		interpolator = mtri.LinearTriInterpolator(triang, z)
	elif method == 'Min_E':
		interpolator = mtri.CubicTriInterpolator(triang, z, kind='min_E')
	elif method == 'Geom':
		interpolator = mtri.CubicTriInterpolator(triang, z, kind='geom')
	else:
		'Could not find the desired method, stopping now...'
		sys.exit()
	# Interpolation
	zi = interpolator(xi, yi)
	print 'Interpolation of '+var+' completed for timestep ',t
	# Return interpolated object
	return zi
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# End of the Function
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
#}}}
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MAIN
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
if len(sys.argv) != 11:
	print 'Wrong number of Arguments, stopping now...'
	print 'Usage:'
	print 'python sel2asc.py -i input.slf -v 4 -t 0 -s 2.0 -o output.asc'
	sys.exit()
# I/O

input_file = sys.argv[2]         # input *.slf file
var_index  = int(sys.argv[4])    # index number of grided output variable 
t = int(sys.argv[6])             # index of time record of the output to use in griding (integer, 0 to n)                                  
spacing = float(sys.argv[8])     # specified the grid spacing of the output file
output_file = sys.argv[10]        # output *.asc grid file


# create the output file
fout = open(output_file, "w")
#
# Read the header of the selafin result file and get geometry and
# variable names and units
slf,x,y,ikle,numvars,nrecs,times = read_selafin()
variables, units = get_var_names_and_units()
#res = get_values(0)

# reads all variables for time desired (in the case below, it is t=0)
master_results = read_all_variables(t)

# creates a triangulation grid using matplotlib function Triangulation
triang = mtri.Triangulation(x, y, ikle)

# determine the spacing of the regular grid
range_in_x = x.max() - x.min()
range_in_y = y.max() - y.min()

max_range = max(range_in_x, range_in_y)

# first index is integer divider, second is remainder
num_x_pts = divmod(range_in_x, spacing)
num_y_pts = divmod(range_in_y, spacing)

print "Size of output matrix is : " + str(int(num_x_pts[0])) + " x " + str(int(num_y_pts[0]))
print "Grid resolution is : " + str(spacing) + " m"

# creates the regular grid
xreg, yreg = np.meshgrid(np.linspace(x.min(), x.max(), int(num_x_pts[0])),
	np.linspace(y.min(), y.max(), int(num_y_pts[0])))
x_regs = xreg[1,:]
y_regs = yreg[:,1]

# to interpolate to a reg grid
z =  tri2reg(triang,xreg,yreg,master_results[var_index],'Linear',0,"Output")

print "Shape of array z: " + str(z.shape[0])

print "Shape of arrays xreg and yreg: " + str(x_regs.shape) + " " + str(y_regs.shape) 

where_are_NaNs = np.isnan(z)
z[where_are_NaNs] = -999.0

#np.savetxt("temp.out", z, fmt='%.2f', delimiter='') # this has no max spaces
np.savetxt('temp.out', np.flipud(z), fmt='%10.3f', delimiter='') # this has 10 char spaces, 2 after decimal

# open the output *.asc file, and write the header info
fout.write("NCOLS " + str(z.shape[1]) + "\n")
fout.write("NROWS " + str(z.shape[0]) + "\n")
fout.write("XLLCORNER " + str(x_regs[0]) + "\n")
fout.write("YLLCORNER " + str(y_regs[0]) + "\n")
fout.write("CELLSIZE " + str(spacing) + "\n")
fout.write("NODATA_VALUE " + str(-999.00) + "\n")

# read the file, and write every line in fout
with open("temp.out") as fp:
	for line in fp:
		fout.write(line);
# remove the temp file
print "Removing temporary files ..."
os.remove("temp.out")
print "Done"
#
# Program completed
#print 'Output written to: ',output_file
#print 'Program completed.'

