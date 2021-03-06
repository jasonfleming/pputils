#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 append_adcirc.py                      # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Feb 20, 2016
#
# Purpose: Script takes two *.grd adcirc files (one bathy and one friction)
# and merges them into a single *.slf file for use in TELEMAC simulations.
# Similar to append.py, except it uses adcirc files as input.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python append_adcirc.py -i bathy.grd friction.grd -o merged.slf
# where:
# -i input *.grd files
# -o output *.slf file with merged variables 
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import numpy as np 
from ppmodules.selafin_io_pp import *
from ppmodules.readMesh import *
from ppmodules.utilities import *
#
# I/O
if len(sys.argv) != 6 :
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python append_adcirc.py -i bathy.grd friction.grd -o merged.slf')
	sys.exit()
dummy1 =  sys.argv[1]
first_file = sys.argv[2]
second_file = sys.argv[3]
dummy2 =  sys.argv[4]
output_file = sys.argv[5]

# reads the first and second ADCIRC files
n1,e1,x1,y1,z1,ikle1 = readAdcirc(first_file)
n2,e2,x2,y2,z2,ikle2 = readAdcirc(second_file)

if (n1 != n2) or (e1 != e2):
	print('Nodes and elements of two input files do not match ... exiting.')
	sys.exit()

# use getIPOBO_IKLE() to get IPOBO and IKLE arrays
# this method also writes a 'temp.cli' file as well
IPOBO, IKLE = getIPOBO_IKLE(first_file)

# rename temp.cli to proper name
cli_file = output_file.split('.',1)[0] + '.cli'
os.rename('temp.cli',cli_file)

# It needs these to write the *.slf file
NELEM = e1
NPOIN = n1
NDP = 3 # always 3 for triangular elements
x = x1
y = y1

# now we are ready to write the output *.slf file
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

bf[0,:] = z1
bf[1,:] = z2

out.writeVariables(0.0, bf)
