#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 shp2csv.py                            # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Nov 1, 2016
#
# Purpose: Takes a shapefile of types polyline, polygon, polylinez, or
# polygonz and converts it to a pputils lines file. This script uses
# Joel Lawhead's pyshp (https://github.com/GeospatialPython/pyshp).
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

# these are the type ids for shapefiles
POINT = 1
POLYLINE = 3
POLYGON = 5

POINTZ = 11
POLYLINEZ = 13
POLYGONZ = 15

# print the type of the first object
shape_type = sf.shape(0).shapeType
print('The shapefile type of first shape is: ' + str(shape_type))

# write node files too in case of polygons or polylines
if (shape_type == 3 or shape_type == 5 or shape_type == 13 or shape_type == 15):
	nodes_file = output_file.rsplit('.',1)[0] + '_nodes.csv'
	fout2 = open(nodes_file, 'w')
	

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

# find 'z' or 'friction' attribute in the attr list
# if it finds it, assign index of the attr, otherwise the index is -1000

# this means that a user can not have both z and friction attributes in the file
# warn the user that friction attributes must be done with polygon files only!

for i in range(len(attr)):
	if (attr[i].find('z') > -1) or (attr[i].find('friction') > -1):
		locz = i
		break
	else:
		locz = -1000

# to print if the attr is found
# if (locz != -1000):
# 	print('attr is found at: ' + str(locz))
# else:
# 	print('attr is not found')
# -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+		


# each shape has a value for each attribute
records = sf.records()

# shapeid is initialized here
shapeid = -1

# set up an iterator (thanks to Joel Lawhead's email!)
for s in sf.iterShapes():
	
	# this is just a counter
	shapeid = shapeid + 1
	
	if (shape_type == POINTZ):
		xyz = s.points[0]
		xyz.append(s.z[0])
		
		fout.write(str(xyz[0]) + ',' +str(xyz[1]) + ',' +str(xyz[2]) + '\n')
		
	elif (shape_type == POINT):
		xyz = s.points[0]
		
		# if the data has an attribute z
		if (locz != -1000):
			fout.write(str(xyz[0]) + ',' +str(xyz[1]) + ',' + \
				str(records[shapeid][locz]) + '\n')
		else:
			fout.write(str(xyz[0]) + ',' +str(xyz[1]) + ',' +str(0.0) + '\n')
			
	if (shape_type == POLYLINE) or (shape_type == POLYGON):
		xyz = s.points
		
		# if the data has an attribute z write it to all nodes of each line
		# this is useful when processing contours with shapefiles
		if (locz != -1000):
			for j in range(len(xyz)):
				fout.write(str(shapeid) + ',' + str(xyz[j][0]) + ',' + \
					str(xyz[j][1]) + ',' +str(records[shapeid][locz]) + '\n')
				
				fout2.write(str(xyz[j][0]) + ',' + \
					str(xyz[j][1]) + ',' +str(records[shapeid][locz]) + '\n')
		else:
			for j in range(len(xyz)):
				fout.write(str(shapeid) + ',' + str(xyz[j][0]) + ',' +str(xyz[j][1]) + '\n')
				
				fout2.write(str(xyz[j][0]) + ',' +str(xyz[j][1]) + str(0,0) + '\n')
				
	if (shape_type == POLYLINEZ) or (shape_type == POLYGONZ):				
		xyz = s.points
		
		# polylineZ and polygonZ shapefiles are assumed not to have attributes
		for j in range(len(xyz)):
			fout.write(str(shapeid) + ',' + str(xyz[j][0]) + ',' +str(xyz[j][1]) + \
				',' + str(s.z[j]) + '\n')
			
			fout2.write(str(xyz[j][0]) + ',' +str(xyz[j][1]) + ',' + str(s.z[j]) + '\n')

print('All done!')

