#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 adcirc2ply.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Nov 2, 2016
#
# Modified: Nov 9, 2016
# Automatically shift the mesh to the min x and y coordinate in the 
# input mesh. This is needed as MeshLab doesn't retain all of the 
# coordinates when it saves a mesh after a change. The script 
# ply2adcirc.py automatically reads the shift coordinates and re-creates
# the mesh back to the adcirc format to the coorect coordinates.
#
# Purpose: Script takes in a mesh in ADCIRC format, and outputs a *.ply 
# file for visualization and repair with MeshLab. This is useful when a 
# TIN or mesh need to be cleaned and/or repaired.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python adcirc2ply.py -i out.grd -o out.ply
# where:
# -i input adcirc mesh file
# -o output *.ply file
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy             as np             # numpy
from ppmodules.readMesh import *           # to get all readMesh functions
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 5 :
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python adcirc2ply.py -i out.grd -o out.ply')
  sys.exit()
adcirc_file = sys.argv[2]
ply_file = sys.argv[4]

# to create the output files
fout = open(ply_file,'w')

# read the adcirc file
n,e,x,y,z,ikle = readAdcirc(adcirc_file)

# before writing the MeshLab file, find coordinates of x and y min to
# shift the mesh
xref = x[np.argmin(x)] 
yref = y[np.argmin(x)] 

# write these to a file (needed by the ply2adcirc.py script)
plyout = open('ply_shift_coordinates.txt', 'w')
plyout.write(str(xref) + ' ' + str(yref))
plyout.close()

# write the *.ply file
# ply header file
fout.write('ply' + '\n')
fout.write('format ascii 1.0'+ '\n')
fout.write('comment created with pputils'+ '\n')
fout.write('element vertex ' + str(n) + '\n')
fout.write('property float32 x'+ '\n')
fout.write('property float32 y'+ '\n')
fout.write('property float32 z'+ '\n')
fout.write('element face ' + str(e) + '\n')
fout.write('property list uint8 int32 vertex_index'+ '\n')
fout.write('end_header'+ '\n')

# to write the node coordinates
for i in range(len(x)):
  fout.write(str("{:.3f}".format(x[i]-xref)) + ' ' + 
    str("{:.3f}".format(y[i]-yref)) + ' ' + str("{:.3f}".format(z[i])) + 
    '\n')
    
for i in range(len(ikle)):
  fout.write('3 ' + str(ikle[i][0]) + ' ' + str(ikle[i][1]) + ' ' + 
    str(ikle[i][2]) + '\n')
      
