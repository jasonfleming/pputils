#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 sel_mod_date.py                       # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Sep 25, 2020
# Purpose: Script that takes in a *.slf file, and simply modifies the
# date according to the intputs given. Nothing is changed in the *.slf
# file other than the date.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python sel_mod_date.py -i in.slf -d 2020 09 25 01 00 00 -o out.slf
# where:
# -i input *.slf file
# -d date as a six integers (yyyy mm dd hh mm ss)
# -o output *.slf file with the specified date
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import numpy as np
from ppmodules.selafin_io_pp import *
from progressbar import ProgressBar, Bar, Percentage, ETA
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# I/O
if len(sys.argv) != 12:
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python sel_mod_date.py -i in.slf -d 2020 09 25 01 00 00 -o out.slf')
  sys.exit()

input_file = sys.argv[2]
year = int(sys.argv[4])
month = int(sys.argv[5])
day = int(sys.argv[6])
hour = int(sys.argv[7])
minute = int(sys.argv[8])
second = int(sys.argv[9])
output_file = sys.argv[11]

# check to make sure the date entered is valid
if (month < 1 or month > 12):
  print('Invalid month. Try again. Exiting!')
  sys.exit(0)
if (day < 1 or day > 31):
  print('Invalid day. Try again. Exiting!')
  sys.exit(0)
if (hour < 0 or hour > 23):
  print('Invalid hour. Try again. Exiting!')
  sys.exit(0)  
if (minute < 0 or minute > 59):
  print('Invalid minute. Try again. Exiting!')
  sys.exit(0)
if (second < 0 or second > 59):
  print('Invalid second. Try again. Exiting!')
  sys.exit(0)  

# read the *.slf file
slf = ppSELAFIN(input_file)
slf.readHeader()
slf.readTimes()

# reads the header information from the SELAFIN file
times = slf.getTimes()
vnames = slf.getVarNames()
vunits = slf.getVarUnits()
float_type,float_size = slf.getPrecision()
NELEM, NPOIN, NDP, IKLE, IPOBO, x, y = slf.getMesh()
DATE = slf.getDATE()
NVAR = len(vnames)

# create a new slf output file
# now write the SELAFIN file for the extracted time step t
slf_out = ppSELAFIN(output_file)
slf_out.setPrecision(float_type, float_size)
slf_out.setTitle('created with pputils')
slf_out.setVarNames(vnames)
slf_out.setVarUnits(vunits)
slf_out.setIPARAM([1, 0, 0, 0, 0, 0, 0, 0, 0, 1])
slf_out.setMesh(NELEM, NPOIN, NDP, IKLE, IPOBO, x, y)
slf_out.setDATE([year,month,day,hour,minute,second])
slf_out.writeHeader()

# for the progress bar
w = [Percentage(), Bar(), ETA()]
pbar = ProgressBar(widgets=w, maxval=len(times)).start()

# now loop over each time step, read the all the variables, and write
# them to the file
for t in range(len(times)):
  pbar.update(t+1)
  # read the variables for each time step
  slf.readVariables(t)
  results = slf.getVarValues()

  # write the answers to the output file
  slf_out.writeVariables(t, results)
pbar.finish()
