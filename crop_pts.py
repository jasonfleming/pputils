#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 crop_pts.py                           # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Jun 5, 2016
# Purpose: Takes in a closed polygon (in pputils format), and a set of
# xyz points, and outputs all points within the closed polygon. The
# script uses Matplotlib for point in poly test (same as assign_mpl.py).
#
# Uses: Python 2 or 3, Matplotlib, Numpy, Scipy
#
# Example:
#
# python crop_pts.py -n points.csv -p polygon.csv -o points_cropped.csv
# where:
# -n original xyz file (comma delimited)
# -p crop polygon (in pputils format)
# -o cropped to polygon xyz file (comma delimited)
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import matplotlib.path as mplPath
import numpy as np
from progressbar import ProgressBar, Bar, Percentage, ETA
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# I/O
if len(sys.argv) != 7 :
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python crop_pts.py -n points.csv -p polygon.csv -o points_cropped.csv')
  sys.exit()
  
input_file = sys.argv[2]
polygon_file = sys.argv[4]
output_file = sys.argv[6]

# to create the output file
fout = open(output_file,"w")

# read input file
input_data = np.loadtxt(input_file, delimiter=',',skiprows=0,unpack=True)

# master nodes in the file (from the nodes file)
x = input_data[0,:]
y = input_data[1,:]
z = input_data[2,:]
n = len(x)

# crop all the points to three decimals only
x = np.around(x,decimals=3)
y = np.around(y,decimals=3)
z = np.around(z,decimals=3)

# read polygon file
poly_data = np.loadtxt(polygon_file, delimiter=',',skiprows=0,unpack=True)

# polygon data
shapeid_poly = poly_data[0,:]
x_poly = poly_data[1,:]
y_poly = poly_data[2,:]

# crop all the polygon points to three decimals only
x_poly = np.around(x_poly,decimals=3)
y_poly = np.around(y_poly,decimals=3)

# get the unique polygon ids
polygon_ids = np.unique(shapeid_poly)

# find out how many different polygons there are
n_polygons = len(polygon_ids)

if (n_polygons > 1):
  print('Number of polygons in input file greater than 1. Exiting.')
  sys.exit()
  
# construct a polygon as mpl object
poly = list()
for i in range(len(shapeid_poly)):
  poly.append( (x_poly[i], y_poly[i]) )
  
# convert poly list to a numpy array
poly_array = np.asarray(poly)

# create a mathplotlib path object
path = mplPath.Path(poly_array)

# for the progress bar
w = [Percentage(), Bar(), ETA()]
pbar = ProgressBar(widgets=w, maxval=n).start()

for j in range(n):
  poly_test = path.contains_point( (x[j], y[j]) )
  if (poly_test == True):
    fout.write( str(x[j]) + ',' + str(y[j]) + ',' + str(z[j]) + '\n')
  pbar.update(j+1)

pbar.finish()

print('All done!')


