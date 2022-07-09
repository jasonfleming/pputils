#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 2dm_to_adcirc.py                      # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Apr 19, 2020
#
# Purpose: Script takes in a mesh in 2dm format, and writes it to a
# adcirc file format. This script works only for triangular elements.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python 2dm_to_adcirc.py -i -out.2dm -o out.grd 
# where:
# -i input 2dm mesh file 
# -o output adcirc mesh file
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
  print('python 2dm_to_adcirc.py -i out.2dm -o out.grd')
  sys.exit()

two_dm_file = sys.argv[2]
adcirc_file = sys.argv[4]

# read the 2dm file
n,e,x,y,z,ikle = read2dm(two_dm_file)

# write the adcirc file
writeAdcirc(n,e,x,y,z,ikle,adcirc_file)

print('All done!')
