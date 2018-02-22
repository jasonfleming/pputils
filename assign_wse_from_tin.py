#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 assign_wse_from_tin.py                # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Feb 22, 2018
#
# Purpose: Script takes in a mesh in *.slf format and a PPUTILS tin
# file (containing a surface of water surface elevations) to produce 
# a *.slf file to be used as a warm start in a Telemac-2D simlation.
# This is particularly useful when generating a warm start file for
# dam break studies where the downstream river has a slopting water
# surface.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python assign_wse_from_tin.py -m mesh.slf -t tin.grd -o mesh_warm.slf
# where:
#
# -m input mesh file in *.slf format
# -p input tin file in adcirc format (the tin represents water surface)
# -o output file in *.slf format that can be used as a warm start 
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy             as np             # numpy
from ppmodules.selafin_io_pp import *      # to get SELAFIN I/O 
from ppmodules.readMesh import *           # to get the readMesh methods
import matplotlib.tri as mtri              # matplotlib triangulations
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
#
# I/O
if len(sys.argv) != 7:
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python assign_wse_from_tin.py -m mesh.slf -t tin.grd -o mesh_warm.slf')
  sys.exit()

mesh_file = sys.argv[2]
tin_file = sys.argv[4]
output_file  = sys.argv[6]

# now read the input *.slf geometry file
slf = ppSELAFIN(mesh_file)
slf.readHeader()
slf.readTimes()

times = slf.getTimes()
variables = slf.getVarNames()
units = slf.getVarUnits()
float_type,float_size = slf.getPrecision()
NELEM, NPOIN, NDP, IKLE, IPOBO, x, y = slf.getMesh()

# reads all vars at the last time step in the file
slf.readVariables(times[-1])
results = slf.getVarValues()

# gets the number of planes
NPLAN = slf.getNPLAN()

if (NPLAN > 1):
  print('3d SELAFIN files are not yet supported. Exiting!')
  sys.exit()

# make sure that the variable bottom is in the mesh_file
idx_bottom = -999
idx_bottom_friction = -999

# find the index of the vector variables
for i in range(len(variables)):
  if (variables[i].find('BOTTOM          ') > -1):
    idx_bottom = i
  elif (variables[i].find('FOND            ') > -1):
    idx_bottom = i
  
  # find bottom friction
  elif (variables[i].find('BOTTOM FRICTION ') > -1):
    idx_bottom_friction = i

if (idx_bottom < 0):
  print('Variable BOTTOM or FOND not found in input file. Exiting!')
  sys.exit()

# this is the bottom array, as a 1d vector
bottom = results[idx_bottom,:]

# now we can read in the tin_file (twse is the wse read from the tin)
tn,te,tx,ty,twse,tikle = readAdcirc(tin_file)

# now construct the Matplotlib's Triangulation object
tin = mtri.Triangulation(tx, ty, tikle)

# to perform the triangulation
interpolator = mtri.LinearTriInterpolator(tin, twse)
wse = interpolator(x, y)

# if the mesh node is outside of the tin boundary, Matplotlib will assign
# a NaN value to that node
where_are_NaNs = np.isnan(wse)
wse[where_are_NaNs] = -999.0

# rather than keeping the -999.0 as the mesh node value outside the tin,
# simply assign to that mesh node the bottom elevation.
for i in range(NPOIN):
  if (where_are_NaNs[i] == True):
    wse[i] = bottom[i]

# now we are ready to write the new *.slf warm start (ws) file
slf_ws = ppSELAFIN(output_file)
slf_ws.setPrecision(float_type,float_size)
slf_ws.setTitle('warm start file created with pputils')

# if there is no bottom friction, write these variables
if (idx_bottom_friction  < 0):
  slf_ws.setVarNames(['BOTTOM','WATER DEPTH','FREE SURFACE','VELOCITY U', 'VELOCITY V'])
  slf_ws.setVarUnits(['M','M','M','M/S','M/S'])
  
# if bottom friction is present, write these variables
else:
  slf_ws.setVarNames(['BOTTOM','BOTTOM FRICTION','WATER DEPTH','FREE SURFACE','VELOCITY U', 'VELOCITY V'])
  slf_ws.setVarUnits(['M',' ','M','M','M/S','M/S'])

slf_ws.setIPARAM([1, 0, 0, 0, 0, 0, 0, 0, 0, 1])
slf_ws.setMesh(NELEM, NPOIN, NDP, IKLE, IPOBO, x, y)
slf_ws.writeHeader()

# re-create the depth array from the wse and bottom arrays
depth = np.subtract(wse, bottom)

# make sure there are not negative depths,
# and that wse is not smaller than bottom
for i in range(NPOIN):
  if (depth[i] < 0):
    depth[i] = 0.0
  if (wse[i] < bottom[i]):
    wse[i] = bottom[i]

# this is the master results to write for the warm start file
if (idx_bottom_friction  < 0):
  res_ws = np.zeros((5,NPOIN))
  res_ws[0,:] = bottom
  res_ws[1,:] = depth
  res_ws[2,:] = wse
  res_ws[3,:] = np.zeros(NPOIN)
  res_ws[4,:] = np.zeros(NPOIN)
else:
  res_ws = np.zeros((6,NPOIN))
  res_ws[0,:] = bottom
  res_ws[1,:] = results[idx_bottom_friction]
  res_ws[2,:] = depth
  res_ws[3,:] = wse
  res_ws[4,:] = np.zeros(NPOIN)
  res_ws[5,:] = np.zeros(NPOIN)

# it does not write the time of the original file, but rather
# writes zero instead as the time of the warm start file
slf_ws.writeVariables(0, res_ws)
