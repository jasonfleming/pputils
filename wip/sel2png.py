#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 sel2png.py                            # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng. 
# 
# Date: Aug 6, 2017
#
# Purpose: Script designed to open 2D telemac binary file, read the
# the desired output variable for a desired time step, and create a
# *.png file out of the output. TODO: figure out how to incorporate
# vectors into the plot.
# 
# Using: Python 2 or 3, Matplotlib, Numpy
#
# Example: python sel2png.py -i input.slf -v 4 -t 0 -o output.png
# 
# where:
#       --> -i is the *.slf file as input
#
#       --> -v is the index of the variable to extract; see probe.py for 
#                        index codes of the variables
#
#       --> -t is the index of the time step to extract; see probe.py for
#                        index codes of the time steps
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

if len(sys.argv) != 9:
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python sel2png.py -i input.slf -v 4 -t 0 -o output.png')
  sys.exit()

input_file = sys.argv[2]         # input *.slf file
var_index  = int(sys.argv[4])    # index number of grided output variable 
t = int(sys.argv[6])             # index of time record (integer, 0 to n) 
output_file = sys.argv[8]        # output *.flt grid file

# Read the header of the selafin result file and get geometry and
# variable names and units

# use selafin_io_pp class ppSELAFIN
slf = ppSELAFIN(input_file)
slf.readHeader()
slf.readTimes()
slf.readVariables(t)

# gets some of the mesh properties from the *.slf file
NELEM, NPOIN, NDP, IKLE, IPOBO, x, y = slf.getMesh()

# the IKLE array starts at element 1, but matplotlib needs it to start
# at zero
IKLE[:,:] = IKLE[:,:] - 1

# these are the results for all variables, for time step t
master_results = slf.getVarValues() 

# creates a triangulation grid using matplotlib function Triangulation
triang = mtri.Triangulation(x, y, IKLE)

# this is the range of the colour coding
cbar_min = np.min(master_results[var_index])
cbar_max = np.max(master_results[var_index])
levels = np.linspace(cbar_min, cbar_max, 16)
levels = np.linspace(0, 5, 16)

# now to plot the desired variable, for the desired time step, for the desired variable
plt.figure()
plt.gca().set_aspect('equal')
cmap = cm.get_cmap(name='jet') # 'jet', 'terrain', for reverse use jet_r
plt.tricontourf(triang, master_results[var_index], levels=levels, 
  cmap=cmap, antialiased=True)

# axis limits
#plt.xlim(449575,449875)
#plt.ylim(4705998,4706398)
plt.axis('off')

# this is for the colorbar
cb = plt.colorbar(orientation='vertical', shrink=0.75)
cb.set_ticks(levels)
#cb.ax.set_title('Sig. Wave Height [m]')

# to plot the vectors
#u = master_results[0]
#v = master_results[1]
#plt.quiver(x, y, u, v, width=0.0005, pivot='middle', color='white')

# this plots the figure
fig = plt.gcf() # returns the reference for the current figure
fig.set_size_inches(12,9)
fig.savefig(output_file, dpi=300, bbox_inches='tight')



