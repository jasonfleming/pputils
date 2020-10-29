#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 interp_mod.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: June 28, 2015
#
# Modified: Feb 21, 2016
# Made it work under python 2 or 3
#
# Modified: Oct 29, 2020
# Made it so that values are assigned only from the area bounded by the
# tin. For nodes in the mesh that fall outside of the tin, current node
# values are retained (and are not modified). This script works when one
# has a tin for only a fraction of the mesh domain, and wants to modify
# values in that area only, leaving everying else unchanged.
#
# Purpose: Script takes in a tin and a mesh file (both in ADCIRC format), 
# and interpolates the nodes of the mesh file from the tin.
#
# Uses: Python 2 or 3, Matplotlib, Numpy
#
# Example:
#
# python interp.py -t tin.grd -m mesh.grd -o mesh_interp.grd
# where:
# -t tin surface
# -m mesh (whose nodes are to be interpolated)
# -o interpolated mesh
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import matplotlib.tri    as mtri           # matplotlib triangulations
import numpy             as np             # numpy
from ppmodules.readMesh import *           # to get all readMesh functions
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
	print('python interp.py -t tin.grd -m mesh.grd -o mesh_interp.grd')
	sys.exit()

dummy1 =  sys.argv[1]
tin_file = sys.argv[2]
dummy2 =  sys.argv[3]
mesh_file = sys.argv[4]
dummy3 =  sys.argv[5]
output_file = sys.argv[6] # interp_mesh

# read the adcirc tin file
t_n,t_e,t_x,t_y,t_z,t_ikle = readAdcirc(tin_file)

# read the adcirc mesh file
# this one has z values that are all zeros
m_n,m_e,m_x,m_y,m_z,m_ikle = readAdcirc(mesh_file)

# create tin triangulation object using matplotlib
tin = mtri.Triangulation(t_x, t_y, t_ikle)

# to perform the triangulation
interpolator = mtri.LinearTriInterpolator(tin, t_z)
m_z_interp = interpolator(m_x, m_y)

# if the node is outside of the boundary of the domain, assign value -999.0
# as the interpolated node
where_are_NaNs = np.isnan(m_z_interp)
m_z_interp[where_are_NaNs] = -999.0

# rather than keeping the -999.0 as the mesh node value outside the tin,
# simply assign to that mesh node the elevation of its original node
for i in range(len(m_x)):
	if (where_are_NaNs[i] == True):
		m_z_interp[i] = m_z[i]

# to create the output file
fout = open(output_file,"w")

# now to write the adcirc mesh file
fout.write("ADCIRC" + "\n")
# writes the number of elements and number of nodes in the header file
fout.write(str(m_e) + " " + str(m_n) + "\n")

# writes the nodes
for i in range(0,m_n):
	fout.write(str(i+1) + " " + str("{:.3f}".format(m_x[i])) + " " + 
		str("{:.3f}".format(m_y[i])) + " " + str("{:.3f}".format(m_z_interp[i])) + "\n")
#
# writes the elements
for i in range(0,m_e):
	fout.write(str(i+1) + " 3 " + str(m_ikle[i,0]+1) + " " + str(m_ikle[i,1]+1) + " " + 
		str(m_ikle[i,2]+1) + "\n")
