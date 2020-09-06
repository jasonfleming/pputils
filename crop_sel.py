#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 crop_sel.py                           # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
#
# Date: Mar 9, 2017
#
# Purpose: Script designed to take an existing SELAFIN result file, and
# retain only the desired time step. This is useful when creating hot-
# start files for use in TELEMAC simulations. To know which time step
# to retain, make sure you run probe.py script first.
#
# Uses: Python 2 or 3, Numpy
#
# Usage:
# python crop_sel.py -i result.slf -t 8 -o result_8.slf
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
  output_file  = sys.argv[6]       # output *.slf file

else:
  print('Wrong number of arguments ... stopping now ...')
  print('Usage:')
  print('python crop_sel.py -i result.slf -t 8 -o result_8.slf')
  sys.exit()

# create the output file
#fout = open(output_file, 'w')
#
# Read the header of the selafin result file and get geometry and
# variable names and units

# use selafin_io_pp class ppSELAFIN
slf = ppSELAFIN(input_file)
slf.readHeader()
slf.readTimes()

# reads the header information from the SELAFIN file
times = slf.getTimes()
vnames = slf.getVarNames()
vunits = slf.getVarUnits()
float_type,float_size = slf.getPrecision()
NELEM, NPOIN, NDP, IKLE, IPOBO, x, y = slf.getMesh()

# number of variables
NVAR = len(vnames)

# read the variables for the specified time step t
slf.readVariables(t)
results = slf.getVarValues()

# now write the SELAFIN file for the extracted time step t
slf_cr = ppSELAFIN(output_file)
slf_cr.setPrecision(float_type, float_size)
slf_cr.setTitle('created with pputils')
slf_cr.setVarNames(vnames)
slf_cr.setVarUnits(vunits)
slf_cr.setIPARAM([1, 0, 0, 0, 0, 0, 0, 0, 0, 1])
slf_cr.setMesh(NELEM, NPOIN, NDP, IKLE, IPOBO, x, y)
slf_cr.writeHeader()

# write the results
# it does not write the time of the original file, but rather
# writes zero instead; if the user wants the time from the
# original file, replace zero with times[t]
slf_cr.writeVariables(0, results)

