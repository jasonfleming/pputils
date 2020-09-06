#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 mkbreakline.py                        # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Sept 20, 2015
#
# Modified: Feb 21, 2016
# Made it work under python 2 or 3
#
# Purpose: Takes in nodes.csv and a pputils lines.csv file, and creates
# a 3d breakline in pputils csv format. To convert pputils breakline to
# a 3d breakline in dxf format, use breaklines2dxf.py script!
# 
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python mkbreakline.py -n nodes.csv -l lines.csv -o lines3d.csv 
#
# where
#       --> -n is the xyz file listing of all nodes (incl. embedded nodes) 
#       --> -l is the pputils input lines file (in 2d)
#       --> -o is the pputils output lines file (in 3d)
#       --> -i is an optional flag whether to interpolate for the missing
#                    nodes on the lines file. Sometimes topology cleaning
#                    in GRASS GIS will create additional nodes on the 
#                    breaklines that will have no z values. By default
#                    this interpolation is not done. The user has to specify
#                    -i 1 for it to take effect.
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy             as np             # numpy
from collections import OrderedDict        # for removal of duplicate nodes
from scipy import spatial                  # kd tree for searching coords
from progressbar import ProgressBar, Bar, Percentage, ETA
curdir = os.getcwd()
#
# I/O
if len(sys.argv) == 7 :
	dummy1 =  sys.argv[1]
	nodes_file = sys.argv[2]
	dummy2 =  sys.argv[3]
	lines_file = sys.argv[4]
	dummy3 =  sys.argv[5]
	output_file = sys.argv[6]
	dummy4 = ''
	interpolate_flag = 0 # do not interpolate for missing node values
elif len(sys.argv) == 9 :
	dummy1 =  sys.argv[1]
	nodes_file = sys.argv[2]
	dummy2 =  sys.argv[3]
	lines_file = sys.argv[4]
	dummy3 =  sys.argv[5]
	output_file = sys.argv[6]
	dummy4 = sys.argv[7]
	interpolate_flag = sys.argv[8] # interpolate for missing node values
	interpolate_flag = int(interpolate_flag)
else:
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python mkbreakline.py -n nodes.csv -l lines.csv -o lines3d.csv')
	sys.exit()

# find out if the nodes file is x,y,z or x,y,x,size
with open(nodes_file, 'r') as f:
    line = next(f) # read 1 line
    n_attr = len(line.split(','))

# to create the output file
fout = open(output_file,"w")

# use numpy to read the file
# each column in the file is a row in data read by no.loadtxt method
nodes_data = np.loadtxt(nodes_file, delimiter=',',skiprows=0,unpack=True)
lines_data = np.loadtxt(lines_file, delimiter=',',skiprows=0,unpack=True)

# master nodes in the file (from the nodes file)
x = nodes_data[0,:]
y = nodes_data[1,:]
z = nodes_data[2,:]
if (n_attr == 4):
	size = nodes_data[3,:]
else:
	size = np.zeros(len(x))
		
# n is the number of nodes
n = len(x)

# creates node numbers from the nodes file
node = np.zeros(n,dtype=np.int32)

# to check for duplicate nodes
# crop all the points to three decimals only
x = np.around(x,decimals=3)
y = np.around(y,decimals=3)
z = np.around(z,decimals=3)
size = np.around(size,decimals=3)

# this piece of code uses OrderedDict to remove duplicate nodes
# source "http://stackoverflow.com/questions/12698987"
# ###################################################################
tmp = OrderedDict()
for point in zip(x, y, z, size):
  tmp.setdefault(point[:2], point)

# in python 3 tmp.values() is a view object that needs to be 
# converted to a list
mypoints = list(tmp.values()) 
# ###################################################################
n_rev = len(mypoints)

# replace x,y,z,size and n with their unique equivalents
for i in range(n_rev):
	x[i] = mypoints[i][0]
	y[i] = mypoints[i][1]
	z[i] = mypoints[i][2]
	size[i] = mypoints[i][3]
n = n_rev

# when I made the change to python 3, had to use np.column_stack
# http://stackoverflow.com/questions/28551279/error-running-scipy-kdtree-example

# to create the tuples of the master points
points = np.column_stack((x,y))
tree = spatial.cKDTree(points)

shapeid_lns = lines_data[0,:]
shapeid_lns = shapeid_lns.astype(np.int32)
x_lns = lines_data[1,:]
y_lns = lines_data[2,:]
	
# round lines nodes to three decimals
x_lns = np.around(x_lns,decimals=3)
y_lns = np.around(y_lns,decimals=3)
	
# number of nodes in the lines file
n_lns = len(x_lns)

w = [Percentage(), Bar(), ETA()]
pbar = ProgressBar(widgets=w, maxval=n_lns).start()
# index for the minimum, for each lines node
minidx_lns = np.zeros(n_lns,dtype=np.int32) - 1

pt_lns = list()

for i in range(0,n_lns):
	pt_lns.append(x_lns[i])
	pt_lns.append(y_lns[i])
	
	# find the index of each lines point
	minidx_lns_temp = tree.query_ball_point(pt_lns, 0.01)
	
	if (len(minidx_lns_temp) > 0):
		minidx_lns[i] = minidx_lns_temp[0]
		
		fout.write(str(shapeid_lns[i]) + "," + str(x_lns[i]) + "," + 
			str(y_lns[i]) + "," +  str(z[minidx_lns[i]]) + "\n")
	else:
		if (interpolate_flag == 0):
			# simply insert -999.0 as the elevation (useful for finding problem spots
			print('Lines node ' + str(x_lns[i]) + ' ' + str(y_lns[i]) + ' not found')
			fout.write(str(shapeid_lns[i]) + "," + str(x_lns[i]) + "," + 
				str(y_lns[i]) + "," +  str('-999.0') + "\n")
		else:
			# interpolate the missing elevation
			# for now, simply assign the point that is closest (by distance)
			# to the lines node with the missing value
			
			# find the distance between the missing lines node and all of the
			# input nodes
			xdist = np.subtract(x,x_lns[i])
			ydist = np.subtract(y,y_lns[i])
			dist = np.sqrt(np.power(xdist,2.0) + np.power(ydist,2.0))
			minidx = np.argmin(dist)
			
			fout.write(str(shapeid_lns[i]) + "," + str(x_lns[i]) + "," + 
				str(y_lns[i]) + "," +  str(z[minidx]) + "\n")
		
	# to remove the node to search for
	pt_lns.remove(x_lns[i])
	pt_lns.remove(y_lns[i])	
	
	# update the pbar
	pbar.update(i+1)
	
pbar.finish()
