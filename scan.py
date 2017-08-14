#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 scan.py                               # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
#
# Date: Aug 9, 2017
#
# Purpose: Scans the selafin file, and outputs the min and max of each
# variable. The number format may need to be adjusted if small variables
# are written in the *.slf file. This script is considerably slower than
# probe.py because it reads data for all variables, for all time steps,
# in order to find the min and max of the data.
#
# Modified: Aug 14, 2017
# Rather than scanning data for all time steps, scan the file for a
# particular time step only.
#
# Uses: Python 2 or 3, Numpy
#
# Example: python scan.py -i input.slf -t 3
# 
# where:
#       --> -i is the telemac *.slf file being probed
#       --> -t is the index of the time step being probed
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# need future for backward compatibility with python2
from __future__ import absolute_import, division, print_function
import sys
import numpy as np             
from ppmodules.selafin_io_pp import *

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MAIN
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
if len(sys.argv) == 5:
  input_file = sys.argv[2]   # input *.slf file
  t = int(sys.argv[4])
else:
  print('Wrong number of Arguments, stopping now...')
  print('Example usage:')
  print('python scan.py -i input.slf -t 3')
  sys.exit()

# constructor for pp_SELAFIN class
slf = ppSELAFIN(input_file)
slf.readHeader()
slf.readTimes()

times = slf.getTimes()
vnames = slf.getVarNames()
vunits = slf.getVarUnits()
ftype,fsize = slf.getPrecision()
nplan = slf.getNPLAN()

if (t >= len(times)):
  print('time step is not within the file. Exiting!')
  sys.exit()

# gets some of the mesh properties from the *.slf file
NELEM, NPOIN, NDP, IKLE, IPOBO, x, y = slf.getMesh()

# number of variables
numvars = len(vnames)

# this is the min and max for each variable, for each time step
#tempmin = np.zeros((numvars, len(times)))
#tempmax = np.zeros((numvars, len(times)))

# the min max array for each variable
minmax = np.zeros((numvars,2))

# number of planes
if (nplan > 1):
  slf_type = '3d'
else:
  slf_type = '2d'

# precision of *.slf file
if(ftype == 'f' and fsize == 4):
  precision = 'single'
elif(ftype == 'd' and fsize == 8):
  precision = 'double'
else:
  precision = 'unknown'

# prints variable names and their min and max values from a particular time step
slf.readVariables(t)
master_results = slf.getVarValues()

for j in range(numvars):
  minmax[j,0] = np.min(master_results[j,:])
  minmax[j,1] = np.max(master_results[j,:])
  
print('#########################################################')
print("The input file being scaned: " + input_file)
print('Precision: ' + precision )
print('File type: ' + slf_type )
if (slf_type == '3d'):
  print('Number of planes: ' + str(nplan))
print('Number of elements: ' + str(NELEM))
print('Number of nodes: ' + str(NPOIN))
print('Number of time steps: ' + str(len(times)))
print('Index of output time step: ' + str(t))          
print(' ')
print('#########################################################')
print('Variables in '+input_file+' are: ')
print('---------------------------------------------------------')
print('     v     variable               min         max unit'   )
print('---------------------------------------------------------')
for i in range(len(vnames)):
  print('    ',i, '-->', vnames[i] + str("{:10.3f}".format(minmax[i,0])) +
    '  ' + str("{:10.3f}".format(minmax[i,1]))  + ' [' + vunits[i].strip() + ']')
print(' ')
print('#########################################################')

print('All done!')
