#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 append_adcirc_friction.py             # 
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
# Revised: Feb 18, 2017
# Added precision (single or double) as a command line input.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python append_adcirc.py -b bathy.grd -f friction.grd -p single -o merged.slf
# where:
# -b input bathy *.grd file
# -f input fruction *.grd file
# -p precision of the *.slf file
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
if len(sys.argv) != 9 :
  print('Wrong number of arguments, stopping now...')
  print('Usage:')
  print('python append_adcirc_friction.py -b bathy.grd -f friction.grd -p single -o merged.slf')
  sys.exit()

bathy_file = sys.argv[2]
friction_file = sys.argv[4]
precision = sys.argv[6]
output_file = sys.argv[8]

if(precision == 'single'):
  ftype = 'f'
  fsize = 4
elif(precision == 'double'):
  ftype = 'd'
  fsize = 8
else:
  print('Precision unknown! Exiting!')
  sys.exit(0)

# reads the first and second ADCIRC files
# note that ikle's are zero based in the readAdcirc() method
# but, we are not using the ikle's from here, only z1 and z2
n1,e1,x1,y1,z1,ikle1 = readAdcirc(bathy_file)
n2,e2,x2,y2,z2,ikle2 = readAdcirc(friction_file)

if (n1 != n2) or (e1 != e2):
  print('Nodes and elements of two input files do not match ... exiting.')
  sys.exit()

# use getIPOBO_IKLE() to get the geometry from the bathy file
# this method also writes a 'temp.cli' file as well
# note indices in ikle and ipobo are one based
n,e,x,y,z,IKLE,IPOBO = getIPOBO_IKLE(bathy_file)

# rename temp.cli to proper name
cli_file = output_file.split('.',1)[0] + '.cli'
os.rename('temp.cli',cli_file)

# It needs these to write the *.slf file
NELEM = e
NPOIN = n
NDP = 3 # always 3 for triangular elements

# now we are ready to write the output *.slf file
out = ppSELAFIN(output_file)
out.setPrecision(ftype, fsize) 
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
