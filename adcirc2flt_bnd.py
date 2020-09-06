#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 adcirc2flt_bnd.py                     # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Dec 1, 2016
#
# Purpose: Script takes in a tin in ADCIRC format, and generates an ESRI *.flt 
# file for easy visualization by a GIS. This is the same as my adcirc2flt.py
# script, except that this one generates the grid for the region within the 
# boundary polygon, instead for the entire triangulation. The boundary polygon
# should be inside the boundary of the triangulation. If this is not the case
# garbage results will be generated for the area outside the triangulation
# boundary but inside the boundary polygon.
#
# Uses: Python 2 or 3, Matplotlib, Numpy
#
# Example:
#
# python adcirc2flt_bnd.py -i tin.grd -b boundary.csv -s 10 -o tin.asc
# where:
# -i input adcirc mesh file
# -b boundary where the grid is to be generated
# -s spacing (in m) of the *.asc grid file
# -o generated *.asc grid file
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import matplotlib.tri    as mtri           # matplotlib triangulations
import matplotlib.path as mplPath          # matplotlib path object
import numpy             as np             # numpy
from ppmodules.readMesh import *           # to get all readMesh functions
import struct                              # to write binary data to file
from progressbar import ProgressBar, Bar, Percentage, ETA
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 9:
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python adcirc2flt_bnd.py -i tin.grd -p poly.csv -s 10 -o tin.asc')
  sys.exit()
adcirc_file = sys.argv[2]
boundary_file = sys.argv[4]
spacing = sys.argv[6]
spacing = float(spacing)
output_file = sys.argv[8] # output *.asc grid

# to create the output file
fout = open(output_file,'wb')

# the name of the header file (this is asci format)
# use reverse split!
header_file = output_file.rsplit('.',1)[0] + '.hdr'
fhdr = open(header_file,'w')

# read the adcirc file
print('Reading TIN ...')
n,e,x,y,z,ikle = readAdcirc(adcirc_file)

# read polygon file
print('Reading boundary ...')
poly_data = np.loadtxt(boundary_file, delimiter=',',skiprows=0,unpack=True)

# polygon data
shapeid_poly = poly_data[0,:]
x_poly = poly_data[1,:]
y_poly = poly_data[2,:]

# crop all the polygon points to three decimals only
x_poly = np.around(x_poly,decimals=3)
y_poly = np.around(y_poly,decimals=3)

# get the unique polygon ids
polygon_ids = np.unique(shapeid_poly)

# find out how many different polygons there are
n_polygons = len(polygon_ids)

if (n_polygons > 1):
  print('Number of polygons in input file greater than 1. Exiting.')
  sys.exit()
  
# construct a polygon as mpl object
poly = list()
for i in range(len(shapeid_poly)):
  poly.append( (x_poly[i], y_poly[i]) )
  
# convert poly list to a numpy array
poly_array = np.asarray(poly)

# create a mathplotlib path object
path = mplPath.Path(poly_array)

# create tin triangulation object using matplotlib
print('Creating Matplotlib triangulation ...')
tin = mtri.Triangulation(x, y, ikle)

# determine the spacing of the regular grid
range_in_x = x_poly.max() - x_poly.min()
range_in_y = y_poly.max() - y_poly.min()

max_range = max(range_in_x, range_in_y)

# first index is integer divider, second is remainder
num_x_pts = divmod(range_in_x, spacing)
num_y_pts = divmod(range_in_y, spacing)

print("Size of output matrix is : " + str(int(num_x_pts[0])) + " x " + str(int(num_y_pts[0])))
print("Grid resolution is : " + str(spacing) + " m")

# creates the regular grid
print('Creating the grid ...')
xreg, yreg = np.meshgrid(np.linspace(x_poly.min(), x_poly.max(), int(num_x_pts[0])),
  np.linspace(y_poly.min(), y_poly.max(), int(num_y_pts[0])))
x_regs = xreg[1,:]
y_regs = yreg[:,1]

# perform the triangulation
print('Performing interpolations ...')
interpolator = mtri.LinearTriInterpolator(tin, z)
interp_zz = interpolator(xreg, yreg)

where_are_NaNs = np.isnan(interp_zz)
interp_zz[where_are_NaNs] = -999.0

# ravel interp_zz (i.e., create a 1d array out of the interpolated z)
interp_zz_ravel = np.ravel(interp_zz)

# to assign -999.0 to all mesh nodes outside of the poly boundary
# to make the gridded 2d points arrays into 1d arrays (i.e., unravel the
# 2d points into 1d grids
x_grid_pts = np.ravel(xreg)
y_grid_pts = np.ravel(yreg)

# loop through each point of the raveled arrays, and assign a NaN to
# one that lies outside of the boundary; this is the longest execution task
# of this script!
print('Clipping results to boundary ...')

w = [Percentage(), Bar(), ETA()]
pbar = ProgressBar(widgets=w, maxval=len(x_grid_pts)).start()

for i in range(len(x_grid_pts)):
  poly_test = path.contains_point( (x_grid_pts[i], y_grid_pts[i]) )
  if (poly_test == False):
    interp_zz_ravel[i] = -999.00
  pbar.update(i+1)  
pbar.finish()

# now, turn interp_zz_ravel back into a 2d array
interp_zz = np.reshape(interp_zz_ravel, xreg.shape)

# open the output *.hdr file, and write the header info
fhdr.write("NCOLS " + str(interp_zz.shape[1]) + "\n")
fhdr.write("NROWS " + str(interp_zz.shape[0]) + "\n")
fhdr.write("XLLCORNER " + str(x_regs[0]) + "\n")
fhdr.write("YLLCORNER " + str(y_regs[0]) + "\n")
fhdr.write("CELLSIZE " + str(spacing) + "\n")
fhdr.write("NODATA_VALUE " + str(-999.00) + "\n")
fhdr.write("BYTEORDER LSBFIRST " + "\n")

print('Writing binary data file ...')
for i in range(interp_zz.shape[0]):
  s = struct.pack('f'*interp_zz.shape[1], *np.flipud(interp_zz)[i,:])
  fout.write(s)
fout.close()

print("All done!")
