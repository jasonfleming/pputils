#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 SWANmat2vtk.py                        # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: December 13, 2015
#
# Modified: Feb 21, 2016
# Made it work for python 2 or 3
#
# Purpose: Script takes in a binary Matlab output file generated by a 
# run from an unstructured SWAN calculation, and outputs the data to a
# a *.vtk file format. Script assumes the SWAN directions are in NAUT
# convention, and that these output variables XP YP DEP HS DIR RTP are 
# specified in the *.swn steering file:
#
# BLOCK 'COMPGRID' NOHEAD 'out.mat' LAY 3 XP YP DEP HS DIR RTP
#
# If there are other variables present, the script simply ignores them
#
# For now, it only works for stationary SWAN simulations.
# TODO: update for non-stationary output as well
#
# Uses: Python 2 or 3, Numpy, Scipy
#
# Example:
#
# python SWANmat2vtk.py -m out.grd -i out.mat -o out.vtk
# where:
# -m mesh which was used by unstructured swan
# -i output *.mat file generated by unstructured swan
# -o output *.csv file 
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy             as np             # numpy
import math
import scipy.io          as io             # scipy's io functions for loadmat()
from ppmodules.readMesh import *           # to get all readMesh functions
from ppmodules.writeMesh import *          # to get all writeMesh functions
#
if len(sys.argv) != 7:
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python SWANmat2vtk.py -m out.grd -i out.mat -o out.txt')
	sys.exit()

# I/O
adcirc_file = sys.argv[2]        # input *.grd file (adcirc mesh file)
input_file = sys.argv[4]         # input *.mat file (swan output)
output_file = sys.argv[6]        # output *.vtk file 

# output *.csv file
fout = open(output_file, "w")

# uses scipy's loadmat function, and produces one master dictionary
mat = io.loadmat(input_file)

# remove from the dictionary __header__, __version__, __globals__
# it assumes all of these dictionary keys already exist 
mat.pop('__header__', None)
mat.pop('__version__', None)
mat.pop('__globals__', None)
mat.pop('Yp', None)
mat.pop('Xp', None)

# get the dict keys (i.e., var names)
v = list(mat.keys())

for i in range (len(v)):
	# find the variables in the mat dictionary
	if (v[i].find('Hsig') > -1):
		Hsig = mat['Hsig'][0,:]
	elif(v[i].find('RTpeak') > -1):
		RTpeak = mat['RTpeak'][0,:]
	elif(v[i].find('Dir') > -1):
		Dir = mat['Dir'][0,:]
	elif(v[i].find('Depth') > -1):
		Depth = mat['Depth'][0,:]
		
num_pts = len(Depth)

# in case the fort.14 file in SWAN calculations has a -ve depth (i.e., an
# elevation value above Chart Datum, SWAN assigns a nan to this node)
for i in range(num_pts):
	if (Depth[i] < 0.0):
		Hsig[i] = 0.0
		RTpeak[i] = 0.0
		Dir[i] = 0.0
		
# create wx and wy cartesian unit vectors from the Dir (in nautical conv)
wx = np.zeros(num_pts)
wy = np.zeros(num_pts)

for i in range(num_pts):
	if ((Dir[i] >= 0) and (Dir[i] <= 90)):
		Dir_rad = Dir[i] * 3.141592654 / 180.0
		wx[i] = -1.0 * math.sin(Dir_rad) * Hsig[i]
		wy[i] = -1.0 * math.cos(Dir_rad) * Hsig[i]
	
	elif ((Dir[i] > 90) and (Dir[i] <= 180)):
		Dir_rad = (180 - Dir[i]) * 3.141592654 / 180.0
		wx[i] = -1.0 * math.sin(Dir_rad)* Hsig[i]
		wy[i] = math.cos(Dir_rad)* Hsig[i]
	
	elif ((Dir[i] > 180) and (Dir[i] <= 270)):
		Dir_rad = (Dir[i]-180) * 3.141592654 / 180.0
		wx[i] = math.sin(Dir_rad)* Hsig[i]
		wy[i] = math.cos(Dir_rad)* Hsig[i]
	
	elif ((Dir[i] > 270) and (Dir[i] <= 360)):
		Dir_rad = (360-Dir[i]) * 3.141592654 / 180.0
		wx[i] = math.sin(Dir_rad)* Hsig[i]
		wy[i] = -1.0 * math.cos(Dir_rad)* Hsig[i]

# now reads the adcirc file
# read the adcirc mesh file
n,e,x,y,z,ikle = readAdcirc(adcirc_file)

# write the *.vtk file

# vtk header file
fout.write('# vtk DataFile Version 3.0' + '\n')
fout.write('Created with pputils' + '\n')
fout.write('ASCII' + '\n')
fout.write('' + '\n')
fout.write('DATASET UNSTRUCTURED_GRID' + '\n')
fout.write('POINTS ' + str(len(x)) + ' float' + '\n')

# to write the node coordinates
for i in range(len(x)):
	fout.write(str("{:.3f}".format(x[i])) + ' ' + 
		str("{:.3f}".format(y[i])) + ' ' + str("{:.3f}".format(0.0)) + '\n')
		
# to write the node connectivity table
fout.write('CELLS ' + str(len(ikle)) + ' ' + str(len(ikle)*4) + '\n')

for i in range(len(ikle)):
	fout.write('3 ' + str(ikle[i][0]) + ' ' + str(ikle[i][1]) + ' ' + 
		str(ikle[i][2]) + '\n')
		
# to write the cell types
fout.write('CELL_TYPES ' + str(len(ikle)) + '\n')
for i in range(len(ikle)):
	fout.write('5' + '\n')
	
# write the empty line
fout.write('' + '\n')

# write the data
fout.write('POINT_DATA ' + str(len(x)) + '\n')

# write the vector data
fout.write('VECTORS Wave_Dir float' + '\n')
for i in range(len(x)):
	fout.write(str("{:.4f}".format(wx[i])) + ' ' + 
		str("{:.4f}".format(wy[i])) + ' 0.0' + '\n')

# write the scalar data 
fout.write('SCALARS ' + 'Hsig' + '\n')
fout.write('float' + '\n')
fout.write('LOOKUP_TABLE default' + '\n')
for i in range(len(x)):
	fout.write(str("{:.3f}".format(Hsig[i])) + '\n')

fout.write('SCALARS ' + 'RTpeak' + '\n')
fout.write('float' + '\n')
fout.write('LOOKUP_TABLE default' + '\n')
for i in range(len(x)):
	fout.write(str("{:.3f}".format(RTpeak[i])) + '\n')
	
fout.write('SCALARS ' + 'Depth' + '\n')
fout.write('float' + '\n')
fout.write('LOOKUP_TABLE default' + '\n')
for i in range(len(x)):
	fout.write(str("{:.3f}".format(Depth[i])) + '\n')
