#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 adcirc_to_2dm.py                      # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Apr 19, 2020
#
# Purpose: Script takes in a mesh in adcirc format, and writes it to a
# *.2dm file format.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python adcirc_to_2dm.py -i -out.grd -o out.2dm 
# where:
# -i input adcirc mesh file
# -o output 2dm mesh file
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys,time                         # system parameters
import numpy             as np             # numpy
from ppmodules.readMesh import *           # to get all readMesh functions
from ppmodules.writeMesh import *          # to get all readMesh functions
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 5 :
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python adcirc_to_2dm.py -i out.grd -o out.2dm')
  sys.exit()

adcirc_file = sys.argv[2]
two_dm_file = sys.argv[4]

# read the adcirc file
n,e,x,y,z,ikle = readAdcirc(adcirc_file)

# write the 2dm file
write2dm(n,e,x,y,z,ikle,two_dm_file)

print('All done!')

