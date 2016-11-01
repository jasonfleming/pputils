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
# pyshp (https://github.com/GeospatialPython/pyshp). This script does 
# not yet read z values in polylineZ or polygonZ or pointZ types.
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
from pyshp.shapefile import *              # pyshp class
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

# get properties of each shape
shapes = sf.shapes()

print(len(shapes))

# these are the type ids for shapefiles
POINT = 1
POLYLINE = 3
POLYGON = 5

POINTZ = 11
POLYLINEZ = 13
POLYGONZ = 15

# print the type of the first object
print('The shapefile type of first shape is: ')
print(shapes[0].shapeType)

# -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# these are the fields (or attributes)
fields = sf.fields

# ignore the first (the first one is a dummy)
fields = fields[1:]

# number of fields
nf = len(fields)

# the list of attributes
attr = list()

# assigns the attributes to the list
for i in range(nf):
	attr.append(fields[i][0])

print('The shapefile has the following attributes:')
print(attr)
print(' ')

# find 'z' attribute in the attr list
# if it finds it, assign index of the attr, otherwise the index is -1000
for i in range(len(attr)):
	if (attr[i].find('z') > -1):
		locz = i
		break
	else:
		locz = -1000

# to print if the z attr is found
if (locz != -1000):
	print('attr z is found at: ' + str(locz))
else:
	print('attr z is not found')
# -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+		


# each shape has values for each attribute
records = sf.records()

# shapeid is initialized here
shapeid = 0

for i in range(len(shapes)):
	# increment the shapeid counter
	shapeid = shapeid + 1
	
	# gets all of the coordinates as a list	
	lst = shapes[i].points

	# these are polyline and polygon
	if (shapes[i].shapeType == POLYLINE) or (shapes[i].shapeType == POLYGON):
		if (locz != -1000):
			
			# if shapefile has the z attribute, write z with the coordinates
			# this is useful when the shapefiles are contours
			
			# writes the coordinates to the pputils lines file, with z attr
			for j in range(len(lst)):
				fout.write(str(shapeid) + ',' + str(lst[j][0]) + ',' + \
					str(lst[j][1]) +  ',' + str(records[i][locz]) + '\n')
		else:
			# writes the coordinates to the pputils lines file, no z attr
			for j in range(len(lst)):
				fout.write(str(shapeid) + ',' + str(lst[j][0]) + ',' + \
					str(lst[j][1]) + '\n')
	
	elif (shapes[i].shapeType == POINT):
		if (locz != -1000):
			
			# if shapefile has the z attribute, write z with the coordinates
			# this is useful when the shapefiles are contours
			
			# writes the coordinates to the pputils points file, with z attr
			for j in range(len(lst)):
				fout.write(str(lst[j][0]) + ',' + str(lst[j][1]) +  ',' + str(records[i][locz]) + '\n')
		else:
			# writes the coordinates to the pputils lines file, no z attr
			# I can't think of the situation that a shapefile of type POINT
			# would be used without a z attribute in pputils, but its included
			# here for completeness
			for j in range(len(lst)):
				fout.write(str(lst[j][0]) + ',' + \
					str(lst[j][1]) + ',' + '0.0' + '\n')	
				
	# these are polylinez and polygonz
	# these will not need to have attributes assigned to them, as they have
	# z values associated with each node
	if (shapes[i].shapeType == POLYLINEZ) or (shapes[i].shapeType == POLYGONZ):
		
		# writes the coordinates to the pputils lines file, no z attr
		for j in range(len(lst)):
			fout.write(str(shapeid) + ',' + str(lst[j][0]) + ',' + \
				str(lst[j][1]) + ',' + str(0.0) + '\n')			

	elif (shapes[i].shapeType == POINTZ):
		for j in range(len(lst)):
			fout.write(str(lst[j][0]) + ',' + \
				str(lst[j][1]) + ',' + '0.0' + '\n')
		
				
print('All done!')

