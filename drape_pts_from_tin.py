#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 drape_pts_from_tin.py                 # 
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
# Purpose: Script takes in a tin and a xy pts file, and drapes the pts 
# over the tin. The output is a xyz file with draped z value.
#
# Uses: Python 2 or 3, Matplotlib, Numpy
#
# Example:
#
# python drape_pts_from_tin.py -t tin.grd -p pts.csv -o pts_draped.xyz
# where:
# -t tin surface
# -p points file
# -o points file, draped
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
  print('python drape_pts_from_tin.py -t tin.grd -p pts.csv -o pts_draped.xyz')
  sys.exit()


tin_file = sys.argv[2]
points_file = sys.argv[4]
output_file = sys.argv[6]

# read the adcirc tin file
t_n,t_e,t_x,t_y,t_z,t_ikle = readAdcirc(tin_file)

# read the points file
points_data = np.loadtxt(points_file, delimiter=',',skiprows=0,unpack=True)

# assumes xyz in points file, comma delimited
p_x = points_data[0,:]
p_y = points_data[1,:]
p_z = points_data[2,:]

# create tin triangulation object using matplotlib
tin = mtri.Triangulation(t_x, t_y, t_ikle)

# to perform the triangulation
interpolator = mtri.LinearTriInterpolator(tin, t_z)
p_z = interpolator(p_x, p_y)

# if the node is outside of the boundary of the domain, assign value -999.0
# as the interpolated node
where_are_NaNs = np.isnan(p_z)
p_z[where_are_NaNs] = -999.0

# rather than keeping the -999.0 as the mesh node value outside the tin,
# simply assign to that mesh node the elevation of the closest tin node.
for i in range(len(p_x)):
  if (where_are_NaNs[i] == True):
    xdist = np.subtract(t_x,p_x[i])
    ydist = np.subtract(t_y,p_y[i])
    dist = np.sqrt(np.power(xdist,2.0) + np.power(ydist,2.0))
    minidx = np.argmin(dist)
    
    p_z[i] = t_z[minidx]

# to create the output file
fout = open(output_file,"w")

# now to write the draped points file
for i in range(len(p_x)):
  fout.write(str(p_x[i]) + ',' + str(p_y[i]) + ',' + str(p_z[i]) + '\n')
  
fout.close()


