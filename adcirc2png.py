#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 adcirc2png.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Oct 2, 2017
#
# Purpose: Script takes in a mesh in ADCIRC format, and outputs a *.png
# file using Matplotlib for quick visualization. Additional parameters
# that control the levels and zoom are given in the file adcirc2png.cfg.
#
# Revised: Dec 5, 2017
# Made the *.cfg file a required command line input.
#
# Revised: Mar 8, 2018
# If the colour code is set to none, then the script will write only
# the mesh to the *.png file. This is to be used for quick visualization
# of the mesh, without the need to open a mesh viewer.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python adcirc2png.py -i out.grd -o out.png
# where:
# -i input adcirc mesh file
# -o output *.vtk file
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import numpy as np
import matplotlib.tri as mtri
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from ppmodules.readMesh import * 
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
  print('python adcirc2png.py -i out.grd -c adcirc2png.cfg -o out.png')
  sys.exit()
  
adcirc_file = sys.argv[2]
cfg_file = sys.argv[4]
png_file = sys.argv[6]

# reads the sel2png.cfg file for additional parameters
# each line in the file is a list object
line = list()
with open(cfg_file, 'r') as f1:
  for i in f1:
    line.append(i)

# reads the first set of parameters from the *.cfg file
params1 = line[1].split()
    
cbar_min_global = float(params1[0])
cbar_max_global = float(params1[1])
cbar_color_map = params1[2]

# reads the second set of parameters from the *.cfg file
params2 = line[13].split()

zoom = int(params2[0])
xll = float(params2[1])
yll = float(params2[2])
xur = float(params2[3])
yur = float(params2[4])

# reads the third set of parameters from the *.cfg file
params3 = line[23].split()

show_mesh = int(params3[0])
lineweight = float(params3[1])
mesh_color = params3[2]

# read the adcirc file
n,e,x,y,z,ikle = readAdcirc(adcirc_file)

# creates a triangulation grid using matplotlib function Triangulation
triang = mtri.Triangulation(x, y, ikle)

if ((cbar_min_global == -1) and (cbar_max_global == -1)):
  # this is the range of the colour coding
  cbar_min = np.min(z)
  cbar_max = np.max(z)
  
  if ((cbar_max - cbar_min) < 0.001):
    cbar_max = cbar_min + 0.001
else:
  cbar_min = cbar_min_global
  cbar_max = cbar_max_global

# the flag that tells if the limits are default or not
is_default = (cbar_min_global == -1) and (cbar_max_global == -1)

# adjust the plot_array for limits of levels (before plotting)
# added on 2018.07.28
if (cbar_max_global > 0 and is_default == False):
  #print('I am in the +ve section')
  for i in range(len(z)):
    if (z[i] <= cbar_min):
      z[i] = cbar_min + cbar_min*0.01
    if (z[i] >= cbar_max):
      z[i] = cbar_max - cbar_max*0.01

if (cbar_min_global < 0 and cbar_max_global < 0 and is_default == False):
  #print('I am in the -ve section')
  for i in range(len(z)):
    if (z[i] <= cbar_min):
      z[i] = cbar_min - cbar_min*0.01
    if (z[i] >= cbar_max):
      z[i] = cbar_max + cbar_max*0.01

# adjust the levels
levels = np.linspace(cbar_min, cbar_max, 16)

plt.figure()
plt.gca().set_aspect('equal')
if (cbar_color_map != 'none'):
  cmap = cm.get_cmap(name=cbar_color_map)

# this plots the triangulation only
if (show_mesh > 0):
  plt.triplot(triang, lw=lineweight, color=mesh_color)

if (cbar_color_map != 'none'):

  # this plots the colour coded z values
  plt.tricontourf(triang, z, levels=levels, cmap=cmap, antialiased=True)
  
  # this is for the colorbar
  cb = plt.colorbar(orientation='vertical', shrink=0.3,format='%.3f')
  cb.set_ticks(levels)
  cb.ax.tick_params(labelsize=5)
  
  # determine the axis label
  title = 'z [m]'
  
  # set the title, and its size
  cb.ax.set_title(title, size=5)

# axis limits (the zoom flag controls this)
if (zoom > 0):
  plt.xlim(xll,xur)
  plt.ylim(yll,yur)

plt.axis('off')

# this plots the figure
fig = plt.gcf() # returns the reference for the current figure
fig.set_size_inches(12,9)
fig.savefig(png_file, dpi=300, bbox_inches='tight', transparent=False)
plt.close()
