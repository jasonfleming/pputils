#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 sel2adcirc.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.

# Date: Apr 12, 2016
#
# Purpose: Script designed to open 2D telemac binary file, read the
# the desired *.slf result variable(s), and output it to an adcirc *.grd file.
# This script is useful for taking geometry built from previous modeling files
# (which were saved in *.slf) and bringing them to pputils.
# 
# Works for Python 2 or Python 3 as it uses selafin_io_pp class ppSELAFIN.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
# 
# when extracting 1 variable
# python sel2adcirc.py -i input.slf -v 2 -t 23 -o output.grd
#
# where:
#       --> -i is the *.slf file from which to extract data
#
#       --> -v is the index of the variable to extract;
#                         see probe.py for index codes;
#
#       --> -t is the index of the time step to extract
#
#       --> -o is the adcirc output file
#
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sys
import numpy as np
from ppmodules.selafin_io_pp import *
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MAIN
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
# I/O
if len(sys.argv) == 9:
	# python extract.py -i input.slf -v 2 -t 23 -o output.xyz
	input_file = sys.argv[2]         # input *.slf file
	var1_idx = int(sys.argv[4])      # index of variable 1
	var2_idx = 0                     # variable 2 is nothing here ...
	t = int(sys.argv[6])             # index of time record
	output_file  = sys.argv[8]       # output file
else:
	print('Wrong number of arguments ... stopping now ...')
	print(' ')
	print('python sel2adcirc.py -i input.slf -v 2 -t 23 -o output.grd')
	sys.exit()

# create the output file
fout = open(output_file, "w")
#
# Read the header of the selafin result file and get geometry and
# variable names and units

# use selafin_io_pp class ppSELAFIN
slf = ppSELAFIN(input_file)
slf.readHeader()
slf.readTimes()
slf.readVariables(t)

times = slf.getTimes()
vnames = slf.getVarNames()
vunits = slf.getVarUnits()
master_results = slf.getVarValues()
x = slf.getMeshX()
y = slf.getMeshY()
ikle = slf.getIKLE()

# nodes and elements
nodes = len(x)
elements = len(ikle[:,0])

# the variable to print in the adcirc file
var1 = master_results[var1_idx]

# now to write the adcirc mesh file
fout.write("ADCIRC" + "\n")
# writes the number of elements and number of nodes in the header file
fout.write(str(elements) + " " + str(nodes) + "\n")

# writes the nodes
for i in range(nodes):
	fout.write(str(i+1) + " " + str("{:.3f}".format(x[i])) + " " + 
		str("{:.3f}".format(y[i])) + " " + str("{:.3f}".format(var1[i])) + "\n")

# writes the elements
for i in range(elements):
	fout.write(str(i+1) + " 3 " + str(ikle[i,0]) + " " + str(ikle[i,1]) + " " + 
		str(ikle[i,2]) + "\n")	

# print("All Done!")


