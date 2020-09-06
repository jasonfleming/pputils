#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 interp_from_pts.py                    # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: May 26, 2016
#
# Purpose: Script takes in a xyz points file and a mesh file (in ADCIRC 
# format),  and interpolates the nodes of the mesh file from the points
# file. It uses scipy's kdtree to assign to the mesh node the point in
# the xyz dataset that is closest.
#
# Revised: May 27, 2016
# Made it such that a number of scipy neighbours is an input argument. If
# closest node is wanted, just use 1 neighbour. Note that this interpolation
# script is good only when data points file is very dense.
#
# Revised: Nov 13, 2016
# Fixed a division by zero error if the distance is exactly zero in the
# kdTree algorithm.
#
# Revised: Nov 21, 2016
# Changed KDTree to cKDTree to improve performance.
#
# Uses: Python 2 or 3, Matplotlib, Numpy
#
# Example:
#
# python interp_from_pts.py -p points.csv -m mesh.grd -o mesh_interp.grd -n 10
# where:
# -p xyz points file, no headers, comma delimited
# -m mesh (whose nodes are to be interpolated)
# -o interpolated mesh
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
	print('python interp_from_pts.py -p points.csv -m mesh.grd -o mesh_interp.grd -n 10')
	sys.exit()

pts_file = sys.argv[2]
mesh_file = sys.argv[4]
output_file = sys.argv[6] # interp_mesh
neigh = int(sys.argv[8]) # the number of nearest neighbours

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

# read the adcirc mesh file (_m is for mesh)
# this one has z values that are all zeros
m_n,m_e,m_x,m_y,m_z,m_ikle = readAdcirc(mesh_file)

print('Constructing KDTree object')
# to create a KDTree object
source = np.column_stack((x,y))
tree = spatial.cKDTree(source)

den = 0.0
tmp_sum = 0.0

print('Interpolating')
w = [Percentage(), Bar(), ETA()]
pbar = ProgressBar(widgets=w, maxval=m_n).start()
for i in range(m_n):
	d,idx = tree.query((m_x[i],m_y[i]), k = neigh)
	
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
	m_z[i] = tmp_sum
	
	# reset the denominator
	den = 0.0
	tmp_sum = 0.0
	
	pbar.update(i+1)
pbar.finish()

print('Writing results to file')
# to create the output file (this is the interpolated mesh)
fout = open(output_file,"w")

# now to write the adcirc mesh file
fout.write("ADCIRC" + "\n")
# writes the number of elements and number of nodes in the header file
fout.write(str(m_e) + " " + str(m_n) + "\n")

# writes the nodes
for i in range(0,m_n):
	fout.write(str(i+1) + " " + str("{:.3f}".format(m_x[i])) + " " + 
		str("{:.3f}".format(m_y[i])) + " " + str("{:.3f}".format(m_z[i])) + "\n")
#
# writes the elements
for i in range(0,m_e):
	fout.write(str(i+1) + " 3 " + str(m_ikle[i,0]+1) + " " + str(m_ikle[i,1]+1) + " " + 
		str(m_ikle[i,2]+1) + "\n")
print('All done!')
