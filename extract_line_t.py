#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 extract_line_t.py                     # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
#
# Date: Feb 22, 2017
#
# Purpose: Script designed to open 2D telemac binary file and write the
# values of all variables (for a particular time step) for the nodes
# along the given line. 
#
# Revised: Mar 9, 2017
# Deleted the trailing comma in the text output.
#
# Uses: Python 2 or 3, Numpy
#
# Usage:
# python extract_line_t.py -i res.slf -t 8 -l line.csv -o line_t.csv
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sys
import numpy as np
import matplotlib.tri as mtri
from ppmodules.selafin_io_pp import *
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MAIN
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
# I/O
if len(sys.argv) == 9:
  input_file = sys.argv[2]         # input *.slf file
  t = int(sys.argv[4])             # index of time record
  lines_file = sys.argv[6]         # input lines file
  output_file  = sys.argv[8]       # output lines file
else:
  print('Wrong number of arguments ... stopping now ...')
  print('Usage:')
  print('python extract_line_t.py -i res.slf -t 8 -l line.csv -o line_t.csv')
  sys.exit()

# use Numpy to read the lines file
# all data is read as floats
lines_data = np.loadtxt(lines_file, delimiter=',',skiprows=0,unpack=True)
shapeid = lines_data[0,:]
shapeid = shapeid.astype(np.int32)
lnx = lines_data[1,:]
lny = lines_data[2,:]

# Read the header of the selafin result file and get geometry and
# variable names and units

print('Reading result file headers ...')

# use selafin_io_pp class ppSELAFIN
slf = ppSELAFIN(input_file)
slf.readHeader()
slf.readTimes()

# get the mesh properties from the resultfile
NELEM, NPOIN, NDP, IKLE, IPOBO, x, y = slf.getMesh()

# the IKLE array starts at element 1, but matplotlib needs it to start at zero
# note that doing this invalidates the IPOBO array; but we don't need IPOBO here
IKLE[:,:] = IKLE[:,:] - 1

# use get methods from ppSELAFIN class
times = slf.getTimes()
vnames = slf.getVarNames()
vunits = slf.getVarUnits()
NPLAN = slf.getNPLAN()

# to warn the user that this applies for 2d SELAFIN files only
if (NPLAN > 1):
  print('It does not make sense to run this script for 3d SELAFIN files.')
  print('Use POSTEL-3D or Paraview instead!')
  sys.exit(0)

# number of variables
numvars = len(vnames)

# create the new output variables for the output file
ln_interp = np.zeros((numvars, len(lnx)))
sta = np.zeros(len(lnx))
tempid = np.zeros(len(lnx))
dist = np.zeros(len(lnx))

# to create the sta array
sta[0] = 0.0
tempid = shapeid
dist[0] = 0.0

for i in range(1,len(lnx)):
  if (tempid[i] - shapeid[i-1] < 0.001):
    xdist = lnx[i] - lnx[i-1]
    ydist = lny[i] - lny[i-1]
    dist[i] = np.sqrt(np.power(xdist,2.0) + np.power(ydist,2.0))
    sta[i] = sta[i-1] + dist[i]

# create a result triangulation object
triang = mtri.Triangulation(x, y, IKLE)

# read the variables for the specified time step t
slf.readVariables(t)
results = slf.getVarValues()

print('Interpolating ...')

# now to interpolate the result file to the nodes of the lines file, for
# each variable in the file (for the specified time step only).
for j in range(numvars):
  interpolator = mtri.LinearTriInterpolator(triang, results[j,:])
  ln_interp[j,:] = interpolator(lnx,lny)

print('Transposing ...')
  
# tranpose the interpolated result, so that they will print nicely  
ln_interp_tr = np.transpose(ln_interp)

where_are_NaNs = np.isnan(ln_interp_tr)
if (np.sum(where_are_NaNs) > 0):
	print('#####################################################')
	print('')
	print('WARNING: Some line nodes are outside of the mesh boundary!!!')
	print('')
	print('#####################################################')

print('Writing output to file ...')

# to write the output file
fout = open(output_file, 'w')

# to write variable names header (this is not in true style of pputils
# lines data, but it will be easier on the eyes ...)
fout.write(str('id, x, y, sta, '))
for j in range(numvars):
  if (j < len(vnames)-1):
    fout.write(str(vnames[j]) + ', ')
  else:
    fout.write(str(vnames[j]))
fout.write('\n')  
           
# to write the data
for i in range(len(lnx)):
  fout.write(str(shapeid[i]) + ', ' + str(lnx[i]) + ', ' + str(lny[i]) + ', ')
  fout.write(str(sta[i]) + ', ')
  for j in range(numvars):
    if (j < len(vnames)-1):
      fout.write(str(ln_interp_tr[i,j]) + ', ')
    else:
      fout.write(str(ln_interp_tr[i,j]))
  fout.write('\n')  

