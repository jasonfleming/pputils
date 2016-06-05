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
# lines (also in pputils format), and outputs all line segments within 
# the closed polygon boundary. The script uses Matplotlib for point
# in poly test (same as assign_mpl.py).
#
# Uses: Python 2 or 3, Matplotlib, Numpy, Scipy
#
# Example:
#
# python crop_lns.py -n lines.csv -p polygon.csv -o lines_cropped.csv
# where:
# -n original lines file (comma delimited, pputils format)
# -p crop polygon (in pputils format)
# -o cropped to polygon lines file (comma delimited, pputils format)
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
	print('python crop_lns.py -n lines.csv -p polygon.csv -o lines_cropped.csv')
	sys.exit()
	
lines_file = sys.argv[2]
polygon_file = sys.argv[4]
output_file = sys.argv[6]

# to create the output file
fout = open(output_file,"w")

# read input file
lines_data = np.loadtxt(lines_file, delimiter=',',skiprows=0,unpack=True)

# find out if lines_file has z values or not
# the lines file is either shapeid,x,y or shapeid,x,y,z
n_attr = len(lines_data[:,0])

# find out the number of points in the lines file
n_lns = len(lines_data[0,:])

shapeid_lns = lines_data[0,:]
x_lns = lines_data[1,:]
y_lns = lines_data[2,:]

if (n_attr == 3):
	z_lns = np.zeros(n_lns)
else:
	z_lns = lines_data[3,:]

# crop all the lns points to three decimals only
x_lns = np.around(x_lns,decimals=3)
y_lns = np.around(y_lns,decimals=3)
z_lns = np.around(z_lns,decimals=3)

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
pbar = ProgressBar(widgets=w, maxval=n_lns).start()

for j in range(n_lns):
	poly_test = path.contains_point( (x_lns[j], y_lns[j]) )
	if (poly_test == True):
		fout.write(str(shapeid_lns[j]) + ',' + str(x_lns[j]) + ',' + 
			str(y_lns[j]) + ',' + str(z_lns[j]) + '\n')
	pbar.update(j+1)

pbar.finish()
	
print('All done!')


