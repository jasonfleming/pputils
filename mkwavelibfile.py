#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 mkwavelibfile.py                      # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: May 25, 2016
#
# Purpose: This script creates the master wave library file. It takes the
# last time step in the *.slf result files that were created by the wave 
# library task farming process and merges it into one master file. Each  
# record in the master wave library file is a scenario of wave the library.  
# Prior to running this script, one must run the mkwavescen.py script (which  
# generates the wave library scenarios), and then execute run_scenarios.sh   
# script (that generates results for all cases). 
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python mkwavelibfile.py -o master_wave_lib.slf
# where:
# -o is the master wave library file
#
# Note this script has no input parameters; it uses python's glob function
# to get a list of all *.slf files in the present directory.
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys,glob
import numpy as np
from ppmodules.selafin_io_pp import *
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# I/O
if len(sys.argv) == 3:
	master_lib_file = sys.argv[2]
else:
	print('Wrong number of arguments ... stopping now ...')
	print('Usage:')
	print('python mkwavelibfile.py -o master_wave_lib.slf')
	sys.exit()

# in case the master_lib_file is there from a previous run, remove it
if os.path.isfile(master_lib_file):
	os.remove(master_lib_file)

# gets the current working directory
curdir = os.getcwd()

# gets all the *.cas files in a list
slfFiles = list()
slfFiles = glob.glob('*.slf')

# sort the list of library *.slf files (glob doesn't sort the files read)
slfFiles.sort()

# read the first *.slf file in the list (output will be based on this file)
res = ppSELAFIN(slfFiles[0])
res.readHeader()
res.readTimes()

times = res.getTimes()
vnames = res.getVarNames()
vunits = res.getVarUnits()
float_type,float_size = res.getPrecision()

NELEM, NPOIN, NDP, IKLE, IPOBO, x, y = res.getMesh()
res.close()

# this is the last index of the *.slf result files
t = len(times) - 1

# now create the master library *.slf file
lib = ppSELAFIN(master_lib_file)
lib.setPrecision(float_type,float_size)
lib.setTitle('created with pputils')
lib.setVarNames(vnames)
lib.setVarUnits(vunits)
lib.setIPARAM([1, 0, 0, 0, 0, 0, 0, 0, 0, 1])
lib.setMesh(NELEM, NPOIN, NDP, IKLE, IPOBO, x, y)
lib.writeHeader()

# initialize the counter (x is the scenario id in the library file)
# scenario ids start at 1
x = 1

# now read the results from each *.slf file in slfFiles list and write the 
# master wave library file
for item in slfFiles:
	print('Writing results from file: ' + item)
	res = ppSELAFIN(item)
	res.readHeader()
	res.readTimes()
	res.readVariables(t)
	results = res.getVarValues()
	
	# close the file
	res.close()	
	
	# now write the master lib file
	lib.writeVariables(x, results)
	
	# update counter
	x = x + 1
	
# close the master library file
lib.close()

