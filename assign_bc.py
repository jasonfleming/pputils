#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 assign_bc.py                          # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Jul 21, 2017
#
# Purpose: Script takes in a mesh in *.slf format, a *.cli file, and
# a set of closed boundaries with TELEMAC BC markers to produce a
# modified *.cli file with the boundary condition information ready
# for a simulation. The bc *.csv file must define for each closed
# polygon a four digit attribute corresponding to columns 1,2,3,8 of
# the *.cli file --> 4555 is flow; 5444 is level; 5662 is offshore.
# Of course, any valid four digits recognized by TELEMAC can be used.
#
# Revised: Apr 4, 2018
# Added an ability to read a description field from the *.csv poly
# file so that text based description can be written for each boundary.
# This makes it easier for the user to know what each boundary is.
#
# The script is also backward compatible with the previous version,
# which did not have the description field present.
#
# The PPUTILS poly file should have the following columns:
# shapeid,x,y,bc_code,description [if the user wants the description]
# or
# shapeid,x,y,bc_code [if the user doesn't need the description]
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python assign_bc.py -g geo.slf -c geo.cli -b bc.csv -o geo_mod.cli
# where:
#
# -g input mesh file in *.slf format
# -c input BC file in *.cli format
# -b input boundary file (where each polygon has an attribute value to 
#    be assigned to the mesh)
# -o output BC file in *.cli format 
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy             as np             # numpy
from ppmodules.selafin_io_pp import *      # to get SELAFIN I/O 
from ppmodules.utilities import *          # to get the utilities
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
  print('python assign_bc.py -g geo.slf -c geo.cli -b bc.csv -o geo_mod.cli')
  sys.exit()

geo_file = sys.argv[2]
bc_file = sys.argv[4]
poly_file = sys.argv[6]
bc_file_mod = sys.argv[8]

# to create the output file
fout = open(bc_file_mod,'w')

# now read the input *.slf geometry file
slf = ppSELAFIN(geo_file)
slf.readHeader()
slf.readTimes()
slf.readVariables(0) # reads all vars at zero time step index

times = slf.getTimes()
vnames = slf.getVarNames()
vunits = slf.getVarUnits()
master_results = slf.getVarValues()
x = slf.getMeshX()
y = slf.getMeshY()
ikle = slf.getIKLE()
n = len(x)

# now read existing *.cli file using numpy
cli_data = np.loadtxt(bc_file, delimiter=' ',skiprows=0,unpack=True)

# these are the global nodes read from the bc_file
global_nodes = cli_data[11,:]
global_nodes_int = global_nodes.astype(dtype=np.int32)

# the number of lines in the *.cli file
n_cli = len(global_nodes)

# now we must assign coordinates for each node in the *.cli file
cli_x = np.zeros(n_cli)
cli_y = np.zeros(n_cli)

for i in range(n_cli):
  cli_x[i] = x[global_nodes_int[i]-1]
  cli_y[i] = y[global_nodes_int[i]-1]

# use pure python to read in the PPUTILS formatted poly file
# this poly file can have one field (4 integer BC code) and a
# 80 character description field

# store the PPUTILS formatted poly fine as a list (there will
# never be thousands of lines in this file, so it is OK to
# use the list structure here)
poly_data = list()

fpoly = open(poly_file, 'r')
poly_data = fpoly.readlines()
fpoly.close()

# take the first line, and determine if there are description fields in the data
# count is the number of columns in the input boundary polygon file
numcols = len(poly_data[0].split(','))
desc_present = False

if (numcols == 5):
  desc_present = True
elif(numcols == 4):
  desc_present = False
else:
  print('Input boundary polygon file is bad. Reformat and try again!')
  sys.exit(0)

# number of lines in the poly data
n_poly = len(poly_data)

# the poly data will be stored in these arrays/list
shapeid_poly = np.zeros(n_poly, dtype=np.float64)
x_poly = np.zeros(n_poly, dtype=np.float64)
y_poly = np.zeros(n_poly, dtype=np.float64)
attr_poly = np.zeros(n_poly, dtype=np.int32)
desc_poly = list()

# now assign the values to arrays/list
for i in range(n_poly):
  lst = poly_data[i].split(',')
  shapeid_poly[i] = lst[0]
  x_poly[i] = lst[1]
  y_poly[i] = lst[2]
  attr_poly[i] = lst[3]

  if (desc_present):
    desc_poly.append(lst[4])
  else:
    desc_poly.append('')

# below is the same as the older version of this script

# to accomodate code pasting
attr_poly_int = attr_poly

# round boundary nodes to three decimals
x_poly = np.around(x_poly,decimals=3)
y_poly = np.around(y_poly,decimals=3)

# total number of nodes in the polygon file
nodes = len(x_poly)

# get the unique polygon ids
polygon_ids = np.unique(shapeid_poly)

# find out how many different polygons there are
n_polygons = len(polygon_ids)

# to get the attribute data for each polygon
attribute_data = np.zeros(n_polygons, dtype=np.int)
desc_data = list()
attr_count = -1

# go through the polygons, and assign attribute_data 
for i in range(nodes-1):
  if (shapeid_poly[i] - shapeid_poly[i+1] < 0):
    attr_count = attr_count + 1
    attribute_data[attr_count] = attr_poly[i]

    if (desc_present):
      desc_data.append(desc_poly[i])
    else:
      desc_data.append('')

# manually assign the attribute_data for the last polygon
attribute_data[n_polygons-1] = attr_poly_int[nodes-1]

if (desc_present):
  desc_data.append(desc_poly[nodes-1])
else:
  desc_data.append('')

# define the default *.cli file attribute for columns 1,2,3,8
f = np.zeros(n_cli, dtype=np.int)

# creates an numpy array of string, with n_cli elements, with each
# element being 80 characters
fdesc = np.chararray(n_cli, itemsize=80)

# loop over all polygons
for i in range(n_polygons):
  # construct each polygon
  poly = []
  for j in range(nodes):
    if (shapeid_poly[j] == polygon_ids[i]):
      poly.append( (x_poly[j], y_poly[j]) )
  #print poly
  
  # to loop over all nodes in the *.cli file
  for k in range(n_cli):
    poly_test = point_in_poly(cli_x[k], cli_y[k], poly)
    if (poly_test == 'IN'):
      f[k] = attribute_data[i]
      fdesc[k] = desc_data[i]
  
  # delete all elements in the poly list
  del poly[:]    

# now we are ready to write the new *.cli file
for i in range(n_cli):
  if f[i] > 0:
    a = str(f[i])

    # this is not perfect, but it works
    if desc_present:
      fout.write(a[0] + ' ' +a[1] + ' ' + a[2] + ' 0.000 0.000 0.000 0.000 ' +
        a[3] + ' 0.000 0.000 0.000 ' +
        str(global_nodes_int[i]) + ' ' + str(i+1) + ' # ' + fdesc[i].decode() + '\n')
    else:
      fout.write(a[0] + ' ' +a[1] + ' ' + a[2] + ' 0.000 0.000 0.000 0.000 ' +
        a[3] + ' 0.000 0.000 0.000 ' +
        str(global_nodes_int[i]) + ' ' + str(i+1) + ' # ' + fdesc[i] + '\n')
  else:
    fout.write('2 2 2 0.000 0.000 0.000 0.000 2 0.000 0.000 0.000 ' +
      str(global_nodes_int[i]) + ' ' + str(i+1) + '\n')
