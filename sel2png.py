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
# vector magnitude, and plot its result. Note that this script needs to
# read the configuration file titled sel2png.cfg, as additional options
# are specified in the *.cfg file.
#
# Revised: Oct 3, 2017
# Changed the parameters in the sel2png.py configuration file, and added
# the ability to plot vectors. It works for plotting vectors on all mesh
# nodes, and on a user specified grid of points.
#
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

# reads the first set of parameters from the sel2png.cfg file
params1 = line[1].split()
    
cbar_min_global = float(params1[0])
cbar_max_global = float(params1[1])
cbar_color_map = params1[2]

# reads the second set of parameters from the sel2png.cfg file
params2 = line[11].split()

vectors = int(params2[0])
vector_scale = float(params2[1])
vector_width = float(params2[2])
vector_color = str(params2[3])
vector_grid = int(params2[4])
vector_grid_size = float(params2[5])

# reads the third set of parameters from the sel2png.cfg file
params3 = line[24].split()

zoom = int(params3[0])
xll = float(params3[1])
yll = float(params3[2])
xur = float(params3[3])
yur = float(params3[4])

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

# the vector variables that it searches for
# for telemac2d
idx_vel_u = -1000
idx_vel_v = -1000

# for tomawac
idx_mean_dir = -1000
idx_wave_height = -1000

# for artemis
idx_art_wave_inc = -1000
idx_art_wave_height = -1000

# find the index of the vector variables
for i in range(len(variables)):
  if (variables[i].find('VELOCITY U') > -1):
    idx_vel_u = i
  elif (variables[i].find('VELOCITY V') > -1):
    idx_vel_v = i
  elif (variables[i].find('MEAN DIRECTION') > -1):
    idx_mean_dir = i
  elif (variables[i].find('WAVE HEIGHT HM0') > -1):
    idx_wave_height = i
  elif (variables[i].find('WAVE HEIGHT') > -1):
    idx_art_wave_height = i
  elif (variables[i].find('WAVE INCIDENCE') > -1):
    idx_art_wave_inc = i
  
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

# define u and v for plotting (if needed)
u = np.zeros(NPOIN)
v = np.zeros(NPOIN)

# the IKLE array starts at element 1, but matplotlib needs it to start
# at zero
IKLE[:,:] = IKLE[:,:] - 1

# create a Matplotlib triangulation object
triang = mtri.Triangulation(x,y,IKLE)

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

  '''
  # adjust the plot_array for limits of levels (before plotting)
  for i in range(len(plot_array)):
    if (plot_array[i] < cbar_min):
      plot_array[i] = cbar_min
    if (plot_array[i] > cbar_max):
      plot_array[i] = cbar_max
  '''

  # adjust the levels
  levels = np.linspace(cbar_min, cbar_max, 16)
  
  plt.figure()
  plt.gca().set_aspect('equal')
  cmap = cm.get_cmap(name=cbar_color_map)
  plt.tricontourf(triang, plot_array, levels=levels,
    cmap=cmap, antialiased=True)
  
  # axis limits (the zoom flag controls this)
  if (zoom > 0):
    plt.xlim(xll,xur)
    plt.ylim(yll,yur)

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
  
  # to plot the vectors (if vector flag is on)
  if (vectors > 0):
    
    # now we must find the vector variables to plot
    # it will find telemac2d velocity vector, tomawac's mean direction, and
    # artemis's wave_incidence vector

    # for telemac2d
    if ((idx_vel_u > -1000) and (idx_vel_v > -1000)):
      u = master_results[idx_vel_u]
      v = master_results[idx_vel_v]

    # for tomawac  
    elif ((idx_mean_dir > -1000) and (idx_wave_height > -1000)):
      for i in range(len(x)):
        u[i] = np.sin(master_results[idx_mean_dir][i] * np.pi / 180.0) * \
            master_results[idx_wave_height][i]
        v[i] = np.cos(master_results[idx_mean_dir][i] * np.pi / 180.0) * \
            master_results[idx_wave_height][i]

    # for artemis
    elif ((idx_art_wave_height > -1000) and (idx_art_wave_inc > -1000) ):
      for i in range(len(x)):
        u[i] = np.cos(master_results[idx_art_wave_inc][i] * np.pi / 180.0) * \
            master_results[idx_art_wave_height][i]
        v[i] = np.sin(master_results[idx_art_wave_inc][i] * np.pi / 180.0) * \
            master_results[idx_art_wave_height][i]
    else:
      print('Vector variable not found in file. Exiting.')
      sys.exit()

    if (vector_grid > 0):
      # plot the vectors on a grid
      # we now have to convert the u and v to a regular vector based on the
      # vector_grid_size parameter, the code here is taken from adcirc2asc.py

      # to accomodate code pasting
      spacing = vector_grid_size
      
      # determine the spacing of the regular grid
      range_in_x = float(np.max(x) - np.min(x))
      range_in_y = float(np.max(y) - np.min(y))

      max_range = max(range_in_x, range_in_y)
      
      # first index is integer divider, second is remainder
      num_x_pts = divmod(range_in_x, spacing)
      num_y_pts = divmod(range_in_y, spacing)
      
      # creates the regular grid
      xreg, yreg = np.meshgrid(np.linspace(np.min(x), np.max(x), int(num_x_pts[0])),
        np.linspace(np.min(y), np.max(y), int(num_y_pts[0])))
      x_regs = xreg[1,:]
      y_regs = yreg[:,1]

      # perform the triangulation
      interpolator = mtri.LinearTriInterpolator(triang, u)
      u_grid = interpolator(xreg, yreg)

      interpolator = mtri.LinearTriInterpolator(triang, v)
      v_grid = interpolator(xreg, yreg)

      # matplotlib automatically manages np.nan's
      # now, we are ready to plot the vectors
      
      # width is the shaft width of the arrows
      plt.quiver(x_regs, y_regs, u_grid, v_grid,
        width=vector_width, pivot='middle', color=vector_color,
        angles='xy', scale_units='xy',
        scale=1.0/vector_scale)
                                          
    else:
      # plot the vectors at every node point
      plt.quiver(x, y, u, v, pivot='middle',width=vector_width,
        color=vector_color, angles='xy', scale_units='xy',
        scale=1.0/vector_scale)
  
  # this plots the figure
  fig = plt.gcf() # returns the reference for the current figure
  fig.set_size_inches(12,9)
  fig.savefig(file_out[count], dpi=300, bbox_inches='tight', transparent=False)
  plt.close()
  
