#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 adcirc2asc.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: June 29, 2015
#
# Purpose: Script takes in a tin in ADCIRC format, and generates an ESRI *.asc 
# file for easy visualization by a GIS.
#
# Uses: Python 2 or 3, Matplotlib, Numpy
#
# Example:
#
# python adcirc2asc.py -i tin.14 -s 10 -o tin.asc
# where:
# -i input adcirc mesh file
# -s spacing (in m) of the *.asc grid file
# -o generated *.asc grid file
# 
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
  print('python adcirc2asc.py -i tin.14 -s 10 -o tin.asc')
  sys.exit()
dummy1 =  sys.argv[1]
adcirc_file = sys.argv[2]
dummy2 =  sys.argv[3]
spacing = sys.argv[4]
spacing = float(spacing)
dummy3 =  sys.argv[5]
output_file = sys.argv[6] # output *.asc grid

# to create the output file
fout = open(output_file,"w")

# read the adcirc file
n,e,x,y,z,ikle = readAdcirc(adcirc_file)

# create tin triangulation object using matplotlib
tin = mtri.Triangulation(x, y, ikle)

# determine the spacing of the regular grid
range_in_x = x.max() - x.min()
range_in_y = y.max() - y.min()

max_range = max(range_in_x, range_in_y)

# first index is integer divider, second is remainder
num_x_pts = divmod(range_in_x, spacing)
num_y_pts = divmod(range_in_y, spacing)

print("Size of output matrix is : " + str(int(num_x_pts[0])) + " x " + str(int(num_y_pts[0])))
print("Grid resolution is : " + str(spacing) + " m")

# creates the regular grid
xreg, yreg = np.meshgrid(np.linspace(x.min(), x.max(), int(num_x_pts[0])),
  np.linspace(y.min(), y.max(), int(num_y_pts[0])))
x_regs = xreg[1,:]
y_regs = yreg[:,1]

# perform the triangulation
interpolator = mtri.LinearTriInterpolator(tin, z)
interp_zz = interpolator(xreg, yreg)

# print "Shape of array z: " + str(interp_zz.shape[0])

# print "Shape of arrays xreg and yreg: " + str(x_regs.shape) + " " + str(y_regs.shape) 

where_are_NaNs = np.isnan(interp_zz)
interp_zz[where_are_NaNs] = -999.0

# write the header string
header_str = "NCOLS " + str(interp_zz.shape[1]) + "\n"
header_str = header_str + "NROWS " + str(interp_zz.shape[0]) + "\n"
header_str = header_str + "XLLCORNER " + str(x_regs[0]) + "\n"
header_str = header_str + "YLLCORNER " + str(y_regs[0]) + "\n"
header_str = header_str + "CELLSIZE " + str(spacing) + "\n"
header_str = header_str + "NODATA_VALUE " + str(-999.00)

#np.savetxt("temp.out", z, fmt='%.2f', delimiter='') # this has no max spaces
np.savetxt(output_file, np.flipud(interp_zz), fmt='%10.3f', header = header_str, 
  comments = '', delimiter='') # this has 10 char spaces, 2 after decimal

print("All done!")
