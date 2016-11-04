#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 breaklines2shp.py                     # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Nov 3, 2016
#
# Purpose: Takes a pputils 3d breakline and exports it to shp format
# using the pyshp code.
# 
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python breaklines2shp.py -l lines3d.csv -o lines3d.shp
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy             as np             # numpy
from pyshp.shapefile import *              # pyshp class
from progressbar import ProgressBar, Bar, Percentage, ETA
#
# I/O
if len(sys.argv) == 5 :
	dummy2 =  sys.argv[1]
	lines_file = sys.argv[2]
	dummy3 =  sys.argv[3]
	output_file = sys.argv[4]
else:
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python breaklines2shp.py -l lines3d.csv -o lines3d.shp')
	sys.exit()

# use numpy to read the file
# each column in the file is a row in data read by np.loadtxt method
lines_data = np.loadtxt(lines_file, delimiter=',',skiprows=0,unpack=True)

shapeid_lns = lines_data[0,:]
x_lns = lines_data[1,:]
y_lns = lines_data[2,:]
z_lns = lines_data[3,:]
	
# round lines nodes to three decimals
x_lns = np.around(x_lns,decimals=3)
y_lns = np.around(y_lns,decimals=3)
z_lns = np.around(z_lns,decimals=3)

# finds out how many unique breaklines there are
n_unique_lns = np.unique(shapeid_lns)

# number of nodes in the lines file
n_lns = len(x_lns)

w = [Percentage(), Bar(), ETA()]
pbar = ProgressBar(widgets=w, maxval=n_lns).start()

# write the breaklines
# to create the output file
out = Writer(shapeType=13) # this is POLYLINEZ
out.field('id', 'C', 10, 0)

part=[]

for i in range(0,n_lns):
	pbar.update(i+1)

	if (i>0):
		cur_lns_shapeid = shapeid_lns[i]
		prev_lns_shapeid = shapeid_lns[i-1]

		if (cur_lns_shapeid - prev_lns_shapeid < 0.001):
			# create tupples for vertexes to add
			
			part.append([x_lns[i-1], y_lns[i-1], z_lns[i-1], 0.0])
			
			
			# this is needed, as the else below is never executed
			# for the last line in the lines file!
			if (i == n_lns-1):
				part.append([x_lns[i], y_lns[i], z_lns[i], 0.0])
				out.line(parts=[part])
				out.record(id=i+1)
			
		else:
			part.append([x_lns[i-1], y_lns[i-1], z_lns[i-1], 0.0])
			out.line(parts=[part])
			out.record(id=i+1)
			
			part=[]


############################################################################

# save the shapefile
out.save(output_file)

pbar.finish()	
