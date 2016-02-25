#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 adcirc2asc.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: June 29, 2015
#
# Purpose: Script takes in a tin in ADCIRC format, and generates an ESRI *.asc 
# file for easy visualization by a GIS.
#
# Uses: Python 2 or 3, Matplotlib, Numpy
#
# Example:
#
# python adcirc2asc.py -i tin.14 -s 10 -o tin.asc
# where:
# -i input adcirc mesh file
# -s spacing (in m) of the *.asc grid file
# -o generated *.asc grid file
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import matplotlib.tri    as mtri           # matplotlib triangulations
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
	print('python adcirc2asc.py -i out.grd -o out.txt')
	sys.exit()
dummy1 =  sys.argv[1]
adcirc_file = sys.argv[2]
dummy2 =  sys.argv[3]
output_file = sys.argv[4]

# to create the output file
fout = open(output_file,"w")

# read the adcirc file
n,e,x,y,z,ikle = readAdcirc(adcirc_file)

# create tin triangulation object using matplotlib
tin = mtri.Triangulation(x, y, ikle)

# neighbors
# the indices of the three triangles that share the same edges, 
# or -1 if there is no such neighboring triangle
neighbours = tin.get_cpp_triangulation().get_neighbors()

# edges
# Return integer array of shape (nedges,2) containing all edges of 
# non-masked triangles. Each edge is the start point index and 
# end point index. Each edge (start,end and end,start) appears only once.
edges = tin.get_cpp_triangulation().get_edges()

fout.write('neighbors' + '\n')
for i in range(e):
	fout.write(str(i+1) + ' ' + str(neighbours[i,0]+1) + ' ' + str(neighbours[i,1]+1) + ' ' + str(neighbours[i,2]+1) + '\n')

fout.write(' ' + '\n')
fout.write('edges' + '\n')
for i in range(n):
	fout.write(str(i+1) + ' ' + str(edges[i,0]+1) + ' ' + str(edges[i,1]+1)+ '\n')
