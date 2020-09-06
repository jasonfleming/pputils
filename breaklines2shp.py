#!/usr/bin/env python3
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
# Modified: Nov 13, 2016
# Added an option for letting the user chose to write a 2d or a 3d shp
# format. The 2d shp format is useful when cleaning the breaklines has
# to be done with GRASS v.clean tool to ensure proper geometry is 
# produced that will make a valid tin for matplotlib.tri object.
#
# Modififed: Nov 26, 2016
# Added an option for checking if there the lines data has z values.
#
# Modififed: Nov 24, 2019
# Incorporated changes suggested by user nstrahl, that make the script
# work in the latest version of pyshp package.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python breaklines2shp.py -l lines3d.csv -t 3d -o lines3d.shp
# 
# where
# -l is the lines file in pputils format
# -t is the type of the shapefile that will be created (2d or 3d)
# -o output shapefile
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
if len(sys.argv) == 7 :
  lines_file = sys.argv[2]
  shptype = sys.argv[4]
  output_file = sys.argv[6]
else:
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python breaklines2shp.py -l lines3d.csv -t 2d -o lines3d.shp')
  sys.exit()

# use numpy to read the file
# each column in the file is a row in data read by np.loadtxt method
lines_data = np.loadtxt(lines_file, delimiter=',',skiprows=0,unpack=True)

# find out how many columns there are in the lines_file
with open(lines_file, 'r') as f:
    line = next(f) # read 1 line
    ncols = len(line.split(','))

# assign the data read to variables
shapeid_lns = lines_data[0,:]
x_lns = lines_data[1,:]
y_lns = lines_data[2,:]

# if z is in the file, retain the z, otherwise write zeros
if (ncols > 3):
  z_lns = lines_data[3,:]
else:
  z_lns = np.zeros(len(x_lns))
  
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

# to create the output file
if (shptype == '2d'):
  out = Writer(target=output_file, shapeType=3) # this is POLYLINE type, or 2d shapefile
elif (shptype == '3d'):
  out = Writer(target=output_file, shapeType=13) # this is POLYLINEZ, or 3d shapefile
else:
  print('Invalid type specified in the -t argument. Exiting!')

# create the field 'id'
out.field('id', 'C', 10, 0)

# now we can write the breaklines

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
        if (shptype == '2d'):
          out.line(lines=[part])
        else:
          out.linez(lines=[part])
          
        out.record(id=i+1)
      
    else:
      part.append([x_lns[i-1], y_lns[i-1], z_lns[i-1], 0.0])
      if (shptype == '2d'):
        out.line(lines=[part])
      else:
        out.linez(lines=[part])
          
      out.record(id=i+1)
      
      part=[]

out.close()
pbar.finish()  
