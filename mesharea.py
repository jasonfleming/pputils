#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 mesharea.py                           # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Sep 6, 2015
# 
# Modified: Feb 21, 2016
# Made it work under python 2 or 3
#
# Purpose: Script takes the adcirc grid file, and outputs the areas of 
# elements within a specified threshold (i.e. < 0.01 m2). This is useful
# for finding potentially troubling spots in the input topology (i.e., bad
# breaklines) that cause creation of zero area triangles.
#
# Uses: Python 2 or 3, Matplotlib, Numpy
#
# Example:
#
# python mesharea.py -i out.grd -a 0.01 -o outarea.txt
# where:
# -i input adcirc grid file
# -a threshold area (in m2)
# -o output file with coordinates of elements meeting the area threshold
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import numpy as np
from ppmodules.readMesh import *
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Functions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def elemprop(x1,y1,x2,y2,x3,y3):
	# element properties - computes area and centroids of each element
	
	# signs in eqs work when the elements are CCW (for example Triangle mesh
	# generator produces these) 
	# outputs element area, and its centroid coordinate
	twoA = (x2*y3 - x3*y2) - (x1*y3-x3*y1) + (x1*y2 - x2*y1)
	area = twoA / 2.0
	
	xc = (x1 + x2 + x3) / 3.0
	yc = (y1 + y2 + y3) / 3.0
	return area, xc, yc

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# I/O
if len(sys.argv) != 7 :
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python mesharea.py -i out.grd -a 0.01 -o outarea.txt')
	sys.exit()
dummy1 =  sys.argv[1]
adcirc_file = sys.argv[2]
dummy2 =  sys.argv[3]
area_threshold = sys.argv[4]
area_threshold = float(area_threshold)
dummy3 = sys.argv[5]
output_file = sys.argv[6]

# to create the output file
fout = open(output_file,"w")

# read the adcirc file
n,e,x,y,z,ikle = readAdcirc(adcirc_file)

# define properties arrays
area = np.zeros(e)
xc = np.zeros(e)
yc = np.zeros(e)

for i in range(e):
	area[i],xc[i],yc[i] = elemprop(x[ikle[i,0]], y[ikle[i,0]],
		x[ikle[i,1]], y[ikle[i,1]],	x[ikle[i,2]], y[ikle[i,2]])
	if (area[i] < area_threshold):
		fout.write(str(xc[i]) + ',' + str(yc[i]) + ',' + str(area[i]) + '\n')
	
