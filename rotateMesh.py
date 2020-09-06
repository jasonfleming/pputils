#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 rotateMesh.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: July 15, 2017
#
# Purpose: Script takes in an ADCIRC mesh and rotates it about a point
# specified, with the rotation specified.
#
# Uses: Python 2 or 3, Numpy, Scipy
#
# Example:
#
# python rotateMesh.py -i out.grd -s 100 199 30 -o out_rotated.grd
# where:
# -i mesh in ADCIRC format
# -s rotates the mesh about (100,199), using 30 deg (+ve is CCW w.r.t. x-axis)
# -o output mesh that is rotated
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy as np                         # numpy
from scipy import spatial                  # to get the cKDTree      
from ppmodules.readMesh import *           # to get all readMesh functions
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 9 :
  print('Wrong number of arguments, stopping now...')
  print('Usage:')
  print('python rotateMesh.py -i out.grd -s 100 199 30 -o out_rotated.grd')
  sys.exit()

input_file = sys.argv[2]
x_coord = float(sys.argv[4])
y_coord = float(sys.argv[5])
angle = float(sys.argv[6])
output_file = sys.argv[8]

# read the adcirc mesh file
n,e,x,y,z,ikle = readAdcirc(input_file)

# find the mesh node that is nearest to the entered coordinate
# use cKDTree to perform the search

# create a KDTree object
source = np.column_stack((x,y))
tree = spatial.cKDTree(source)

# find the index of the node the user is seeking
d, idx = tree.query((x_coord,y_coord), k = 1)

print('Performing rotation about:')
print(str(x[idx]) + ' ' + str(y[idx]))

# convert angle to radians
angle_rad = angle * np.pi / (180.0)

# now create the rotated points
'''
x_rot = np.zeros(n)
y_rot = np.zeros(n)

for i in range(n):
  x_rot[i] = ((x[i] - x_coord) * np.cos(angle_rad)) - ((y[i] - y_coord) * np.sin(angle_rad))
  y_rot[i] = ((x[i] - x_coord) * np.sin(angle_rad)) + ((y[i] - y_coord) * np.cos(angle_rad))

# now shift
for i in range(n):
  x_rot[i] = x_rot[i] + x_coord
  y_rot[i] = y_rot[i] + y_coord
'''
# this is vectorized
x_rot = (x-x_coord) * np.cos(angle_rad) -(y-y_coord) * np.sin(angle_rad)
y_rot = (y-y_coord) * np.cos(angle_rad) + (x-x_coord) * np.sin(angle_rad)

x_rot = x_rot + x_coord
y_rot = y_rot + y_coord

# this is the adcirc output mesh (i.e., rotated mesh)
fout = open(output_file, 'w')

# now to write the adcirc mesh file
fout.write('ADCIRC' + '\n')
# writes the number of elements and number of nodes in the header file
fout.write(str(e) + ' ' + str(n) + '\n')

# writes the nodes
for i in range(n):
  fout.write(str(i+1) + ' ' + str('{:.3f}'.format(x_rot[i])) + ' ' +
    str('{:.3f}'.format(y_rot[i])) + ' ' + str('{:.3f}'.format(z[i])) + '\n')

# writes the elements
for i in range(e):
  fout.write(str(i+1) + ' 3 ' + str(ikle[i,0]+1) + ' ' +
    str(ikle[i,1]+1) + ' ' +  str(ikle[i,2]+1) + '\n')  

print('All done!')
