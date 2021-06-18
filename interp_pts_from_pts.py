#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 interp_pts_from_pts.py                # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: May 4, 2021
#
# Purpose: Script takes in an input points file (xyz with z=-999) and 
# an input points file (xyz with z=non missing), and assigns to the
# input nodes the closest elevation non missing z value file. It uses
# scipy's kdtree to assign to the mesh node the point in the xyz dataset
# that is closest.
#
# Uses: Python 2 or 3, Matplotlib, Numpy
#
# Example:
#
# python interp_from_pts.py -i points_xy.csv -z bathy.xyz -o points_xyz.csv -n 10
# where:
# -i input xyz points file, no headers, comma delimited, no elevation
# -z input xyz points file no headers, comma delimited, with elevation
# -o output file (points_xy.csv interpolated)
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy             as np             # numpy
from scipy import spatial                  # scipy to get kdTree
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
	print('python interp_from_pts.py -i points_xy.csv -z bathy.xyz -o points_xyz.csv -n 10')
	sys.exit()

pts_file = sys.argv[2]
bathy_file = sys.argv[4]
output_file = sys.argv[6] # interp_mesh
neigh = int(sys.argv[8]) # the number of nearest neighbours

# I am imposing a limit on neigh to be between 1 and 10
if ((neigh < 1) or (neigh > 10)):
	print('Number of neighbours must be between 1 and 10. Exiting.')
	sys.exit(0)

print('Reading input data')
# read the points file (this one doesn't have elevation values)
pts_data = np.loadtxt(pts_file, delimiter=',',skiprows=0,unpack=True)
ix = pts_data[0,:]
iy = pts_data[1,:]
iz = np.zeros(len(ix))

# read the bathy points data (this one has elevation values)
bathy_data = np.loadtxt(bathy_file, delimiter=',',skiprows=0,unpack=True)
x = bathy_data[0,:]
y = bathy_data[1,:]
z = bathy_data[2,:]

print('Constructing KDTree object')
# to create a KDTree object
source = np.column_stack((x,y))
tree = spatial.cKDTree(source)

den = 0.0
tmp_sum = 0.0

print('Interpolating')
w = [Percentage(), Bar(), ETA()]
pbar = ProgressBar(widgets=w, maxval=len(ix)).start()
for i in range(len(ix)):
	d,idx = tree.query((ix[i],iy[i]), k = neigh)
	
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
	iz[i] = tmp_sum
	
	# reset the denominator
	den = 0.0
	tmp_sum = 0.0
	
	pbar.update(i+1)
pbar.finish()

print('Writing results to file')
# to create the output file (this is the interpolated mesh)
fout = open(output_file,"w")

# now to write the adcirc mesh file
for i in range(len(ix)):
  fout.write(str(ix[i]) + ',' + str(iy[i]) + ',' + str(iz[i]) + '\n')
