#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 rotate_pts.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: June 20, 2020
#
# Purpose: Script takes in a points file and rotates it about a point
# specified, with the rotation angle specified.
#
# Uses: Python 2 or 3, Numpy, Scipy
#
# Example:
#
# python rotate_pts.py -i in.csv -s 100 199 30 -o in_rot.grd
# where:
# -i input csv xyz file
# -s rotates the mesh about (100,199), using 30 deg (+ve is CCW w.r.t. x-axis)
# -o output csv that is rotated
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy as np                         # numpy
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
  print('python rotate_pts.py -i in.csv -s 100 199 30 -o in_rot.grd')
  sys.exit()

input_file = sys.argv[2]
x_coord = float(sys.argv[4])
y_coord = float(sys.argv[5])
angle = float(sys.argv[6])
output_file = sys.argv[8]

# read the input xyz file
pts_data = np.loadtxt(input_file, delimiter=',',skiprows=0,unpack=True)

x = pts_data[0,:]
y = pts_data[1,:]
z = pts_data[2,:]

print('Performing rotation about:')
print(str(x_coord) + ' ' + str(y_coord))

# convert angle to radians
angle_rad = angle * np.pi / (180.0)

# now create the rotated points
x_rot = (x-x_coord) * np.cos(angle_rad) -(y-y_coord) * np.sin(angle_rad)
y_rot = (y-y_coord) * np.cos(angle_rad) + (x-x_coord) * np.sin(angle_rad)

x_rot = x_rot + x_coord
y_rot = y_rot + y_coord

# this is the output pts file (i.e., rotated pts)
fout = open(output_file, 'w')

# writes the nodes
for i in range(len(x)):
  fout.write(str('{:.3f}'.format(x_rot[i])) + ',' +
    str('{:.3f}'.format(y_rot[i])) + ',' + str('{:.3f}'.format(z[i])) + '\n')

print('All done!')
