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
# Modified: Nov 10, 2016
# Rather than searching for 'z' as the field name, write all field names
# for all records in the shapefile (only for 2D shapefile types). 3D
# shapefiles are assumed not have any field names!
#
# Purpose: Takes a shapefile of types POINT, POLYLINE, POLYGON, 
# POINTZ, POLYLINEZ, or POLYGONZ and converts it to a pputils file(s).
# The script also automatically creates the nodes file (in case the
# input file is a lines file (POLYLINE, POLYGON, POLYLINE, and POLYGONZ).
# This script uses Joel Lawhead's pyshp, available through GitHub on:
# https://github.com/GeospatialPython/pyshp
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

if (shape_type == 1):
	print('Type: ' + 'POINT')
elif (shape_type == 3):
	print('Type: ' + 'POLYLINE')
elif (shape_type == 5):
	print('Type: ' + 'POLYGON')
elif (shape_type == 11):
	print('Type: ' + 'POINTZ')
elif (shape_type == 13):
	print('Type: ' + 'POLYLINEZ')
elif (shape_type == 15):
	print('Type: ' + 'POLYGONZ')
else:
	print('Unknown type. Exiting!')
	sys.exit(0)	

# write node files too in case of polygons or polylines
if (shape_type == 3 or shape_type == 5 or shape_type == 13 or shape_type == 15):
	nodes_file = output_file.rsplit('.',1)[0] + '_nodes.csv'
	fout2 = open(nodes_file, 'w')
	

# -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# these are the fields
fields = sf.fields

# ignore the first (the first one is a dummy)
fields = fields[1:]

# number of fields
nf = len(fields)

# the list of field names
field_names = list()

# assigns the fields to the list of field names
for i in range(nf):
	field_names.append(fields[i][0])

print('The shapefile has the following fields:')
print(field_names)
print(' ')

# -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+		

# each shape has a value for each field name
records = sf.records()

# shapeid is initialized here
shapeid = -1

# set up an iterator (thanks to Joel Lawhead's email!)
for s in sf.iterShapes():
	
	# this is just a counter
	shapeid = shapeid + 1
	
	# if the shapefile is of type POINTZ, field names are not written
	if (shape_type == POINTZ):
		xyz = s.points[0]
		xyz.append(s.z[0])
		
		fout.write(str(xyz[0]) + ',' +str(xyz[1]) + ',' +str(xyz[2]) + '\n')
		
	elif (shape_type == POINT):
		xyz = s.points[0]
		
		# write all fields for all records in the POINT file
		# write the coordinates
		fout.write(str(xyz[0]) + ',' +str(xyz[1]))
		
		if (len(field_names) > 0):
			for i in range(len(field_names)):
				fout.write(',' + str(records[shapeid][i]))
				if (i == len(field_names)-1):
					fout.write('\n')
		else:
			fout.write(',' + str(0.0) + '\n')
			
	if (shape_type == POLYLINE) or (shape_type == POLYGON):
		xyz = s.points
		
		# if the data has an attribute z write it to all nodes of each line
		# this is useful when processing contours with shapefiles

		for j in range(len(xyz)):
			fout.write(str(shapeid) + ',' + str(xyz[j][0]) + ',' + str(xyz[j][1]))
			if (len(field_names) > 0):
				for i in range(len(field_names)):
					fout.write(',' + str(records[shapeid][i]))
					if (i == len(field_names)-1):
						fout.write('\n')
			else:
				fout.write(',' + str(0.0) + '\n')			
				
		# to write the nodes file (same as above, but without shapeid)
		for j in range(len(xyz)):
			fout2.write(str(xyz[j][0]) + ',' + str(xyz[j][1]))
			if (len(field_names) > 0):
				for i in range(len(field_names)):
					fout2.write(',' + str(records[shapeid][i]))
					if (i == len(field_names)-1):
						fout2.write('\n')
			else:
				fout2.write(',' + str(0.0) + '\n')			
			
	if (shape_type == POLYLINEZ) or (shape_type == POLYGONZ):				
		xyz = s.points
		
		# polylineZ and polygonZ shapefiles are assumed not to have fields
		for j in range(len(xyz)):
			fout.write(str(shapeid) + ',' + str(xyz[j][0]) + ',' + \
				str(xyz[j][1]) + ',' + str(s.z[j]) + '\n')
			
			fout2.write(str(xyz[j][0]) + ',' +str(xyz[j][1]) + ',' + \
				str(s.z[j]) + '\n')

