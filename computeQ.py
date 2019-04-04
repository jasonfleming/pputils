#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 computeQ.py                           # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Apr 5, 2018
#
# Purpose: Script takes in a *.slf file (2d for now), and computes the
# discharge through sections (which have to be re-sampled and be 
# provided in PPUTILS line format). The cross sections have to be
# defined such that they are perpedicular to the flow. If the sections
# are not perpedicular to the flow, garbage results may be reported.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python computeQ.py -i result.slf -l line.csv -o line_Q.csv
# where:
#
# -i ==> 2d *.slf result file, containing variables depth and velocity
# -l ==> PPUTILS formatted line fine, resampled (shapeid,x,y columns) 
# -o ==> output *.csv file, which prints a time series of Q for each 
#        section in the -l file
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy             as np             # numpy
import matplotlib.tri    as mtri           # matplotlib triangulations
from ppmodules.selafin_io_pp import *      # to get SELAFIN I/O 
from ppmodules.utilities import *          # to get the utilities
from scipy.integrate import simps          # simpson's rule integration 
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 7:
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python computeQ.py -i result.slf -l line.csv -o line_Q.csv')
  sys.exit()

input_file = sys.argv[2]
lines_file = sys.argv[4]
output_file = sys.argv[6]

# now read the input *.slf geometry file
slf = ppSELAFIN(input_file)
slf.readHeader()
slf.readTimes()

times = slf.getTimes()
vnames = slf.getVarNames()
vunits = slf.getVarUnits()
x = slf.getMeshX()
y = slf.getMeshY()
IKLE= slf.getIKLE()
NPOIN = len(x)

# determine if the *.slf file is 2d or 3d by reading how many planes it has
NPLAN = slf.getNPLAN()

if NPLAN > 1:
  print('3d *.slf files not supported yet. Exiting!')
  sys.exit(0)

# the number of time steps in the *.slf file
ntimes = len(times)

# use numpy to read the lines file in pputils format
lines_data = np.loadtxt(lines_file, delimiter=',',skiprows=0,unpack=True)

# boundary data
shapeid_lns = lines_data[0,:]
x_lns = lines_data[1,:]
y_lns = lines_data[2,:]

# round boundary nodes to three decimals
x_lns = np.around(x_lns,decimals=3)
y_lns = np.around(y_lns,decimals=3)

# need to compute chainage for each line
dist = np.zeros(len(shapeid_lns))
sta = np.zeros(len(shapeid_lns))

for i in range(1, len(shapeid_lns)):
  if (shapeid_lns[i] - shapeid_lns[i-1] < 0.001):
    xdist = x_lns[i] - x_lns[i-1]
    ydist = y_lns[i] - y_lns[i-1]
    dist[i] = np.sqrt(xdist*xdist + ydist*ydist)
    sta[i] = sta[i-1] + dist[i]

# get the unique line ids
unique_lines = np.unique(shapeid_lns)

# find out how many different lines there are
n_lns = len(unique_lines)

# the IKLE array starts at element 1, but matplotlib needs it to start
# at zero
IKLE[:,:] = IKLE[:,:] - 1

# create triangulation object using matplotlib
triang = mtri.Triangulation(x, y, IKLE)

# now we need to find if the result file has these variables:
# DEPTH, VELOCITY U, VELOCITY V

# initialize the indexes to -1
depth_idx = -1
velu_idx = -1
velv_idx = -1

for i in range(len(vnames)):
  if ((vnames[i].find('WATER DEPTH') > -1)): 
    depth_idx = i
  if ((vnames[i].find('VELOCITY U') > -1)): 
    velu_idx = i
  if ((vnames[i].find('VELOCITY V') > -1)): 
    velv_idx = i

if ((depth_idx < 0) or (velu_idx < 0) or (velv_idx < 0) ):
  print('Required variables for computation not found.')
  print('Please include WATER DEPTH, VELOCITY U and VELOCITY V')
  print('in the *.slf input file and try again. Exiting!')
  sys.exit(0)

# the final results variable where the results will be saved
Q = np.zeros( (len(times), n_lns) )

# this is the start of the main loop
for t in range(len(times)):
  
  # print time step to the user
  print('Computing Q at time step index :' + str(t))
  
  # read the snapshot for time t from the *.slf file
  slf.readVariables(t)
  master_results = slf.getVarValues()
  
  # store depths, velu and velv from the input file
  depths = master_results[depth_idx, :]
  velu = master_results[velu_idx, :]
  velv = master_results[velv_idx, :]
  
  # to perform the interpolations at the nodes of the resampled lines
  # for depth, velu, and velv
  interpolator_depths = mtri.LinearTriInterpolator(triang, depths)
  depths_lns = interpolator_depths(x_lns, y_lns)

  interpolator_velu = mtri.LinearTriInterpolator(triang, velu)
  velu_lns = interpolator_velu(x_lns, y_lns)
  
  interpolator_velv = mtri.LinearTriInterpolator(triang, velv)
  velv_lns = interpolator_velv(x_lns, y_lns)
  
  uh = velu_lns[:] * depths_lns[:]
  vh =  velv_lns[:] * depths_lns[:]
  mag = np.sqrt( uh*uh + vh*vh)

  # now go through each line, and integrate
  for j in range(n_lns):
    cursta = list()
    curmag = list()
    for i in range(len(mag)):
      if (abs(unique_lines[j] - shapeid_lns[i]) < 0.01):
        cursta.append(sta[i])
        curmag.append(mag[i])
    Q[t,j] = simps(curmag,cursta)

# prints the final result to the file    
# write the header string
header_str = 'time, '
for i in range(n_lns-1):
  header_str = header_str + str(unique_lines[i]) + ', '
header_str = header_str + str(unique_lines[n_lns-1]) + '\n'  

print('Writing the output file ...')

# create the output file
fout = open(output_file, 'w')

# write the header string
fout.write(header_str)

# write the output file
for t in range(len(times)):
  line = str(times[t]) + ', '
  for j in range(n_lns-1):
    line = line + str(Q[t,j]) + ', '
  line = line + str(Q[t,n_lns-1])
  line = line + '\n'
  fout.write(line)
fout.close()

print('All done!')
