#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 extract.py                            # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
#
# Date: Feb 15, 2016
#
# Purpose: Script designed to open 2D telemac binary file and write the
# values of all variables to a text file for the selected time step.
#
# Revised: Feb 18, 2017
# Got rid of the limitation that only one or two variables could be read.
#
# Revised: Mar 9, 2017
# Deleted the trailing comma in the text output.
#
# Uses: Python 2 or 3, Numpy
#
# Usage:
# python extract.py -i result.slf -t 8 -o result.csv
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sys
import numpy as np
from ppmodules.selafin_io_pp import *
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MAIN
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
# I/O
if len(sys.argv) == 7:
  input_file = sys.argv[2]         # input *.slf file
  t = int(sys.argv[4])             # index of time record
  output_file  = sys.argv[6]       # output text file

else:
  print('Wrong number of arguments ... stopping now ...')
  print('Usage:')
  print('python extract.py -i result.slf -t 8 -o result.csv')
  sys.exit()

# create the output file
fout = open(output_file, 'w')
#
# Read the header of the selafin result file and get geometry and
# variable names and units

# use selafin_io_pp class ppSELAFIN
slf = ppSELAFIN(input_file)
slf.readHeader()
slf.readTimes()

NPLAN = slf.getNPLAN()

if (NPLAN > 1):
  print('It does not make sense to run this script for 3d SELAFIN files.')
  print('Exiting!!!')
  sys.exit(0)

times = slf.getTimes()
vnames = slf.getVarNames()
vunits = slf.getVarUnits()
x = slf.getMeshX()
y = slf.getMeshY()

# number of variables
NVAR = len(vnames)

# now we are ready to output the results
# to write the header of the output file
fout.write('x, ' + 'y, ')
for i in range(NVAR):
  if (i < (NVAR-1)):
    fout.write(vnames[i] + ', ')
  else:
    fout.write(vnames[i])
fout.write('\n')

# do not display units
'''
fout.write('M, M, ')
for i in range(NVAR):
  fout.write(vunits[i] + ', ')
fout.write('\n')
'''

# read the variables for the specified time step t
slf.readVariables(t)
results = slf.getVarValues()

# use numpy to transpose the results
results_tr = np.transpose(results)

# outputs the results
for k in range(len(x)):
  fout.write(str('{:.12f}').format(x[k]) + ', ' + str('{:.12f}').format(y[k]) + ', ')
  for j in range(NVAR):
    if (j < (NVAR-1)):
      fout.write(str("{:.12f}").format(results_tr[k][j]) + ', ')
    else:
      fout.write(str("{:.12f}").format(results_tr[k][j]))
  fout.write('\n')

