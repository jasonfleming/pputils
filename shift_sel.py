#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 shift_sel.py                          # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Feb 5, 2019
#
# Purpose: Script takes in a *.slf file, and simply shifts its x and y
# coordinates, while keeping all results as they are. This script just
# shifts the x and y coordinates of the *.slf file, and nothing else!
#
# Uses: Python 2 or 3, Matplotlib, Numpy
#
# Example:
#
# python shift_sel.py -i in.slf -x 100.0 -y 200.0 -o out.slf
# where:
# -i input *.slf file
# -x, y coordinates of the horizontal shift
# -o output *.slf file
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
from ppmodules.selafin_io_pp import *
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 9 :
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python shift_sel.py -i in.slf -x 100.0 -y 200.0 -o out.slf')
  sys.exit()

input_file = sys.argv[2]
xu = float(sys.argv[4])
yu = float(sys.argv[6])
output_file = sys.argv[8]

# reads the *.slf file
slf = ppSELAFIN(input_file)
slf.readHeader()
slf.readTimes()

# get times of the selafin file, and the variable names
times = slf.getTimes()
variables = slf.getVarNames()
units = slf.getVarUnits()
float_type,float_size = slf.getPrecision()

# number of variables
NVAR = len(variables)

# gets some mesh properties from the *.slf file
NELEM, NPOIN, NDP, IKLE, IPOBO, x, y = slf.getMesh()

# now shift the x and y coordinates by the amounts specified
x_s = x + xu
y_s = y + yu

# now we can write the result file, keeping all time steps for all vars

# write the front matter of the output *.slf file
outslf = ppSELAFIN(output_file)
outslf.setPrecision(float_type, float_size)
outslf.setTitle('created with pputils')
outslf.setVarNames(variables)
outslf.setVarUnits(units)
outslf.setIPARAM([1, 0, 0, 0, 0, 0, 0, 0, 0, 1])
outslf.setMesh(NELEM, NPOIN, NDP, IKLE, IPOBO, x_s, y_s)
outslf.writeHeader()

# read all data, for all time steps, and simply put it in outslf object
for t in range(len(times)):
  
  # read the data from the original *.slf file
  slf.readVariables(t)
  res = slf.getVarValues()
  
  # write the data to the transformed *.slf file
  outslf.writeVariables(times[t], res)

print('All done!')
