#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 ply2adcirc.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.

# Date: Nov 2, 2016
#
# Purpose: Script designed to open a *.ply file, and output it to an 
# adcirc *.grd file. This script is useful for taking geometry modifed
# by MeshLab and then bringing it back to pputils.
# 
# Works for Python 2 or Python 3
#
# Uses: Python 2 or 3, Numpy
#
# Example:
# 
# when extracting 1 variable
# python ply2adcirc.py -i out.ply -o out.grd
# where:
# -i MeshLab *ply mesh file
# -o Adcirc *.grd file
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sys
import numpy as np
from ppmodules.readMesh import *           # to get all readMesh functions
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MAIN
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
# I/O
if len(sys.argv) != 5 :
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python adcirc2ply.py -i out.grd -o out.ply')
	sys.exit()

ply_file = sys.argv[2]	
adcirc_file = sys.argv[4]

# to create the output files
fout = open(adcirc_file,'w')

# read the ply file
n,e,x,y,z,ikle = readPly(ply_file)

# now to write the adcirc mesh file
fout.write("ADCIRC" + "\n")

# writes the number of elements and number of nodes in the header file
fout.write(str(e) + " " + str(n) + "\n")

# writes the nodes
for i in range(n):
	fout.write(str(i+1) + " " + str("{:.3f}".format(x[i])) + " " + 
		str("{:.3f}".format(y[i])) + " " + str("{:.3f}".format(z[i])) + "\n")

# writes the elements
for i in range(e):
	fout.write(str(i+1) + " 3 " + str(ikle[i,0]) + " " + str(ikle[i,1]) + " " + 
		str(ikle[i,2]) + "\n")	

print("All Done!")


