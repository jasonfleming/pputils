#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 adcirc2dxf.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Feb 15, 2016
#
# Purpose: Script takes in a mesh in ADCIRC format, and generates a dxf
# file of the mesh. Nodes and elements are both written in 3d format.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python adcirc2asc.py -i out.grd -o out.dxf
# where:
# -i input adcirc mesh file
# -o output dxf file of the mesh
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys,time                         # system parameters
import numpy             as np             # numpy
from dxfwrite import DXFEngine as dxf      # for dxf export
from ppmodules.readMesh import *           # to get all readMesh functions
# uses Rick van Hattem's progressbar 
# https://github.com/WoLpH/python-progressbar
from progressbar import ProgressBar, Bar, Percentage, ETA
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
  print('python adcirc2dxf.py -i out.grd -o out.dxf')
  sys.exit()
dummy1 =  sys.argv[1]
adcirc_file = sys.argv[2]
dummy2 =  sys.argv[3]
output_file = sys.argv[4]

# to create the output file
drawing = dxf.drawing(output_file)
#fout = open(output_file,"w")

# read the adcirc file
n,e,x,y,z,ikle = readAdcirc(adcirc_file)

############################################################
# writing nodes
w = [Percentage(), Bar(), ETA()]

pbar = ProgressBar(widgets=w, max_value=n).start()
print('processing nodes')

# create nodes in the dxf file
for i in range(n):
  drawing.add(dxf.point(point=(x[i],y[i],z[i])))
  pbar.update(i+1)
  
pbar.finish()

############################################################
# writing elements

pbar = ProgressBar(widgets=w, max_value=e).start()
print('processing elements')
# to create elements
for i in range(e):
  poly = dxf.polyline()
  #pface = dxf.polyface()
  # create tupples for each vertex
  v0 = (x[ikle[i,0]],y[ikle[i,0]],z[ikle[i,0]])
  v1 = (x[ikle[i,1]],y[ikle[i,1]],z[ikle[i,1]])
  v2 = (x[ikle[i,2]],y[ikle[i,2]],z[ikle[i,2]])
  #pface.add_face([v0, v1, v2], color=256)
  poly.add_vertices( [ v0, v1, v2, v0 ])
  drawing.add(poly)
  #drawing.add(pface)
  pbar.update(i+1)
pbar.finish()

############################################################
print('Writing to file ...')
drawing.save()
