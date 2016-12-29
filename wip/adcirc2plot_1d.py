#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 adcirc2plot_1d.py                     # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng. 
# 
# Date: Dec 28, 2016
#
# Purpose: Script designed to take a tin and cross sections from a lines 
# file (PPUTILS lines format), and create a plot of the sections. Each
# line in the file will be plotted on a separate plot.

# This scrpt is similar to interBreakline.py, except rather than 
# outputing cross sections as an interpolated lines file, it outputs a
# series of *.svg files, one file per cross section. I AM NOT HAPPY
# WITH THE AUTOMATIC WAY OF GENERATION OF TICS ...
#
# Using: Python 2 or 3, Matplotlib, Numpy
#
# Example: 
# python adcirc2plot_1d.py -i tin.grd -l profile.csv
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import numpy as np
import matplotlib.tri as mtri
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker

from ppmodules.readMesh import * # for readMesh function
import matplotlib as mpl
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
# 
# I/O
if (len(sys.argv) == 5):
	adcirc_file = sys.argv[2]
	line_file = sys.argv[4]
else:
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python adcirc2plot_1d.py -i tin.grd -l profile.csv')
	sys.exit()

# read the line (profile or cross section) file
line_data = np.loadtxt(line_file, delimiter=',',skiprows=0,unpack=True)
shapeid = line_data[0,:]
shapeid = shapeid.astype(np.int32)
lnx = line_data[1,:]
lny = line_data[2,:]

# create the new output variables
lnz = np.zeros(len(lnx))
sta = np.zeros(len(lnx))
tempid = np.zeros(len(lnx))
dist = np.zeros(len(lnx))

# to create the sta array
sta[0] = 0.0
tempid = shapeid
dist[0] = 0.0

for i in range(1,len(lnx)):
	if (tempid[i] - shapeid[i-1] < 0.001):
		xdist = lnx[i] - lnx[i-1]
		ydist = lny[i] - lny[i-1]
		dist[i] = np.sqrt(np.power(xdist,2.0) + np.power(ydist,2.0))
		sta[i] = sta[i-1] + dist[i]

# read the adcirc file
n,e,x,y,z,ikle = readAdcirc(adcirc_file)

# create tin triangulation object using matplotlib
tin = mtri.Triangulation(x, y, ikle)

# to interpolate the the nodes of the lines file from the tin
interpolator = mtri.LinearTriInterpolator(tin, z)
lnz = interpolator(lnx,lny)

# if the node is outside of the boundary of the domain, assign value -999.0
# as the interpolated node
where_are_NaNs = np.isnan(lnz)
lnz[where_are_NaNs] = -999.0

# rather than keeping the -999.0 as the mesh node value outside the tin,
# simply assign to that mesh node the elevation of the closest tin node.
for i in range(len(lnx)):
	if (where_are_NaNs[i] == True):
		xdist = np.subtract(x,lnx[i])
		ydist = np.subtract(y,lny[i])
		dist = np.sqrt(np.power(xdist,2.0) + np.power(ydist,2.0))
		minidx = np.argmin(dist)
		
		lnz[i] = z[minidx]

# find out the unique shapeid in the lines file 
unique_shapeid = np.unique(shapeid)

# create a list of filename
filenames = list()
for i in range(len(unique_shapeid)):
	filenames.append(line_file.rsplit('.',1)[0] + "{:0>3d}".format(i) + '.png')

# to print the *.png files for each unique shapeid in the lines file
shape_count = 0

for i in range(len(unique_shapeid)):
	cur_sta = sta[shapeid==shape_count]
	cur_z = lnz[shapeid==shape_count]
	
	xmin = np.amin(cur_sta)
	xmax = np.amax(cur_sta)
	ymin = np.amin(cur_z)
	ymax = np.amax(cur_z)
	
	plt.figure(figsize=(5,3)) # this is a 5 in x 3 in plot
	plt.grid(False)
	plt.xlim(xmin,xmax)
	plt.ylim(ymin,ymax)
	plt.xlabel('Station [m]')
	plt.ylabel('Elevation [m]')
	ax = plt.axes()
	
	# this gets rid of top and right axes and ticks
	ax.spines['top'].set_visible(False)
	ax.spines['right'].set_visible(False)
	ax.get_xaxis().tick_bottom()
	ax.get_yaxis().tick_left()
	
	'''
	ax.xaxis.set_major_locator(ticker.MultipleLocator(100))
	ax.xaxis.set_minor_locator(ticker.MultipleLocator(50))
	
	ax.yaxis.set_major_locator(ticker.MultipleLocator(0.1))
	ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.05))
	'''
	# plt.grid(True, which='both')
	
	plt.plot(cur_sta, cur_z)
	mpl.rcParams['svg.fonttype'] = 'none'
	mpl.rcParams.update({'font.size': 11})
	plt.savefig(filenames[i], c = 'k')
	plt.close()
	
	shape_count = shape_count + 1


