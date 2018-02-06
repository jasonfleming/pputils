#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 adcirc2wkt.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Feb 20, 2016
#
# Purpose: Script takes in a mesh in ADCIRC format, and generates two *.csv 
# files in WKT (well known text) format, one corresponding to elements (this
# is that will visualize the triangulation, and one corresponding to nodes 
# (this one visualizes the node numbers). The WKT format is essentially equvalent
# to a shapefile format.
#
# Revised: May 14, 2016
# Changed the required number of output files from two to one at the command 
# line. The script now automatically writes the nodes and elements WKT file
# separately.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python adcirc2wkt.py -i out.grd -o outWKT.csv
# where:
# -i input adcirc mesh file
# -o generated *.csv WKT files for element polygons and nodes
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
	print('python adcirc2asc.py -i out.grd -o outWKT.csv')
	sys.exit()
dummy1 =  sys.argv[1]
adcirc_file = sys.argv[2]
dummy2 =  sys.argv[3]
output_file = sys.argv[4] # output *.csv WKT file

# create the element and node output files
output_file_e = output_file.rsplit('.',1)[0] + '_e.csv'
output_file_n = output_file.rsplit('.',1)[0] + '_n.csv'

# to create the output file
fout = open(output_file_e,"w")

# read the adcirc file
n,e,x,y,z,ikle = readAdcirc(adcirc_file)

# write the header of the WKT file\
fout.write('WKT,element' + '\n')

for i in range(e):
	fout.write('"POLYGON ((')
	fout.write(str('{:.3f}'.format(x[ikle[i,0]] )) + ' ' + 
	  str('{:.3f}'.format(y[ikle[i,0]] )) + ' ' + 
	  str('{:.3f}'.format(z[ikle[i,0]] )) + ', ' +
	  
	  str('{:.3f}'.format(x[ikle[i,1]] )) + ' ' + 
	  str('{:.3f}'.format(y[ikle[i,1]] )) + ' ' + 
	  str('{:.3f}'.format(z[ikle[i,1]] )) + ',' +
	  
	  str('{:.3f}'.format(x[ikle[i,2]] )) + ' ' + 
	  str('{:.3f}'.format(y[ikle[i,2]] )) + ' ' + 
	  str('{:.3f}'.format(z[ikle[i,2]] )) + ', ' +
	  
	  str('{:.3f}'.format(x[ikle[i,0]] )) + ' ' + 
	  str('{:.3f}'.format(y[ikle[i,0]] )) + ' ' + 
	  str('{:.3f}'.format(z[ikle[i,0]] )) + '))",' + str(i+1) + '\n')
	
# to generate the node file
fout_n = open(output_file_n,"w")

# write the header of the WKT file\
fout_n.write('WKT,node' + '\n')

for i in range(n):
	fout_n.write('"POINT (')
	fout_n.write(str('{:.3f}'.format(x[i] )) + ' ' + 
	  str('{:.3f}'.format(y[i] )) + ' ' + 
	  str('{:.3f}'.format(z[i] )) + ')",' + 
	  str(i+1) + '\n')
