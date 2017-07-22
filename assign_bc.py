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
 
# now we read the BC poly file using numpy
poly_data = np.loadtxt(poly_file, delimiter=',',skiprows=0,unpack=True)

# boundary data
shapeid_poly = poly_data[0,:]
x_poly = poly_data[1,:]
y_poly = poly_data[2,:]
attr_poly = poly_data[3,:]

# convert attr_poly to int
attr_poly_int = attr_poly.astype(int)

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
attr_count = -1

# go through the polygons, and assign attribute_data 
for i in range(nodes-1):
  if (shapeid_poly[i] - shapeid_poly[i+1] < 0):
    attr_count = attr_count + 1
    attribute_data[attr_count] = attr_poly[i]
    
# manually assign the attribute_data for the last polygon
attribute_data[n_polygons-1] = attr_poly_int[nodes-1]

# define the default *.cli file attribute for columns 1,2,3,8
f = np.zeros(n_cli, dtype=np.int)

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
  
  # delete all elements in the poly list
  del poly[:]    
  
# now we are ready to write the new *.cli file
for i in range(n_cli):
  if f[i] > 0:
    a = str(f[i])
    fout.write(a[0] + ' ' +a[1] + ' ' + a[2] + ' 0.000 0.000 0.000 0.000 ' +
       a[3] + ' 0.000 0.000 0.000 ' +
       str(global_nodes_int[i]) + ' ' + str(i+1) + '\n')
  else:
    fout.write('2 2 2 0.000 0.000 0.000 0.000 2 0.000 0.000 0.000 ' +
      str(global_nodes_int[i]) + ' ' + str(i+1) + '\n')  
