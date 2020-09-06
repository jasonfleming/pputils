#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 SWANxyz2slf.py                        # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: February 26, 2016
#
# Purpose: Script takes in a *.xyz file, and an existing *.slf file, and 
# interpolates the *.xyz data to the mesh provided in the *.slf file. Right
# now it assumes that the xyz file is for one timestep only and has the 
# variables x,y,depth,hsig,tp,dir (no header); dir is in NAUT convention. 
# To manage a full wave library, to make a script SWANxyzLib2slf.py.
#
# Uses: Python 2 or 3, Matplotlib, Numpy
#
# Example:
#
# python SWANxyz2slf.py -i swan_results.xyz -m mesh.slf -o swan_results.slf
# where:
# -i *.xyz file, no header
# -m mesh file in *.slf format
# -o output mesh_file, with interpolated data from xyz file
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import matplotlib.tri as mtri 
import numpy as np
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
	print('python SWANxyz2slf.py -i out.xyz -m mesh.slf -o mesh_interp.slf')
	sys.exit()

dummy1 =  sys.argv[1]
xyz_file = sys.argv[2]
dummy2 =  sys.argv[3]
mesh_file = sys.argv[4]
dummy3 =  sys.argv[5]
output_file = sys.argv[6] # interp_mesh

# read the mesh.slf file
# constructor for pp_SELAFIN class
slf = ppSELAFIN(mesh_file)
slf.readHeader()
slf.readTimes()

# get the properties from the *.slf mesh file
NELEM, NPOIN, NDP, IKLE, IPOBO, x, y = slf.getMesh()

# get the precision of the slf input file
ftype,fsize = slf.getPrecision()

##########################################################################
# Read the xyz file using pure python and stores into a numpy array.
# I am not loving doing string searches for the missing values.
# But np.genfromtxt also uses strings for missing values.

# store file contents into a master list
master = list()

with open(xyz_file, 'r') as f:
	for line in f:
		# searches each line in the file. when it finds a line that does not
		# having missing values, it appends it to the master list
		# this way, we have only valid values in the master list
		if ((not line.find('-0.990000000E+02') > -1) and \
			(not line.find('-0.900000000E+01') > -1) and \
			(not line.find('-0.999000000E+03') > -1 )):
			master.append(line)
f.close()

# determine how many data points in xyz file
numpts = len(master)

# determine how many variables there are in the xyz data
# now, it assumes x,y,depth,hsig,tp,dir
numvars = len(master[0].split())

# store it all as a master numpy array
swan_data = np.zeros((numvars,numpts))

for i in range(numpts):
	temp = master[i].split()
	swan_data[:,i] = np.asarray(temp)
	
# to add a row to an existing array
#np.concatenate((A,newrow), axis=0)

# to delete the first row from an existing array
#np.delete(x,(0), axis=0)

##########################################################################

# gets the x and y data from the xyz file
xx = swan_data[0,:]
yy = swan_data[1,:]

# initialize the interpolated data numpy array
slf_data = np.zeros((numvars,NPOIN))

# create an mtri triangulation object using swan_data positions
triang = mtri.Triangulation(xx,yy)

# interpolate to the slf_data positions
for i in range(2,numvars):
	interpolator = mtri.LinearTriInterpolator(triang,swan_data[i,:])
	slf_data[i,:] = interpolator(x,y)

# find where the slf_data are np.nan
slf_nans=np.isnan(slf_data)

# go through each variable in the slf_data, and if it is nan, then replace
# it with the closest not nan data from the swan_data array
for i in range(numvars):
	for j in range(NPOIN):
		if (slf_nans[i,j] == True):
			xdist = np.subtract(xx,x[j])
			ydist = np.subtract(yy,y[j])
			dist = np.sqrt(np.power(xdist,2.0) + np.power(ydist,2.0))
			minidx = np.argmin(dist)
			
			slf_data[i,j] = swan_data[i,minidx]

# ignores the swan_data x and y variables, and retains depth,hsig,tp,dir
slf_data_red = slf_data[2:,:]

# now we are ready to store the variables into the *.slf array
# assume the varnames and varunits are
varnames = ['DEPTH           ','WAVE HEIGHT     ',\
	'WAVE PERIOD     ','WAVE DIRECTION  ']

varunits = ['M               ','M               ',\
	'SEC             ','DEG             ']

out = ppSELAFIN(output_file)
out.setPrecision(ftype,fsize)
out.setTitle('created with pputils')
out.setVarNames(varnames)
out.setVarUnits(varunits)
out.setIPARAM([1, 0, 0, 0, 0, 0, 0, 0, 0, 1])
out.setMesh(NELEM, NPOIN, NDP, IKLE, IPOBO, x, y)
out.writeHeader()

out.writeVariables(0.0, slf_data_red)

