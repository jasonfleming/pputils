#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 spe2png.py                            # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Feb 20, 2018
#
# Purpose: Script takes in a spectral file produced by TOMAWAC, and
# outputs a *.png file using Matplotlib for quick visualization.
# Additional parameters that control the levels and zoom are given in
# the *.cfg file.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python spe2png.py -i out.spe -c spe2cfg.cfg -v 0 -o out.png -s 0 -e 10
# where:
# -i input spectral file (ikle are quads, NDP = 4 in this case)
# -c the input *.cfg file that has some additional parameters for plotting
# -v which node of the spectral file to output
# -s and -e the starting and ending time index of the spectral file
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import numpy as np
import matplotlib.tri as mtri
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from ppmodules.selafin_io_pp import *
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
curdir = os.getcwd()

if len(sys.argv) == 9:
  input_file = sys.argv[2]
  cfg_file = sys.argv[4]
  var_index = int(sys.argv[6])
  output_file = sys.argv[8]
  t_start = 0
  t_end = 0
elif len(sys.argv) == 13:
  input_file = sys.argv[2]
  cfg_file = sys.argv[4]
  var_index = int(sys.argv[6])
  output_file = sys.argv[8]
  t_start = int(sys.argv[10])
  t_end = int(sys.argv[12])
else:
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python spe2png.py -i input.slf -c spe2png.cfg -v 4 -o output.png')
  print('python spe2png.py -i input.slf -c spe2png.cfg -v 4 -o output.png -s 1 -e 5')
  sys.exit()  
  
# reads the spe2png.cfg file for additional parameters
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

# reads the third set of parameters from the *.cfg file
params2 = line[11].split()

show_mesh = int(params2[0])
lineweight = float(params2[1])
mesh_color = params2[2]

# read the existing spectral file
slf = ppSELAFIN(input_file)
slf.readHeader()
slf.readTimes()

# index of the time step
times = slf.getTimes()

# update the index of t_end
# len(times) gives total number of items in the array
# len(times) - 1 is the index of the last element
if (len(sys.argv) == 9):
  t_end = len(times)-1

# gets the info from the spectral file and stores into approrpiate vars
ELEM,NPOIN,NDP,IKLE,IPOBO,x,y = slf.getMesh()

# to create a list of files
file_out = list()

# list of time indices in *.slf file
idx_times = np.arange(len(times))

# initialize the index list of time steps to extract
idx_list = list()

# create a list of filenames based on time records in the slf file
filenames = list()
for i in range(t_start, t_end+1, 1):
  filenames.append(output_file.split('.',1)[0] + '_' +
    '{:0>5d}'.format(i) + '.png')
  idx_list.append(i)

# to check if the input file is really a spectral file
if (NDP !=4):
  print('The input file has triangle, not quads. Exiting!.')
  sys.exit(0)

# now we split the quads into triangles, so that they can be plotted using
# matplotlib's Triangulation class

ELEM2 = ELEM * 2
IKLE2 = np.zeros( (ELEM2, 3), dtype=np.int32)

for i in range(ELEM):
  IKLE2[2*i-1,0] = IKLE[i,0]
  IKLE2[2*i-1,1] = IKLE[i,1]
  IKLE2[2*i-1,2] = IKLE[i,2]
  
  IKLE2[2*i,0] = IKLE[i,0]
  IKLE2[2*i,1] = IKLE[i,2]
  IKLE2[2*i,2] = IKLE[i,3]

# make the indexes zero based
IKLE2[:,0] = IKLE2[:,0] - 1
IKLE2[:,1] = IKLE2[:,1] - 1
IKLE2[:,2] = IKLE2[:,2] - 1

# this is the same as my sel2vtk.py script
for count, item in enumerate(filenames):
  print('Writing file ' + item)
  file_out.append(item)

  # file_out[count] is the file that will be saved
  slf.readVariables(idx_list[count])
  master_results = slf.getVarValues()
  plot_array = master_results[var_index]
  
  # now that we have the IKLE2 array, we are ready to triangulate and plot
  # creates a triangulation grid using matplotlib function Triangulation
  triang = mtri.Triangulation(x, y, IKLE2)

  if ((cbar_min_global == -1) and (cbar_max_global == -1)):
    # this is the range of the colour coding
    cbar_min = np.min(plot_array)
    cbar_max = np.max(plot_array)
    
    if ((cbar_max - cbar_min) < 1.0e-6):
      cbar_max = cbar_min + 1.0e-6
  else:
    cbar_min = cbar_min_global
    cbar_max = cbar_max_global

  # adjust the levels
  levels = np.linspace(cbar_min, cbar_max, 16)

  plt.figure()
  plt.gca().set_aspect('equal')
  cmap = cm.get_cmap(name=cbar_color_map)
  
  # this plots the triangulation only
  if (show_mesh > 0):
    plt.triplot(triang, lw=lineweight, color=mesh_color)
  
  # this plots the colour coded z values
  plt.tricontourf(triang, plot_array, levels=levels, cmap=cmap, antialiased=True)
  
  # this is for the colorbar
  cb = plt.colorbar(orientation='vertical', shrink=0.5,format='%.3e')
  cb.set_ticks(levels)
  cb.ax.tick_params(labelsize=8)
  
  # determine the axis label
  title = 'spectral density [-]'
  
  # set the title, and its size
  cb.ax.set_title(title, size=8)
  
  plt.axis('off')
  
  # this plots the figure
  fig = plt.gcf() # returns the reference for the current figure
  fig.set_size_inches(12,9)
  fig.savefig(file_out[count], dpi=300, bbox_inches='tight', transparent=False)
  plt.close()
