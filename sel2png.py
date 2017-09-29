#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 sel2png.py                            # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng. 
# 
# Date: Sep 29, 2017
#
# Purpose: Script designed to open 2D telemac binary file, read the
# desired output variable and create a series of *.png files. If the user
# does not specify starting and ending time step, the script will create
# a plot for the specified variable for every time step in the file. In
# case two variables are specified, the script will simply compute their
# vector magnitude, and plot its result.
# 
# Using: Python 2 or 3, Matplotlib, Numpy
#
# Example: python sel2png.py -i input.slf -v 4 -o output.png
#          python sel2png.py -i input.slf -v 0 1 -o output.png
#          python sel2png.py -i input.slf -v 4 -o output.png -s 1 -e 6
#          python sel2png.py -i input.slf -v 0 1 -o output.png -s 1 -e 6
# 
# where:
#       --> -i is the *.slf file as input
#
#       --> -v is the index of the variable to extract; see probe.py for 
#                        index codes of the variables; can have two values
#                        when the user is computing magnitude
#
#       --> -o is the *.png output file
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import matplotlib.tri as mtri
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from ppmodules.selafin_io_pp import *

if len(sys.argv) == 7:
  input_file = sys.argv[2]         
  var_index1  = int(sys.argv[4])
  var_index2 = -999
  output_file = sys.argv[6]
  t_start = 0
  t_end = 0
elif len(sys.argv) == 11:
  input_file = sys.argv[2]         
  var_index1  = int(sys.argv[4])
  var_index2 = -999
  output_file = sys.argv[6]
  t_start = int(sys.argv[8])
  t_end = int(sys.argv[10])
elif len(sys.argv) == 8:
  input_file = sys.argv[2]         
  var_index1 = int(sys.argv[4])
  var_index2 = int(sys.argv[5])          
  output_file = sys.argv[7]
  t_start = 0
  t_end = 0
elif len(sys.argv) == 12:
  input_file = sys.argv[2]
  var_index1 = int(sys.argv[4])
  var_index2 = int(sys.argv[5])          
  output_file = sys.argv[7]
  t_start = int(sys.argv[9])
  t_end = int(sys.argv[11])
else: 
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python sel2png.py -i input.slf -v 4 -o output.png')
  print('python sel2png.py -i input.slf -v 4 5 -o output.png')
  print('python sel2png.py -i input.slf -v 4 -o output.png -s 1 -e 5')
  print('python sel2png.py -i input.slf -v 4 5 -o output.png -s 1 -e 5')
  sys.exit()

# reads the sel2png.cfg file for additional parameters
# each line in the file is a list object
line = list()
with open('sel2png.cfg', 'r') as f1:
  for i in f1:
    line.append(i)

# reads the parameters from the sel2png.cfg file
params = line[1].split()
    
cbar_min_global = float(params[0])
cbar_max_global = float(params[1])
vector_flag = int(params[2])
vector_scale = float(params[3])
vector_color = str(params[4])

# Read the header of the selafin result file and get geometry and
# variable names and units

# use selafin_io_pp class ppSELAFIN
slf = ppSELAFIN(input_file)
slf.readHeader()
slf.readTimes()

# gets the number of planes
NPLAN = slf.getNPLAN()

if (NPLAN > 1):
  print('3d SELAFIN files are not yet supported. Exiting!')
  sys.exit()

# read times, variables and units
times = slf.getTimes()
variables = slf.getVarNames()
units = slf.getVarUnits()

# update the index of t_end
# len(times) gives total number of items in the array
# len(times) - 1 is the index of the last element
if (len(sys.argv) == 7 or len(sys.argv) == 8):
  t_end = len(times)-1

# to remove duplicate spaces from variables
for i in range(len(variables)):
  variables[i] = ' '.join(variables[i].split())
  units[i] = ' '.join(units[i].split())

# gets some of the mesh properties from the *.slf file
NELEM, NPOIN, NDP, IKLE, IPOBO, x, y = slf.getMesh()

# the IKLE array starts at element 1, but matplotlib needs it to start
# at zero
IKLE[:,:] = IKLE[:,:] - 1

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
  
# to check if the idx_list is within times list
if (idx_list[0] not in idx_times):
  print('Starting time specified not in *.slf file. Exiting.')
  sys.exit()
elif (idx_list[-1] not in idx_times):
  print('Ending time specified not in *.slf file. Exiting.')
  sys.exit()

# this is the same as my sel2vtk.py script
for count, item in enumerate(filenames):
  print('Writing file ' + item)
  file_out.append(item)

  # file_out[count] is the file that will be saved
  slf.readVariables(idx_list[count])
  master_results = slf.getVarValues()

  # if two variable indices were specified, compute vector magnitude
  if (var_index2 > 0):
    plot_array = np.sqrt(np.power(master_results[var_index1],2) +
      np.power(master_results[var_index2],2))
  else:
    plot_array = master_results[var_index1]
  
  # creates a triangulation grid using matplotlib function Triangulation
  triang = mtri.Triangulation(x, y, IKLE)
  
  if ((cbar_min_global == -1) and (cbar_max_global == -1)):
    # this is the range of the colour coding
    cbar_min = np.min(plot_array)
    cbar_max = np.max(plot_array)
    
    if ((cbar_max - cbar_min) < 0.001):
      cbar_max = cbar_min + 0.001
  else:
    cbar_min = cbar_min_global
    cbar_max = cbar_max_global
      
  levels = np.linspace(cbar_min, cbar_max, 16)
  #levels = np.linspace(0, 5, 16)
  
  plt.figure()
  plt.gca().set_aspect('equal')
  cmap = cm.get_cmap(name='jet') # 'jet', 'terrain', for reverse use jet_r
  plt.tricontourf(triang, plot_array, levels=levels,
    cmap=cmap, antialiased=True)
  
  # axis limits
  #plt.xlim(449575,449875)
  #plt.ylim(4705998,4706398)
  plt.axis('off')
  
  # this is for the colorbar
  cb = plt.colorbar(orientation='vertical', shrink=0.3,format='%.3f')
  cb.set_ticks(levels)
  cb.ax.tick_params(labelsize=5)
  
  # determine the axis label
  if (var_index2 > 0):
    title = 'Vel Mag [m/s]'
  else:
    title = variables[var_index1] + ' [' + units[var_index1] + ']'
  
  # set the title, and its size
  cb.ax.set_title(title, size=5)
  
  # to plot the vectors
  #u = master_results[0]
  #v = master_results[1]
  #plt.quiver(x, y, u, v, width=0.0005, pivot='middle', color='white')
  
  # this plots the figure
  fig = plt.gcf() # returns the reference for the current figure
  fig.set_size_inches(12,9)
  fig.savefig(file_out[count], dpi=300, bbox_inches='tight', transparent=False)
  plt.close()
  
