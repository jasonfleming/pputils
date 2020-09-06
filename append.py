#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 append.py                             # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Feb 20, 2016
#
# Purpose: Script takes two *.slf files that have the same mesh, and 
# appends friction variable to the original file. This programs assumes 
# that both *.slf files have only one variable, and only one time record
# (which is the case if they were created with pputils).
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python append.py -i bathy.slf friction.slf -o merged.slf
# where:
# -i input *.slf files
# -o output *.slf file with merged variables 
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import numpy as np 
from ppmodules.selafin_io_pp import *
#
# I/O
if len(sys.argv) != 6 :
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python append.py -i bathy.slf friction.slf -o merged.slf')
	sys.exit()
dummy1 =  sys.argv[1]
first_file = sys.argv[2]
second_file = sys.argv[3]
dummy2 =  sys.argv[4]
output_file = sys.argv[5]

# reads the first SELAFIN file
slf1 = ppSELAFIN(first_file)
slf1.readHeader()
slf1.readTimes()
slf1.readVariables(0)

# get the mesh properties from the first file
NELEM, NPOIN, NDP, IKLE, IPOBO, x, y = slf1.getMesh()

# reads the second SELAFIN file
slf2 = ppSELAFIN(second_file)
slf2.readHeader()
slf2.readTimes()
slf2.readVariables(0)

if (slf1.NPOIN != slf2.NPOIN) or (slf1.NELEM != slf2.NELEM):
	print('Nodes and elements of two input files do not match ... exiting.')
	sys.exit()

# now we are ready to write the output
out = ppSELAFIN(output_file)
out.setPrecision('f',4) # assume single precision
out.setTitle('created with pputils')
out.setVarNames(['BOTTOM          ','BOTTOM FRICTION '])
out.setVarUnits(['M               ','                '])
out.setIPARAM([1, 0, 0, 0, 0, 0, 0, 0, 0, 1])
out.setMesh(NELEM, NPOIN, NDP, IKLE, IPOBO, x, y)
out.writeHeader()

# this is the merged bathy-friction array of size (2,NPOIN)
bf = np.zeros((2,NPOIN))

bathy = slf1.getVarValues()
friction = slf2.getVarValues()

bf[0,:] = bathy[0,:]
bf[1,:] = friction[0,:]

out.writeVariables(0.0, bf)
