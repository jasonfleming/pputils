#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 sel2asc.py                            # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng. 
# 
# Date: May 27, 2015
#
# Modified: Feb 21, 2016
# Made it work under python 2 or 3
#
# Purpose: Script designed to open 2D telemac binary file, read the
# the desired output to an ESRI *.asc file for use in displaying within a
# GIS environment
# 
# Script based on sel2ncdf.py by Caio Eadi Stringari, and 
# sel2ncdf_2014-09-12-2.py by Alex Goater.
#
# Using: Python 2 or 3, Matplotlib, Numpy
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
import os,sys
import matplotlib.tri as mtri
import numpy as np
from numpy import linspace, dtype          
from ppmodules.selafin_io_pp import *
#
if len(sys.argv) != 11:
	print('Wrong number of arguments, stopping now...')
	print('Usage:')
	print('python sel2asc.py -i input.slf -v 4 -t 0 -s 2.0 -o output.asc')
	sys.exit()

input_file = sys.argv[2]         # input *.slf file
var_index  = int(sys.argv[4])    # index number of grided output variable 
t = int(sys.argv[6])             # index of time record of the output to use in griding (integer, 0 to n)                                  
spacing = float(sys.argv[8])     # specified the grid spacing of the output file
output_file = sys.argv[10]       # output *.asc grid file

# Read the header of the selafin result file and get geometry and
# variable names and units

# use selafin_io_pp class ppSELAFIN
slf = ppSELAFIN(input_file)
slf.readHeader()
slf.readTimes()
slf.readVariables(t)

# gets some of the mesh properties from the *.slf file
NELEM, NPOIN, NDP, IKLE, IPOBO, x, y = slf.getMesh()

# the IKLE array starts at element 1, but matplotlib needs it to start
# at zero
IKLE[:,:] = IKLE[:,:] - 1

# these are the results for all variables, for time step t
master_results = slf.getVarValues() 

# creates a triangulation grid using matplotlib function Triangulation
triang = mtri.Triangulation(x, y, IKLE)

# determine the spacing of the regular grid
range_in_x = x.max() - x.min()
range_in_y = y.max() - y.min()

max_range = max(range_in_x, range_in_y)

# first index is integer divider, second is remainder
num_x_pts = divmod(range_in_x, spacing)
num_y_pts = divmod(range_in_y, spacing)

print("Size of output matrix is : " + str(int(num_x_pts[0])) + " x " + str(int(num_y_pts[0])))
print("Grid resolution is : " + str(spacing) + " m")

# creates the regular grid
xreg, yreg = np.meshgrid(np.linspace(x.min(), x.max(), int(num_x_pts[0])),
	np.linspace(y.min(), y.max(), int(num_y_pts[0])))
x_regs = xreg[1,:]
y_regs = yreg[:,1]

# to interpolate to a reg grid
interpolator = mtri.LinearTriInterpolator(triang, master_results[var_index])
z = interpolator(xreg,yreg)

print("Shape of array z: " + str(z.shape[0]))
print("Shape of arrays xreg and yreg: " + str(x_regs.shape) + " " + str(y_regs.shape))

where_are_NaNs = np.isnan(z)
z[where_are_NaNs] = -999.0

# open the output *.asc file, and write the header info
header_str = "NCOLS " + str(z.shape[1]) + "\n"
header_str = header_str + "NROWS " + str(z.shape[0]) + "\n"
header_str = header_str + "XLLCORNER " + str(x_regs[0]) + "\n"
header_str = header_str + "YLLCORNER " + str(y_regs[0]) + "\n"
header_str = header_str + "CELLSIZE " + str(spacing) + "\n"
header_str = header_str + "NODATA_VALUE " + str(-999.00) + "\n"

#np.savetxt("temp.out", z, fmt='%.2f', delimiter='') # this has no max spaces
np.savetxt(output_file, np.flipud(z), fmt='%10.3f', header = header_str,
	comments = '', delimiter='') # this has 10 char spaces, 2 after decimal

print("All Done")
