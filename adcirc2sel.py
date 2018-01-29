#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 adcirc2sel.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: February 15, 2016
#
# Purpose: Script takes in a mesh in ADCIRC format, and converts it to
# TELEMAC's SELAFIN format. Made it to depend on selafin_io_pp, which
# works under python 2 and 3!
#
# Revised: Feb 18, 2017
# Added the precision as a command line argument.
#
# Revised: Apr 29, 2017
# Changed how different system architectures are called; made it run
# for the raspberry pi system.
#
# Revised: May 6, 2017
# Placed a call to processor type inside the posix if statement.
#
# Revised: Jan 29, 2018
# The IPOBO array is now generated using the Fortran program
# bnd_extr_stbtel.f90 (pre-compiled binaries are available for
# Linux 32, Linux 64, and Windows).
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python adcirc2sel.py -i mesh.grd -p single -o mesh.slf
# where:
# -i input adcirc mesh file
# -p precision of the *.slf file (single or double)
# -o converted *.slf mesh file
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy as np                         # numpy
import struct                              # to determine sys architecture
import subprocess                          # to execute binaries
from ppmodules.selafin_io_pp import *      # pp's SELAFIN io
from ppmodules.readMesh import *           # for the readAdcirc function
from ppmodules.utilities import *          # getIPOBO_IKLE() method
#
# this works for python 2 and 3
def CCW(x1,y1,x2,y2,x3,y3):
   return (y3-y1)*(x2-x1) > (y2-y1)*(x3-x1)  
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 7:
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python adcirc2sel.py -i mesh.grd -p single -o mesh.slf')
  sys.exit()
adcirc_file = sys.argv[2]
precision = sys.argv[4]
output_file = sys.argv[6]

# reads mesh data using the get IPOBO_IKLE() method from utilities.py
# the ikle and the ppIPOB are one-based
n,e,x,y,z,ikle,ppIPOB = getIPOBO_IKLE(adcirc_file)

# the above method generates a file called temp.cli, which we rename here
cli_file = output_file.split('.',1)[0] + '.cli'
os.rename('temp.cli',cli_file)

# now we can write the *.slf file
#######################################################################
if(precision == 'single'):
  ftype = 'f'
  fsize = 4
elif(precision == 'double'):
  ftype = 'd'
  fsize = 8
else:
  print('Precision unknown! Exiting!')
  sys.exit(0)

# getIPOBO_IKLE() method provides these values
NELEM = e
NPOIN = n
NDP = 3 # always 3 for triangular elements
IKLE = ikle  
IPOBO = ppIPOB

slf = ppSELAFIN(output_file)
slf.setPrecision(ftype, fsize)
slf.setTitle('created with pputils')
slf.setVarNames(['BOTTOM          '])
slf.setVarUnits(['M               '])
slf.setIPARAM([1, 0, 0, 0, 0, 0, 0, 0, 0, 1])
slf.setMesh(NELEM, NPOIN, NDP, IKLE, IPOBO, x, y)
slf.writeHeader()

# if writing only 1 variable, must have numpy array of size (1,NPOIN)
# for 2 variables, must have numpy array of size (2,NPOIN), and so on.
zz = np.zeros((1,NPOIN))
zz[0,:] = z

slf.writeVariables(0.0, zz)
#######################################################################
