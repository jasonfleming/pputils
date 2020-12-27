#!/usr/bin/env python3
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
# Purpose: Script takes in a mesh in ADCIRC format, and a set of closed
# boundaries in pputils format, and creates another ADCIRC file with
# node z-values assigned with polygon attributes. This is useful for 
# delineating friction zones in GIS, and applying them to the mesh.
#
# Modified: Oct 26, 2015
# The original version assumed that each polygon has a distinct attribute.
#
# Modified: Feb 21, 2016
# Changed ProgressBar, and updated for python 2 and 3.
#
# Modified: Aug 27, 2020
# Changed so that default value is the original value read from the 
# ADCIRC file. What gets modified is only what is contained in the 
# polygon. This is different than how it used to be in the previous 
# version, where values outside the polygon were assigned a default
# value that was hard coded. This version retains the original values
# for nodes outside of the polygons.
#
# Modified: Nov 1, 2020
# The previous revision had a bug when two polygons were used (when it
# got to the second polygon, it didn't remember the updates made in the
# first polygon). This is now fixed.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python assign.py -i out.grd -b boundary.csv -o out_friction.grd
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
from progressbar import ProgressBar, Bar, Percentage, ETA
import timeit
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
curdir = os.getcwd()
start_time = timeit.default_timer()
#
# I/O
if len(sys.argv) != 7 :
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python assign.py -i out.grd -b boundary.csv -o out_friction.grd')
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

# find out how many different polygons there are
n_polygons = len(polygon_ids)

# to get the attribute data for each polygon
attribute_data = np.zeros(n_polygons)
attr_count = -1

# this is really bad programming, but it will have to do for now!
# TODO must fix this!
# go through the polygons, and assign attribute_data 
for i in range(nodes-1):
  #print str(shapeid_poly[i]) + ' ' + str(shapeid_poly[i+1])
  if (shapeid_poly[i] - shapeid_poly[i+1] < 0):
    attr_count = attr_count + 1
    attribute_data[attr_count] = attr_poly[i]
    
# manually assign the attribute_data for the last polygon
attribute_data[n_polygons-1] = attr_poly[nodes-1]

# default attribute
default = 0.0

# define the mesh attribute as the value read from the file
f = z

# for the progress bar
w = [Percentage(), Bar(), ETA()]
pbar = ProgressBar(widgets=w, maxval=n_polygons*n).start()
count_bar = 0

# loop over all polygons
for i in range(n_polygons):
  # construct each polygon
  poly = []
  for j in range(nodes):
    if (shapeid_poly[j] == polygon_ids[i]):
      poly.append( (x_poly[j], y_poly[j]) )
  #print(poly)
  
  # to loop over all nodes in the mesh (inneficient)
  # TODO remove the brute force component of this code!!!
  for k in range(n):
    count_bar = count_bar + 1
    pbar.update(count_bar)
    poly_test = point_in_poly(x[k], y[k], poly)
    if (poly_test == 'IN'):
      f[k] = attribute_data[i]
    elif (poly_test == 'OUT'):
      f[k] = f[k]
    else:
      f[k] = -999
  
  # delete all elements in the poly list
  del poly[:]    
  #print '###########'

# finish the bar
pbar.finish()

# if a particular node of the mesh was not within any polygon
# extract all values that were less then the condition f-default < 0.001
# outside_test = np.extract(f-default < 0.001,f)

#if (len(outside_test) > 0):
#  print('Warning: some nodes were not within any of the input polygons!')
#  print('Assigning default value of ' + str(default) + ' as attribute')

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
end_time = timeit.default_timer()
#print('execution time is ' + str(end_time - start_time))
