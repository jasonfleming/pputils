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
#
# Modified: Feb 21, 2016
# Made it work under python 2 and 3 using selafin_io_pp class ppSELAFIN
#
# Purpose: Script takes in a telemac results file, and transposes results
# of a particular time step to another mesh. This is useful for generating
# hot start files. If the meshes are the same, no need to run this script,
# but simply run chop.py (which already exists in Telemac python scripts).
#
# Revised: May 17, 2016
# Updated so that if the node of the mesh lies outside of the boundary of the 
# results file, the closest results file node is assigned to the mesh node. It 
# uses kdtree from scipy to do this. 
#
# Revised: May 24, 2016
# Rather than working for a single time step, now the script transposes all
# variables for all time steps. This is needed for my wave library processing.
#
# TODO: the script has problems when interpolating a variable like direction
# that takes on values from 0 to 360. In this case, we have to convert from
# direction to vectors, interpolate, then re-create the direction variable
# on the interpolated mesh.
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

numvars = len(vnames)

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

# to perform triangulation for each variable in the result file, 
# for each time step
for t in range(len(times)):
	print('Writing time step: ' + str(t))
	# this is the master transposed array, for time step t
	mesh_results = np.zeros((numvars, NPOIN_m))
	
	# reads the results for a particular variable, and stores it into results
	res.readVariables(t)
	results = res.getVarValues()
	
	# perform the interpolation and create mesh_results array
	for i in range(numvars):
		interpolator = mtri.LinearTriInterpolator(triang, results[i,:])
		mesh_results[i,:] = interpolator(x_m, y_m)
		
		for j in range(NPOIN_m):
			if (np.isnan(mesh_results[i,j])):
				# rather than assigning zero, assign a value from a closest non-nan node
				d, idx = tree.query((x_m[j],y_m[j]), k = 1)
				mesh_results[i,j] = results[i][idx]

	mres.writeVariables(times[t], mesh_results)

