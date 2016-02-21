#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 sel2flt.py                            # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng. 
# 
# Date: Dec 26, 2015
#
# Modified: Feb 21, 2016
# Made it work for python 2 and 3
#
# Purpose: Script designed to open 2D telemac binary file, read the
# the desired output to an ESRI *.flt file for use in displaying within a
# GIS environment. Same as my sel2flt.py script.
# 
# Using: Python 2 or 3, Matplotlib, Numpy
#
# Example: python sel2flt.py -i input.slf -v 4 -t 0 -s 2.0 -o output.flt
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
#       --> -o is the *.flt output file
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import matplotlib.tri as mtri
import numpy as np
import struct
from ppmodules.selafin_io_pp import *
from progressbar import ProgressBar, Bar, Percentage, ETA

if len(sys.argv) != 11:
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python sel2flt.py -i input.slf -v 4 -t 0 -s 2.0 -o output.flt')
	sys.exit()

input_file = sys.argv[2]         # input *.slf file
var_index  = int(sys.argv[4])    # index number of grided output variable 
t = int(sys.argv[6])             # index of time record of the output to use in griding (integer, 0 to n)                                  
spacing = float(sys.argv[8])     # specified the grid spacing of the output file
output_file = sys.argv[10]        # output *.flt grid file

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

# to create the output *.flt file
fout = open(output_file,"wb")

# the name of the header file (this is asci format)
header_file = output_file.split('.',1)[0] + '.hdr'
fhdr = open(header_file,"w")

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

print("Interpolating ...")

# to interpolate to a reg grid
interpolator = mtri.LinearTriInterpolator(triang, master_results[var_index])
z = interpolator(xreg,yreg)

where_are_NaNs = np.isnan(z)
z[where_are_NaNs] = -999.0

#np.savetxt("temp.out", z, fmt='%.2f', delimiter='') # this has no max spaces
#np.savetxt('temp.out', np.flipud(z), fmt='%10.3f', delimiter='') # this has 10 char spaces, 2 after decimal

# open the output *.asc file, and write the header info
fhdr.write("NCOLS " + str(z.shape[1]) + "\n")
fhdr.write("NROWS " + str(z.shape[0]) + "\n")
fhdr.write("XLLCORNER " + str(x_regs[0]) + "\n")
fhdr.write("YLLCORNER " + str(y_regs[0]) + "\n")
fhdr.write("CELLSIZE " + str(spacing) + "\n")
fhdr.write("NODATA_VALUE " + str(-999.00) + "\n")
fhdr.write("BYTEORDER LSBFIRST " + "\n")

print("Writing binary data file ...")

w = [Percentage(), Bar(), ETA()]
pbar = ProgressBar(widgets=w, maxval=z.shape[0]).start()
for i in range(z.shape[0]):
	s = struct.pack('f'*z.shape[1], *np.flipud(z)[i,:])
	fout.write(s)
	pbar.update(i+1)
fout.close()
pbar.finish()

print("All done!")

