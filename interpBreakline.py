#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 interpBreakline.py                    # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: June 28, 2015
#
# Purpose: Script takes in a tin (in ADCIRC format), and a pputils lines 
# file (shapeid,x,y), and interpolates z values from tin. When extracting
# cross sections, the lines file should be resampled at a large number 
# of nodes (say 100), or at specific features in order to get a properly
# extracted cross section for hydraulic modeling.
#
# Modified: Feb 20, 2016
# Made it work for python 2 and 3
#
# Modified: Nov 6, 2016
# Changed name from extractxs.py to interpBreakline.py
#
# Uses: Python 2 or 3, Matplotlib, Numpy
#
# Example:
#
# python interpBreakline.py -t tin.grd -l lines.csv -o lines_z.csv
# where:
# -t tin surface
# -l resampled cross section lines file (in pputils format, shapeid,x,y)
# -o cross section lines file (shapeid,x,y,z,sta)
#
# the script also outputs an additional *.csv file in hec-ras format
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import matplotlib.tri    as mtri           # matplotlib triangulations
import numpy             as np             # numpy
from ppmodules.readMesh import *           # to get all readMesh functions
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 7 :
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python interpBreakline.py -t tin.grd -l lines.csv -o lines_z.csv')
	sys.exit()

dummy1 =  sys.argv[1]
tin_file = sys.argv[2]
dummy2 =  sys.argv[3]
lines_file = sys.argv[4]
dummy3 =  sys.argv[5]
output_file = sys.argv[6] # interp_mesh

# read the adcirc tin file
t_n,t_e,t_x,t_y,t_z,t_ikle = readAdcirc(tin_file)

# read the lines file
lines_data = np.loadtxt(lines_file, delimiter=',',skiprows=0,unpack=True)
shapeid = lines_data[0,:]
#shapeid = shapeid.astype(np.int32)
x = lines_data[1,:]
y = lines_data[2,:]

# create the new output variables
z = np.zeros(len(x))
sta = np.zeros(len(x))
tempid = np.zeros(len(x))
dist = np.zeros(len(x))
		
# create tin triangulation object using matplotlib
tin = mtri.Triangulation(t_x, t_y, t_ikle)

# perform the triangulation
interpolator = mtri.LinearTriInterpolator(tin, t_z)
z = interpolator(x, y)

# if the node is outside of the boundary of the domain, assign value -999.0
# as the interpolated node
where_are_NaNs = np.isnan(z)
z[where_are_NaNs] = -999.0

if (np.sum(where_are_NaNs) > 0):
	print('#####################################################')
	print('')
	print('WARNING: Some nodes are outside of the TIN boundary!!!')
	print('')
	print('A value of -999.0 is assigned to those nodes!')
	print('')
	print('#####################################################')

# to create the output file
fout = open(output_file,"w")

# to create the sta array
sta[0] = 0.0
tempid = shapeid
dist[0] = 0.0

for i in range(1,len(x)):
	if (tempid[i] - shapeid[i-1] < 0.001):
		xdist = x[i] - x[i-1]
		ydist = y[i] - y[i-1]
		dist[i] = np.sqrt(np.power(xdist,2.0) + np.power(ydist,2.0))
		sta[i] = sta[i-1] + dist[i]

# to round the numpy arrays to three decimal spaces
x = np.around(x,decimals=3)
y = np.around(y,decimals=3)
z = np.around(z,decimals=3)
dist = np.around(dist,decimals=3)
sta = np.around(sta,decimals=3)

# now to write the output lines file (with xs information)
for i in range(len(x)):
	fout.write(str(shapeid[i]) + ',' + str(x[i]) + ',' + 
		str(y[i]) + ',' + str(z[i]) + ',' +	str(sta[i]) + '\n')

# create an alternate output csv file that is used by hec-ras
output_file2 = output_file.rsplit('.',1)[0] + '_hec-ras.csv'

# opens the alternate output file
f2 = open(output_file2,'w')

# writes the header lines
f2.write('River,Reach,RS,X,Y,Z' + '\n')
for i in range(len(x)):
	f2.write('river_name,reach_name,' + str(shapeid[i]) + ','+
		str(x[i]) + ',' + str(y[i]) + ',' + str(z[i]) + '\n')

print('All done!')
