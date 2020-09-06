#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 adcirc2vtk_bin.py                     # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Apr 2, 2016
#
# Purpose: Script takes in a mesh in ADCIRC format, and outputs a binary 
# *.vtk file for visualization on ParaView. This script only uses native
# Python to write the Paraview bindary files (using the struct module).
# 
# Revised: Apr 8, 2017
# Made small changes to the previous version to ensure all data is
# is written as big endian. All data is written as double, which produces
# slightly larger file sizes than float.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python adcirc2vtk.py -i out.grd -o out.vtk
# where:
# -i input adcirc mesh file
# -o output binary *.vtk file
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy as np                         # numpy
from ppmodules.readMesh import *           # to get all readMesh functions
from struct import pack                    # to be able write binary data
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
  print('python adcirc2vtk_bin.py -i out.grd -o out.vtk')
  sys.exit()

adcirc_file = sys.argv[2]
vtk_file = sys.argv[4]

# to create the output files
fout = open(vtk_file,'wb')

# read the adcirc file
n,e,x,y,z,ikle = readAdcirc(adcirc_file)

# column stack xyz
xyz = np.column_stack((x,y,z))

# vtk header file
fout.write(pack('>26s', '# vtk DataFile Version 2.0'.encode()))
fout.write(pack('>c', b'\n'))
fout.write(pack('>20s', 'Created with PPUTILS'.encode()))
fout.write(pack('>c', b'\n'))
fout.write(pack('>6s', 'BINARY'.encode()))
fout.write(pack('>c', b'\n'))
fout.write(pack('>25s', 'DATASET UNSTRUCTURED_GRID'.encode()))
fout.write(pack('>c', b'\n'))

# re-construct the points string
pts_str = 'POINTS ' + str(len(x)) + ' double'
pts_fmt = '>' + str(len(pts_str)) + 's'

# write the points string
fout.write(pack(pts_fmt, pts_str.encode()))
fout.write(pack('>c', b'\n'))

# now write the x y z points
for i in range(len(x)):
  fout.write(pack('>d', x[i]))
  fout.write(pack('>d', y[i]))
  fout.write(pack('>d', 0.0))

# empty line  
fout.write(pack('>c', b'\n'))

# re-construct the cells string
cells_str = 'CELLS ' + str(len(ikle)) + ' ' + str(len(ikle)*4)
cells_fmt = '>' + str(len(cells_str)) + 's'

# write the cells string
fout.write(pack(cells_fmt, cells_str.encode()))
fout.write(pack('>c', b'\n'))

# now write the ikle array
for i in range(len(ikle)):
  fout.write(pack('>i', 3))
  fout.write(pack('>i', ikle[i,0]))
  fout.write(pack('>i', ikle[i,1]))  
  fout.write(pack('>i', ikle[i,2]))
  
# empty line  
fout.write(pack('>c', b'\n'))
  
# re-construct the cell_types string
cell_types_str = 'CELL_TYPES ' + str(len(ikle))
cell_types_fmt = '>' + str(len(cell_types_str)) + 's'

# write the cell_types string
fout.write(pack(cell_types_fmt, cell_types_str.encode()))
fout.write(pack('>c', b'\n'))

# now write the cell_types
for i in range(len(ikle)):
  fout.write(pack('>i', 5 ))

# empty line  
fout.write(pack('>c', b'\n'))

# re-construct the point_data string
point_data_str = 'POINT_DATA ' + str(len(x))
point_data_fmt = '>' + str(len(point_data_str)) + 's'

# write the point_data string
fout.write(pack(point_data_fmt, point_data_str.encode()))
fout.write(pack('>c', b'\n'))

# write SCALARS
fout.write(pack('>16s', 'SCALARS z double'.encode()))
fout.write(pack('>c', b'\n'))

# write LOOKUP_TABLE default
fout.write(pack('>20s', 'LOOKUP_TABLE default'.encode()))
fout.write(pack('>c', b'\n'))

# write the z values
for i in range(len(x)):
  fout.write(pack('>d',z[i]))

print('All done!')  
