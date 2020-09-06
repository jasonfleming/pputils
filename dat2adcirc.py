#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 dat2adcirc.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Jan 29, 2018
#
# Purpose: Script takes files of type *.dat and converts it to the
# ADCIRC mesh file format.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python dat2adcirc.py -i out.dat -o out.grd
# where:
# -i input *.dat mesh file
# -o output adcirc *.grd mesh file
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import numpy as np

from ppmodules.readMesh import *
from ppmodules.writeMesh import *

# this works for python 2 and 3
def CCW(x1,y1,x2,y2,x3,y3):
  return (y3-y1)*(x2-x1) > (y2-y1)*(x3-x1)	

# I/O
if len(sys.argv) != 5 :
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python dat2adcirc.py -i out.dat -o out.grd')
  sys.exit()

dat_file = sys.argv[2]
adcirc_file = sys.argv[4]

# reads the *.dat file (this method is in file readMesh.py)
# the ikle array indices are zero based, same as readAdcirc() method
n,e,x,y,z,ikle = readDat(dat_file)

# #######################
# make sure the elements are oriented in CCW fashion
# go through each element, and make sure it is oriented in CCW fashion
for i in range(len(ikle)):
  
  # if the element is not CCW then must change its orientation
  if not CCW( x[ikle[i,0]], y[ikle[i,0]], x[ikle[i,1]], y[ikle[i,1]], 
    x[ikle[i,2]], y[ikle[i,2]] ):
    
    t0 = ikle[i,0]
    t1 = ikle[i,1]
    t2 = ikle[i,2]
    
    # switch orientation
    ikle[i,0] = t2
    ikle[i,2] = t0
# #######################

# writes the mesh file
writeAdcirc(n,e,x,y,z,ikle,adcirc_file)

