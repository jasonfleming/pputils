#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 adcirc2shp.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Feb 20, 2016
#
# Purpose: Script takes in a mesh in ADCIRC format, and generates a shp
# file using pyshp. The projection is not included, and will have to be
# specified by the user when loading the data to a GIS package. Similar
# to the adcirc2wkt.py, this script generates two different shapefiles 
# (one for the elements, and one for the nodes)
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python adcirc2shp.py -i out.grd -o out.shp
# where:
# -i input adcirc mesh file
# -o generated *.shp files for element polygons and nodes
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy             as np             # numpy
from ppmodules.readMesh import *           # to get all readMesh functions
from pyshp.shapefile import *              # pyshp class
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
#
# I/O
if len(sys.argv) != 5 :
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python adcirc2shp.py -i out.grd -o out.shp')
	sys.exit()
	
dummy1 =  sys.argv[1]
adcirc_file = sys.argv[2]
dummy2 =  sys.argv[3]
output_file = sys.argv[4] # output *.shp file

# create the element and node output files
output_file_e = output_file.rsplit('.',1)[0] + '_e.shp'
output_file_n = output_file.rsplit('.',1)[0] + '_n.shp'

# to create the output file
out_e = Writer(shapeType=15) # this is POLYGON
out_n = Writer(shapeType=1) # this is POINT

# read the adcirc file
n,e,x,y,z,ikle = readAdcirc(adcirc_file)

# write the nodes shapefile
out_n.field('id')
out_n.field('z')
for i in range(n):
	out_n.point(x[i],y[i])
	out_n.record(id=i+1, z=z[i])

out_n.save(output_file_n)	


# write the polygon shapefile



'''
for i in range(e):
	fout.write('"POLYGON ((')
	fout.write(str(x[ikle[i,0]]) + ' ' + str(y[ikle[i,0]]) + ' ' + str(z[ikle[i,0]]) + ',' +
		str(x[ikle[i,1]]) + ' ' + str(y[ikle[i,1]]) + ' ' + str(z[ikle[i,1]]) + ',' +
		str(x[ikle[i,2]]) + ' ' + str(y[ikle[i,2]]) + ' ' + str(z[ikle[i,2]]) + ',' +
		str(x[ikle[i,0]]) + ' ' + str(y[ikle[i,0]]) + ' ' + str(z[ikle[i,0]]) + '))",' + str(i+1) + '\n')
	
'''
