#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 extract_line_v.py                     # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
#
# Date: Feb 22, 2017
#
# Purpose: Script designed to open 2D telemac binary file and write the
# values of all time steps (for a given variable) for the nodes along
# the lines file. 
#
# Revised: Mar 9, 2017
# Deleted the trailing comma in the text output.
#
# Revised: Jun 14, 2019
# Added the progress bar.
#
# Uses: Python 2 or 3, Numpy
#
# Usage:
# python extract_line_v.py -i res.slf -v 1 -l line.csv -o line_v.csv
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sys
import numpy as np
import matplotlib.tri as mtri
from ppmodules.selafin_io_pp import *
from progressbar import ProgressBar, Bar, Percentage, ETA
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MAIN
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
# I/O
if len(sys.argv) == 9:
  input_file = sys.argv[2]         # input *.slf file
  v = int(sys.argv[4])             # index of variable to output
  lines_file = sys.argv[6]         # input lines file
  output_file  = sys.argv[8]       # output lines file
else:
  print('Wrong number of arguments ... stopping now ...')
  print('Usage:')
  print('python extract_line_v.py -i res.slf -v 1 -l line.csv -o line_v.csv')
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
ln_interp = np.zeros((len(times), len(lnx)))
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

print('Interpolating ...')

# progress bar
w = [Percentage(), Bar(), ETA()]
pbar = ProgressBar(widgets=w, maxval=len(times)).start()

for i in range(len(times)):
  #print('Interpolating time: ' + str(times[i]) + ' out of ' + str(times[len(times)-1]))
  
  slf.readVariables(i)
  results = slf.getVarValues()

  interpolator = mtri.LinearTriInterpolator(triang, results[v,:])
  ln_interp[i,:] = interpolator(lnx,lny)
  
  # update the pbar
  pbar.update(i+1)

# finish the pbar
pbar.finish()

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
for i in range(len(times)):
  if (i < len(times)-1):
    fout.write(str(times[i]) + ', ')
  else:
    fout.write(str(times[i]))  
fout.write('\n')  

# to write the data
for k in range(len(lnx)):
  fout.write(str(shapeid[k]) + ', ' + str(lnx[k]) + ', ' + str(lny[k]) + ', ')
  fout.write(str(sta[k]) + ', ')
  for j in range(len(times)):
    if (j < len(times)-1):
      fout.write(str(ln_interp_tr[k,j]) + ', ')
    else:
      fout.write(str(ln_interp_tr[k,j]))
  fout.write('\n')  
