#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 probeshp.py                           # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Nov 13, 2016
#
# Purpose: Probes a shapefile, and outputs some metadata about the file.
# Note only the data about the first record is displayed!
#
# Uses: Python 2 or 3
#
# Example:
#
# python probeshp.py -i file.shp
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
from pyshp.shapefile import *              # pyshp class
#
# I/O
if len(sys.argv) == 3 :
	input_file = sys.argv[2]
else:
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python probeshp.py -i file.shp')
	sys.exit()

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

print('Fields:')
print(field_names)

# -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+		

# each shape has a value for each field name
records = sf.records()

# shapeid is initialized here
shapeid = -1

# set up an iterator (thanks to Joel Lawhead's email!)
for s in sf.iterShapes():
	
	# this is just a counter
	shapeid = shapeid + 1
	
print('Records: ' + str(shapeid+1))

