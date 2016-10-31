#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 shp2csv.py                            # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Oct 30, 2016
#
# Purpose: Takes a shapefile of types polyline, polygon, polylinez, or
# polygonz and converts it to a pputils lines file. This utility uses
# pyshp (https://github.com/GeospatialPython/pyshp). FThis script only
# works for lines files. Does not read z values in polylineZ or polygonZ.
# It also does not read shapefile attributes.
#
# Uses: Python 2 or 3
#
# Example:
#
# python shp2csv.py -i file.shp -o file.csv
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
from pyshp.shapefile import *
#
# I/O
if len(sys.argv) == 5 :
	input_file = sys.argv[2]
	output_file = sys.argv[4]
else:
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python shp2csv.py -i file.shp -o file.csv')
	sys.exit()

# to create the output file
fout = open(output_file, 'w')

# read the shapefile using pyshp reader
sf = Reader(input_file)

# get the shape type of each shape
shapes = sf.shapes()

# these are the type ids for shapefiles
POINT = 1
POLYLINE = 3
POLYGON = 5

POINTZ = 11
POLYLINEZ = 13
POLYGONZ = 15

# print the id of the first 10 shapes
#for i in range(10):
#	print(shapes[i].shapeType)

# shapeid is initialized here
shapeid = 0

for i in range(len(shapes)):
	# increment the shapeid counter
	shapeid = shapeid + 1

	if (shapes[i].shapeType == 3) or (shapes[i].shapeType == 5) or \
		(shapes[i].shapeType == 13) or (shapes[i].shapeType == 15):
			
		# gets all of the coordinates as a list	
		lst = shapes[i].points
		
		# writes the coordinates to the pputils lines file
		for j in range(len(lst)):
			fout.write(str(shapeid) + ',' + str(lst[j][0]) + ',' + str(lst[j][1]) + '\n')
print('All done!')

# these are the attribute names
#fields = sf.fields
#print(fields)

# these are its attributes
#records = sf.records()
#print(records[0])

