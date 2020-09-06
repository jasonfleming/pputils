#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 interpBreakline_from_pts.py           # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Nov 6, 2016
#
# Purpose: Script takes in a xyz points file and a breakline file (in 
# pputils format),  and interpolates the nodes of the breakline file 
# from the points file. It uses scipy's kdtree to assign to breakline
# nodes the point in the xyz dataset that is closest. It is similar to
# the interp_from_pts.py, except rather than a mesh, the input is a
# breakline file. Used primarily to assign nodes to a TIN crop boundary.
# If wanting to interpolate breaklines from a TIN, use interpBreakline.py
# script. This script does exactly the same thing as the mkbreakline.py 
# script with the interpolation flag on, but does it in a slightly 
# different way.
#
# Revised: Nov 13, 2016
# Fixed a division by zero error if the distance is exactly zero in the
# kdTree algorithm.
#
# Revised: Nov 21, 2016
# Changed KDTree to cKDTree to improve performance.
#
# Revised: Dec 3, 2016
# Added the station variable in the output.
#
# Uses: Python 2 or 3, Matplotlib, Numpy
#
# Example:
#
# python interpBreakline_from_pts.py -p points.csv -l lines.csv -o lines_3d.csv -n 10
# where:
# -p xyz points file, no headers, comma delimited
# -l lines file (to be interpolated)
# -o interpolated lines file (id,x,y,z,sta)
# -n number of nearest neighbours
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy             as np             # numpy
from scipy import spatial                  # scipy to get kdTree
from ppmodules.readMesh import *           # to get all readMesh functions
from progressbar import ProgressBar, Bar, Percentage, ETA
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 9 :
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python interpBreakline_from_pts.py -p points.csv -l lines.csv -o lines_3d.csv -n 10')
	sys.exit()

pts_file = sys.argv[2]
lines_file = sys.argv[4]
output_file = sys.argv[6]
neigh = int(sys.argv[8])

# I am imposing a limit on neigh to be between 1 and 10
if ((neigh < 1) or (neigh > 10)):
	print('Number of neighbours must be between 1 and 10. Exiting.')
	sys.exit(0)

print('Reading input data')
# read the points file
pts_data = np.loadtxt(pts_file, delimiter=',',skiprows=0,unpack=True)
x = pts_data[0,:]
y = pts_data[1,:]
z = pts_data[2,:]

# read the lines file
lines_data = np.loadtxt(lines_file, delimiter=',',skiprows=0,unpack=True)
shapeid = lines_data[0,:]
shapeid = shapeid.astype(np.int32)
lns_x = lines_data[1,:]
lns_y = lines_data[2,:]
lns_z = np.zeros(len(lns_x))

# create the new output variables
sta = np.zeros(len(lns_x))
tempid = np.zeros(len(lns_x))
dist = np.zeros(len(lns_x))

print('Constructing KDTree object')
# to create a KDTree object our of the xyz points file
source = np.column_stack((x,y))
tree = spatial.cKDTree(source)

den = 0.0
tmp_sum = 0.0

print('Interpolating')
w = [Percentage(), Bar(), ETA()]
pbar = ProgressBar(widgets=w, maxval=len(lns_x)).start()
for i in range(len(lns_x)):
	d,idx = tree.query((lns_x[i],lns_y[i]), k = neigh)
	
	# calculate the denominator
	if neigh > 1:
		for j in range(neigh):
			if (d[j] < 1.0E-6):
				d[j] = 1.0E-6			
			den = den + (1.0 / (d[j]**2))
	else:
		if (d < 1.0E-6):
			d = 1.0E-6		
		den = den + (1.0 / (d**2))
		
	# calculate the weights
	weights = (1.0 / d**2) / den
	
	# to assign the interpolated value
	if neigh > 1:
		for j in range(neigh):
			tmp_sum = tmp_sum + weights[j]*z[idx[j]]
	else:
		tmp_sum = weights * z[idx]
		
	# now assign the value	
	lns_z[i] = tmp_sum
	
	# reset the denominator
	den = 0.0
	tmp_sum = 0.0
	
	pbar.update(i+1)
pbar.finish()

print('Writing results to file')
# to create the output file (this is the interpolated mesh)
fout = open(output_file,'w')

# to create the sta array
sta[0] = 0.0
tempid = shapeid
dist[0] = 0.0

for i in range(1,len(lns_x)):
	if (tempid[i] - shapeid[i-1] < 0.001):
		xdist = lns_x[i] - lns_x[i-1]
		ydist = lns_y[i] - lns_y[i-1]
		dist[i] = np.sqrt(np.power(xdist,2.0) + np.power(ydist,2.0))
		sta[i] = sta[i-1] + dist[i]

# to round the numpy arrays to three decimal spaces
lns_x = np.around(lns_x,decimals=3)
lns_y = np.around(lns_y,decimals=3)
lns_z = np.around(lns_z,decimals=3)
dist = np.around(dist,decimals=3)
sta = np.around(sta,decimals=3)

# now to write the interpolated lines file (and its node values)
for i in range(len(lns_x)):
	fout.write(str(shapeid[i]) + ',' + str(lns_x[i]) + ',' + \
		str(lns_y[i]) + ',' +  str(lns_z[i]) + ',' + str(sta[i]) + '\n')
		
print('All done!')

