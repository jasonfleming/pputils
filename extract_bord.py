#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 extract_bord.py                       # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: March 30, 2017
#
# Purpose: Script takes in a *.slf file, and a PPUTILS points file, and
# extracts results for all time steps, for all variables, in a format
# used by my bord.f subroutine used to force a local TELEMAC-2D
# domain. Essentially, this script extracts boundary conditions at
# specified nodes from a global TELEMAC-2D run, and formats it in a way
# that it can be used to force a local TELEMAC-2D model using my bord.f
# subroutine.
#
# Uses: Python 2 or 3, Matplotlib, Numpy, Scipy
#
# Example:
#
# python extract_pt.py -i in.slf -p points.csv -o out.txt
# where:
# -i input *.slf file
# -p PPUTILS nodes file with coordinates of extraction points
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
if len(sys.argv) != 7 :
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python extract_bord.py -i in.slf -p points.csv -o out.txt')
  sys.exit()

input_file = sys.argv[2]
points_file = sys.argv[4]
output_file = sys.argv[6]

# read the input *.slf file
slf = ppSELAFIN(input_file)
slf.readHeader()
slf.readTimes()

# get times of the selafin file, and the variable names
times = slf.getTimes()
variables = slf.getVarNames()
units = slf.getVarUnits()

# number of variables
NVAR = len(variables)

# number of time steps
ntimes = len(times)

# to remove duplicate spaces from variables and units
for i in range(NVAR):
  variables[i] = ' '.join(variables[i].split())
  units[i] = ' '.join(units[i].split())

# gets some of the mesh properties from the *.slf file
NELEM, NPOIN, NDP, IKLE, IPOBO, x, y = slf.getMesh()

# determine if the *.slf file is 2d or 3d by reading how many planes it has
NPLAN = slf.getNPLAN()

# error checking
if (NPLAN > 1):
  print('Input file is a 3d, which is not yet supported. Sorry.')
  sys.exit()

# now read the PPUTILS points file
points_data = np.loadtxt(points_file, delimiter=',',skiprows=0,unpack=True)

# put the points_data into vectors; ox and oy are offshore x and offshore y
ox = points_data[0,:]
oy = points_data[1,:]

# number of points in the offshore data set
npoints = len(ox)

# create a cKDTree object
source = np.column_stack((x,y))
tree = spatial.cKDTree(source)

# list of output for final results for bord.f
all_res = np.empty([npoints,ntimes,NVAR])

# for each coordinate in the points data, find the corresponding node
# in the results file mesh
for i in range(npoints):
    
  # find the node index using cKDTree        
  d, idx = tree.query((ox[i],oy[i]), k = 1)

  # now that we know which node it is, use methods in ppSELAFIN_io class
  slf.readVariablesAtNode(idx)
  result = slf.getVarValuesAtNode()

  all_res[i,:,:] = result
  
# to write a separate file for each variable
for k in range(NVAR):
  out = np.transpose(all_res[:,:,k])
  out_name = output_file.rsplit('.',1)[0] + '_' + str(variables[k]) + '.csv'
  np.savetxt(out_name, out, delimiter=',')
  
print('All done!')


        
