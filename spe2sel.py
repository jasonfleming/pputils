#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 spe2sel.py                            # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Feb 21, 2018
#
# Purpose: Script takes in a spectral file produced by TOMAWAC, and
# converts it to a *.slf file. Essentially, the quad mesh used by
# the TOMAWAC's spectral file is converted to a triangular mesh,
# which could then be used by any post-processor that reads *.slf files.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python spe2png.py -i out.spe -o out.slf
# where:
# -i input spectral file (ikle are quads, NDP = 4 in this case)
# -o output selafin file (ikle are triangles, NDP = 3(
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import numpy as np
from ppmodules.selafin_io_pp import *
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
curdir = os.getcwd()

if len(sys.argv) == 5:
  input_file = sys.argv[2]
  output_file = sys.argv[4]
else:
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python spe2sel.py -i input.spe -o output.slf')
  sys.exit()  

# read the existing spectral file
spe = ppSELAFIN(input_file)
spe.readHeader()
spe.readTimes()

# gets the precision of the file
float_type, float_size = spe.getPrecision()

# gets the variable names and units
vnames = spe.getVarNames()
vunits = spe.getVarUnits()

# the number of variables
numvars = len(vnames)

# index of the time step
times = spe.getTimes()

# gets the info from the spectral file and stores into approrpiate vars
ELEM,NPOIN,NDP,IKLE,IPOBO,x,y = spe.getMesh()

# to check if the input file is really a spectral file
if (NDP !=4):
  print('The input file has triangle, not quads. Exiting!.')
  sys.exit(0)

# now we split the quads into triangles
ELEM2 = ELEM * 2
IKLE2 = np.zeros( (ELEM2, 3), dtype=np.int32)

for i in range(ELEM):
  IKLE2[2*i-1,0] = IKLE[i,0]
  IKLE2[2*i-1,1] = IKLE[i,1]
  IKLE2[2*i-1,2] = IKLE[i,2]
  
  IKLE2[2*i,0] = IKLE[i,0]
  IKLE2[2*i,1] = IKLE[i,2]
  IKLE2[2*i,2] = IKLE[i,3]

# re-set the NDP variable to 3 (triangles)
NDP = 3

# now we can write the front matter of the output file
slf = ppSELAFIN(output_file)
slf.setPrecision(float_type,float_size)
slf.setTitle('created with pputils')
slf.setVarNames(vnames)
slf.setVarUnits(vunits)
slf.setIPARAM([1, 0, 0, 0, 0, 0, 0, 0, 0, 1])
slf.setMesh(ELEM2, NPOIN, NDP, IKLE2, IPOBO, x, y)
slf.writeHeader()

# now go through all the time steps and copy data
# to the *.slf container above
for t in range(len(times)):
  res = np.zeros( (numvars, NPOIN) )

  # reads the data from the spectral file
  spe.readVariables(t)
  res = spe.getVarValues()

  # writes the data to the selafin file
  slf.writeVariables(times[t], res)
