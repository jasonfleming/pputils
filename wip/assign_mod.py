#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 assign.py                             # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Oct 25, 2015
#
# Purpose: Script takes in a mesh in ADCIRC format, and a set of closed
# boundaries in pputils format, and creates another ADCIRC file with
# node values assigned via polygon boundaries. This is useful for defining
# friction zones in GIS, and applying them to the mesh node values.
#
# If some of the mesh nodes fall outside of the polygon boundaries, the
# default value (zero) is assigned to those nodes. Zero is hard coded,
# but could easily be changed.
#
# The newly created ADCIRC file has to be converted to *.slf, then be 
# used in the append.py script to generate the friction file for use in
# Telemac modeling.
#
# Uses: Python2.7.9, Matplotlib v1.4.2, Numpy v1.8.2
#
# Example:
#
# python adcirc2asc.py -i out.grd -b boundary.csv -o out_friction.grd
# where:
#
# -i input adcirc mesh file
# -b input boundary file (where each polygon has an attribute value to 
#    be assigned to the mesh
# -o output adcirc mesh file containing the attribute as the z value
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy             as np             # numpy
from ppmodules.readMesh import *           # to get all readMesh functions
from ppmodules.utilities import *          # to get the general utilities
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
	print 'python adcirc2asc.py -i out.grd -b boundary.csv -o out_friction.grd'
	sys.exit()
dummy1 =  sys.argv[1]
input_file = sys.argv[2]
dummy2 =  sys.argv[3]
boundary_file = sys.argv[4]
dummy3 = sys.argv[5]
output_file = sys.argv[6]


# to create the output file
fout = open(output_file,"w")

# read the adcirc file
n,e,x,y,z,ikle = readAdcirc(input_file)

# use numpy to read the boundary polygon file in pputils format
poly_data = np.loadtxt(boundary_file, delimiter=',',skiprows=0,unpack=True)

# boundary data
shapeid_poly = poly_data[0,:]
x_poly = poly_data[1,:]
y_poly = poly_data[2,:]
attr_poly = poly_data[3,:]

# round boundary nodes to three decimals
x_poly = np.around(x_poly,decimals=3)
y_poly = np.around(y_poly,decimals=3)

# total number of nodes in the polygon file
nodes = len(x_poly)

# get the unique polygon ids
polygon_ids = np.unique(shapeid_poly)

# to get the attribute data
attribute_data = np.unique(attr_poly)

# find out how many different polygons there are
n_polygons = len(polygon_ids)

# to find out how many different attributes
n_attr = len(attribute_data)

if (n_polygons != n_attr):
	sys.exit()

# default attribute
default = 0.0

# define the mesh attribute
f = np.zeros(n) * default # n is number of mesh nodes

# convert mesh x and y to list
x_lst = x.tolist()
y_lst = y.tolist()

# loop over all polygons
for i in range(n_polygons):
	# constrct each polygon
	poly = []
	for j in range(nodes):
		if (shapeid_poly[j] == polygon_ids[i]):
			poly.append( (x_poly[j], y_poly[j]) )
	#print poly
	
	# to loop over all nodes in the mesh (inneficient)
	# TODO remove the brute force component of this code!!!
	#for k in range(n):
	
	k = -1 # counter for the while loop
	count = 0
	while True:
		k = k + 1
		poly_test = point_in_poly(x_lst[k], y_lst[k], poly)
		if (poly_test == 'IN'):
			f[k] = attribute_data[i]
			del x_lst[k]
			del y_lst[k]
		else:
			count = count +1
		
		if ( count == n-count):
			break
		print 'index k : ' + str(k) + '; len list ' + str(len(x_lst)) 
			
			
	
	# delete all elements in the poly list
	del poly[:]		
	#print '###########'

# if a particular node of the mesh was not within any polygon
# extract all values that were less then the condition f-default < 0.001
outside_test = np.extract(f-default < 0.001,f)

if (len(outside_test) > 0):
	print 'Warning: some nodes were not within any of the input polygons!'
	print 'Assigning default value of ' + str(default) + ' as attribute'

# now to write the adcirc mesh file
fout.write("ADCIRC" + "\n")
# writes the number of elements and number of nodes in the header file
fout.write(str(e) + " " + str(n) + "\n")

# writes the nodes
for i in range(n):
	fout.write(str(i+1) + " " + str("{:.3f}".format(x[i])) + " " + 
		str("{:.3f}".format(y[i])) + " " + str("{:.3f}".format(f[i])) + "\n")
#
# writes the elements
for i in range(e):
	fout.write(str(i+1) + " 3 " + str(ikle[i,0]+1) + " " + str(ikle[i,1]+1) + " " + 
		str(ikle[i,2]+1) + "\n")	
#
