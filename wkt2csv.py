#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 wkt2csv.py                            # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: July 23, 2015
#
# Updated: Oct 24, 2015 - added more -t options
#
# Purpose: Script takes in WKT (Well Known Text) csv file format (exported 
# by QGIS) and prepares the csv files for use in pputils
#
# Uses: Python2.7.9, Matplotlib v1.4.2, Numpy v1.8.2
#
# Example:
#
# python wkt2csv.py -i breaklineWKT.csv -t POINT -o breakline.csv 
# where:
# -i input WKT file csv file exported from QGIS
# -t type of WKT file (either POINT or LINESTRING)
# -o output csv file according to format used by pputils
# 
# If there are attributes in the shapefile, this program ignores them all.
# This conversion utility assumes that the original shapefiles are 2.5D,
# where the z value is part of the geometry, if present. If the
# z value is an attribute in the shapefile, then simply export it to csv 
# from QGIS, without exporting to WKT format.
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
from os import path
import matplotlib.tri    as mtri           # matplotlib triangulations
import numpy             as np             # numpy
import math                                # for the ceil function
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 7 :
	print 'Wrong number of Arguments, stopping now...'
	print 'Usage:'
	print 'python wkt2csv.py -i boundaryWKT.csv -t POINT -o boudary.csv'
	sys.exit()
dummy1 =  sys.argv[1]
input_file = sys.argv[2]
dummy2 = sys.argv[3]
wkt_type = sys.argv[4]
dummy2 =  sys.argv[5]
output_file = sys.argv[6]

# reads the input file using pure python
line = list()

attr_list = list()

with open(input_file, 'r') as f1:
	for i in f1:
	  line.append(i)
	  
# now write the lines files
fout = open('temp.txt', 'w')

n = len(line)

sep = ')"'

count = 0
temp = ''
tmp = ''

if (wkt_type == 'LINESTRING'):
	# ignores the first (header) line in the WKT file
	for i in range(1,n):
	  line[i] = line[i].replace('"LINESTRING (', '')
	  # ignores everythng past the separator 
	  line[i] = line[i].split(sep, 1)[0]	
	  #line[i] = line[i].replace(')"', '')
	  temp = line[i].split(',')
	
	  for j in range(len(temp)):
	    temp[j] = temp[j].replace(' ', ',')
	    fout.write(str(i) + ',' + str(temp[j]) + "\n")
	    #fout.write(str(temp[j]) + "\n")
		  
	# close the temp.txt file
	fout.close()

# this just outputs the nodes of the linestring file
elif (wkt_type == 'LINESTRING_XYZ'):
	# ignores the first (header) line in the WKT file
	for i in range(1,n):
	  line[i] = line[i].replace('"LINESTRING (', '')
	  # ignores everythng past the separator 
	  line[i] = line[i].split(sep, 1)[0]	
	  #line[i] = line[i].replace(')"', '')
	  temp = line[i].split(',')
	
	  for j in range(len(temp)):
	    temp[j] = temp[j].replace(' ', ',')
	    count = temp[j].count(',')		
  
	    if (count < 2):
	      tmp = str(temp[j]) + str(',0') + "\n"
	    else:
	      tmp = str(temp[j]) + "\n"
	  
	    fout.write(tmp)
	  	
		  
	# close the temp.txt file
	fout.close()

elif (wkt_type == 'POLYGON'):
	# for wkt type polygon, the separator is different
	sep = '))"'

	# ignores the first (header) line in the WKT file
	for i in range(1,n):
	  line[i] = line[i].replace('"POLYGON ((', '')
	  
	  # ignores everythng past the separator 
	  line[i] = line[i].split(sep, 1)[0]	
	  #line[i] = line[i].replace(')"', '')
	  temp = line[i].split(',')
	
	  for j in range(len(temp)):
	    temp[j] = temp[j].replace(' ', ',')
	    count = temp[j].count(',')		
  
	    if (count < 2):
	      tmp = str(temp[j]) + str(',0') + "\n"
	    else:
	      tmp = str(temp[j]) + "\n"
	  
	    fout.write(str(i) + ',' + tmp)
		  
	# close the temp.txt file
	fout.close()
	
elif (wkt_type == 'POLYGON_XYZ'):
	# for wkt type polygon, the separator is different
	sep = '))"'

	# ignores the first (header) line in the WKT file
	for i in range(1,n):
	  line[i] = line[i].replace('"POLYGON ((', '')
	  
	  # ignores everythng past the separator 
	  line[i] = line[i].split(sep, 1)[0]	
	  #line[i] = line[i].replace(')"', '')
	  temp = line[i].split(',')
	
	  for j in range(len(temp)):
	    temp[j] = temp[j].replace(' ', ',')
	    count = temp[j].count(',')		
  
	    if (count < 2):
	      tmp = str(temp[j]) + str(',0') + "\n"
	    else:
	      tmp = str(temp[j]) + "\n"
	  
	    fout.write(str(i) + ',' + tmp)
		  
	# close the temp.txt file
	fout.close()
	
# this is the case where the first attribute in the polygon is assigned
# to each node as the z-value	
elif (wkt_type == 'POLYGON_ATTR'):
	# for wkt type polygon, the separator is different
	#sep = '))"'
	attr_sep = '))",'

	# ignores the first (header) line in the WKT file
	for i in range(1,n):
		line[i] = line[i].replace('"POLYGON ((', '')
		
		# gets the polygon attribute
		# uses rsplit (gets the value starting from the right)
		attr = line[i].rsplit(attr_sep)[-1]
		
		# strip the \n from each
		attr = attr.replace('\n', '')
		
	  # ignores everythng past the separator 
		line[i] = line[i].split(attr_sep, 1)[0]
		
		#line[i] = line[i].replace(')"', '')
		temp = line[i].split(',')
	
		for j in range(len(temp)):
			temp[j] = temp[j].replace(' ', ',')
			fout.write(str(i) + ',' + str(temp[j]) + ',' + attr + '\n')
		  
	# close the temp.txt file
	fout.close()
	
elif (wkt_type == 'POINT'):
	# ignores the first (header) line in the WKT file
	for i in range(1,n):
	  line[i] = line[i].replace('"POINT (', '')
	  # ignores everythng past the separator 
	  line[i] = line[i].split(sep, 1)[0]	
	  #line[i] = line[i].replace(')"', '')
	  temp = line[i].split(',')
	
	  for j in range(len(temp)):
	    temp[j] = temp[j].replace(' ', ',')
	    fout.write(str(temp[j]) + "\n")
		  
	# close the temp.txt file
	fout.close()
	
elif (wkt_type == 'POINT_XYZ'):
	
	val = ''
	
	# ignores the first (header) line in the WKT file
	for i in range(1,n):
	  line[i] = line[i].replace('"POINT (', '')
	  # stores the z value as a string
	  val = line[i].split(')",', 1)[1]	
	  # ignores everythng past the separator 
	  line[i] = line[i].split(sep, 1)[0]	
	  temp = line[i].split(',')
	
	  for j in range(len(temp)):
	    temp[j] = temp[j].replace(' ', ',')
	    fout.write(str(temp[j] + ',' + val) + "\n")
		  
	# close the temp.txt file
	fout.close()	

# delete temp
del temp

# the output file
fout2 = open(output_file, 'w')

# open the temp.txt file, and get rid of any blanks
with open('temp.txt', 'r') as f2:
  for line2 in f2:
    if (line2.strip()):
      fout2.write(line2)
		
# delete temp.txt
os.remove('temp.txt')
