#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 shiftMesh.py                          # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: December 1, 2015
#
# Purpose: Script takes in an ADCIRC mesh and shifts it according to
# x_shift and y_shift
#
# Uses: Python2.7.9, Matplotlib v1.4.2, Numpy v1.8.2
#
# Example:
#
# python shiftMesh.py -i out.grd -s -100 -150 -o out_shifted.grd
# where:
# -i mesh in ADCIRC format
# -s amount to shift the x and y coordinates
# -o output mesh that is shifted
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
if len(sys.argv) != 8 :
	print 'Wrong number of Arguments, stopping now...'
	print 'Usage:'
	print 'python shiftMesh.py -i out.grd -s -100 -150 -o out_shifted.grd'
	sys.exit()

dummy1 =  sys.argv[1]
input_file = sys.argv[2]
dummy2 =  sys.argv[3]
x_shift = int(sys.argv[4])
y_shift = int(sys.argv[5])
dummy3 = sys.argv[6]
output_file = sys.argv[7]

# read the adcirc mesh file
n,e,x,y,z,ikle = readAdcirc(input_file)

fout = open(output_file, "w")

# now to write the adcirc mesh file
fout.write("ADCIRC" + "\n")
# writes the number of elements and number of nodes in the header file
fout.write(str(e) + " " + str(n) + "\n")

# writes the nodes
for i in range(n):
	fout.write(str(i+1) + " " + str("{:.3f}".format(x[i] + x_shift)) + " " + 
		str("{:.3f}".format(y[i]+y_shift)) + " " + str("{:.3f}".format(z[i])) + "\n")

# writes the elements
for i in range(e):
	fout.write(str(i+1) + " 3 " + str(ikle[i,0]+1) + " " + str(ikle[i,1]+1) + " " + 
		str(ikle[i,2]+1) + "\n")	



