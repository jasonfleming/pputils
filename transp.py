#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 transp.py                             # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Oct 21, 2015
# Purpose: Script takes in a telemac results file, and transposes results
# of a particular time step to another mesh. This is useful for generating
# hot start files. If the meshes are the same, no need to run this script,
# but simply run chop.py (which already exists in Telemac python scripts).
#
# Revised: Feb 21, 2016
# Made it work under python 2 and 3 using selafin_io_pp class ppSELAFIN
#
# Revised: May 17, 2016
# Updated so that if the node of the mesh lies outside of the boundary of the 
# results file, the closest results file node is assigned to the mesh node. It 
# uses kdtree from scipy to do this. 
#
# Revised: May 24, 2016
# Rather than working for a single time step, now the script transposes all
# variables for all time steps. This is needed for the wave library processing.
#
# Revised: May 30, 2016
# The script had problems when interpolating a variable like direction
# (that take on values from 0 to 360) in cases when values ranged from
# 359 to 1 degree. Interpolating direction variables were now eliminated.
# Instead, direction variable are converted to cartesian, both components
# interpolated, then direction variable is re-created and written to file.
# The limitation with the script as it stands is that it only assumes 
# one direction variable in *.slf file, and that the direction is 
# according to tomawac's nautical convention (CW from vertical, where 
# arrow starts at origin and points outward, with zero being a wave from
# the south). Note that TOMAWAC's nautical convention is different than
# SWAN's nautical convention.
# 
# Revised: Jun 21, 2016
# Added progress bar widget
#
# Uses: Python 2 or 3, Matplotlib, Numpy, Scipy
#
# Example:
#
# python transp.py -r result.slf -m mesh.slf -o mesh_transp.slf
# where:
# -r telemac result file
# -m the input *.slf mesh which will be used to tranpose the result to
# -o final output file with the transposed results
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import matplotlib.tri as mtri
import numpy as np
from scipy import spatial
from ppmodules.selafin_io_pp import *
from progressbar import ProgressBar, Bar, Percentage, ETA
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# converts cartesian vector to Tomawac nautical direction convention
def toTomNautical(u,v):
  
  # quadrants are defined as follows
  # IV  | I
  # ---------
  # III | II
  
  # error checking
  if (abs(v) < 1.0E-6):
    v = 1.0E-6
  if (abs(u) < 1.0E-6):
    u = 1.0E-6
    
  # compute the cartesian angle
  theta_cart = np.arctan(abs(v)/abs(u)) * 360.0 / (2.0 * np.pi)
  
  # quadrant I
  if (u >= 0.0 and v >= 0.0):
    theta_naut = 90 - theta_cart 
  # quadrant II
  elif (u > 0.0 and v < 0.0):
    theta_naut = 90 + theta_cart
  # quadrant III
  elif (u < 0.0 and v < 0.0):
    theta_naut = 270 - theta_cart
  # quadrant IV
  elif (u < 0.0 and v > 0.0):
    theta_naut = 270 + theta_cart
  else:
    theta_naut = 0.0
  
  dir = theta_naut
  
  return dir

curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 7 :
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python transp.py -r result.slf -m mesh.slf -o mesh_transp.slf')
  sys.exit()

result_file = sys.argv[2]
mesh_file = sys.argv[4]
output_file = sys.argv[6]

# reads the results *.slf file
res = ppSELAFIN(result_file)
res.readHeader()
res.readTimes()

# gets some of the mesh properties from the *.slf file
times = res.getTimes()
vnames = res.getVarNames()
vunits = res.getVarUnits()
float_type,float_size = res.getPrecision()

# number of variables
numvars = len(vnames)

# added on 2016.05.30
# looks for a direction variable (that takes on values 0 to 360) such as
# mean direction (from Tomawac)

# assume there will be only one direction variable in the *.slf file
# and that the direction variable is in Tomawac's naut convention
dir_idx = -999
for i in range(numvars):
  if ((vnames[i].find('DIRECTION') > -1)):
    dir_idx = i
    
# subscript r is for the result file
NELEM_r, NPOIN_r, NDP_r, IKLE_r, IPOBO_r, x_r, y_r = res.getMesh()

# the IKLE array starts at element 1, but matplotlib needs it to start
# at zero
IKLE_r[:,:] = IKLE_r[:,:] - 1

# now read the mesh *.slf file
mesh = ppSELAFIN(mesh_file)
mesh.readHeader()
mesh.readTimes()

# subscript m is for the mesh file
NELEM_m, NPOIN_m, NDP_m, IKLE_m, IPOBO_m, x_m, y_m = mesh.getMesh()

# now interpolate results to the mesh object, for each variable
triang = mtri.Triangulation(x_r,y_r,IKLE_r)

# create a KDTree object
source = np.column_stack((x_r,y_r))
tree = spatial.KDTree(source)

# now write the front matter of the results *.slf file
mres = ppSELAFIN(output_file)
mres.setPrecision(float_type,float_size)
mres.setTitle('created with pputils')
mres.setVarNames(vnames)
mres.setVarUnits(vunits)
mres.setIPARAM([1, 0, 0, 0, 0, 0, 0, 0, 0, 1])
mres.setMesh(NELEM_m, NPOIN_m, NDP_m, IKLE_m, IPOBO_m, x_m, y_m)
mres.writeHeader()

# for the progress bar
w = [Percentage(), Bar(), ETA()]
pbar = ProgressBar(widgets=w, maxval=len(times)).start()

# to perform triangulation for each variable in the result file, 
# for each time step
for t in range(len(times)):
  pbar.update(t+1)
  # print('Writing time step: ' + str(t))
  # this is the master transposed array, for time step t
  mesh_results = np.zeros((numvars, NPOIN_m))
  
  # reads the results for a particular variable, and stores it into results
  res.readVariables(t)
  results = res.getVarValues()
  
  # perform the interpolation and create mesh_results array
  for i in range(numvars):
    
    # correction for direction variable
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
    if (i == dir_idx):
      wavex = np.sin(results[i,:]*np.pi/180.0)
      wavey = np.cos(results[i,:]*np.pi/180.0)
      
      # interpolate the direction variable
      interpolator = mtri.LinearTriInterpolator(triang, wavex)
      wavex_int = interpolator(x_m, y_m)
      
      interpolator = mtri.LinearTriInterpolator(triang, wavey)
      wavey_int = interpolator(x_m, y_m)
      
      for j in range(NPOIN_m):
        if (np.isnan(wavex_int[j])):
          # rather than assigning zero, assign a value from a closest non-nan node
          d, idx = tree.query((x_m[j],y_m[j]), k = 1)
          wavex_int[j] = wavex[idx]
          
        if (np.isnan(wavey_int[j])):
          # rather than assigning zero, assign a value from a closest non-nan node
          d, idx = tree.query((x_m[j],y_m[j]), k = 1)
          wavey_int[j] = wavey[idx]
          
        # from wavex_int and wavey_int, re-create the direction variable
        # direction is in tomawac's nautical convention
        mesh_results[i,j] = toTomNautical(wavex_int[j],wavey_int[j])
    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
    else:
      # this is for the rest of the variables
      interpolator = mtri.LinearTriInterpolator(triang, results[i,:])
      mesh_results[i,:] = interpolator(x_m, y_m)
    
      for j in range(NPOIN_m):
        if (np.isnan(mesh_results[i,j])):
          # rather than assigning zero, assign a value from a closest non-nan node
          d, idx = tree.query((x_m[j],y_m[j]), k = 1)
          mesh_results[i,j] = results[i][idx]

  mres.writeVariables(times[t], mesh_results)
pbar.finish()
