#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 adcirc2vtk.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Feb 20, 2016
#
# Purpose: Script takes in a mesh in ADCIRC format, and outputs a legacy 
# *.vtk file for visualization on ParaView. This is useful for viewing
# TINs in ParaView.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python adcirc2vtk.py -i out.grd -o out.vtk
# where:
# -i input adcirc mesh file
# -o output *.vtk file
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy             as np             # numpy
from ppmodules.readMesh import *           # to get all readMesh functions
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
	print('python adcirc2vtk.py -i out.grd -o out.vtk')
	sys.exit()
dummy1 =  sys.argv[1]
adcirc_file = sys.argv[2]
dummy2 = sys.argv[3]
vtk_file = sys.argv[4]

# to create the output files
fout = open(vtk_file,"w")

# read the adcirc file
n,e,x,y,z,ikle = readAdcirc(adcirc_file)

# write the legacy *.vtk file

# vtk header file
fout.write('# vtk DataFile Version 3.0' + '\n')
fout.write('Created with pputils' + '\n')
fout.write('ASCII' + '\n')
fout.write('' + '\n')
fout.write('DATASET UNSTRUCTURED_GRID' + '\n')
fout.write('POINTS ' + str(len(x)) + ' float' + '\n')

# to write the node coordinates
for i in range(len(x)):
	fout.write(str("{:.3f}".format(x[i])) + ' ' + 
		str("{:.3f}".format(y[i])) + ' ' + str("{:.3f}".format(0.0)) + 
		'\n')
		
# to write the node connectivity table
fout.write('CELLS ' + str(len(ikle)) + ' ' + str(len(ikle)*4) + '\n')

for i in range(len(ikle)):
	fout.write('3 ' + str(ikle[i][0]) + ' ' + str(ikle[i][1]) + ' ' + 
		str(ikle[i][2]) + '\n')
		
# to write the cell types
fout.write('CELL_TYPES ' + str(len(ikle)) + '\n')
for i in range(len(ikle)):
	fout.write('5' + '\n')
	
# write the empty line
fout.write('' + '\n')

# write the data
fout.write('POINT_DATA ' + str(len(x)) + '\n')

# write the z as scalar data also
fout.write('SCALARS z' + '\n')
fout.write('float' + '\n')
fout.write('LOOKUP_TABLE default' + '\n')
for i in range(len(x)):
	fout.write(str("{:.3f}".format(z[i])) + '\n')
			
			
			
