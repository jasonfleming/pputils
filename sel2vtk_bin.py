#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 sel2vtk_bin.py                        # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng. 
# 
# Date: Apr 16, 2017
#
# Purpose: Same as the sel2vtk.py, except that it writes binary *.vtk
# files. It writes a double precision Paraview binary file regardless
# of the precision of the input *.slf file.
#
# Using: Python 2 or 3, Matplotlib, Numpy
#
# Example: python sel2vtk_bin.py -i results.slf -o results.vtk
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import numpy as np
from ppmodules.selafin_io_pp import *

if len(sys.argv) == 5:
  input_file = sys.argv[2]
  output_file = sys.argv[4]
  t_start = 0
  t_end = 0
elif len(sys.argv) == 9:
  input_file = sys.argv[2]
  output_file = sys.argv[4]
  t_start = int(sys.argv[6])
  t_end = int(sys.argv[8])  
else:
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python sel2vtk_bin.py -i results.slf -o results.vtk')
  print('or')
  print('python sel2vtk_bin.py -i results.slf -o results.vtk -t_start 0 -t_end 5')
  sys.exit()
  
# we are going to have one file per time record in the slf file
# use selafin_io_pp class ppSELAFIN
slf = ppSELAFIN(input_file)
slf.readHeader()
slf.readTimes()

# get times of the selafin file, and the variable names
times = slf.getTimes()
variables = slf.getVarNames()

# update the index of t_end
# len(times) gives total number of items in the array
# len(times) - 1 is the index of the last element
if len(sys.argv) == 5:
  t_end = len(times)-1

# gets some of the mesh properties from the *.slf file
NELEM, NPOIN, NDP, IKLE, IPOBO, x, y = slf.getMesh()

# to remove duplicate spaces from variables
for i in range(len(variables)):
  variables[i] = ' '.join(variables[i].split())

# determine if the *.slf file is 2d or 3d by reading how many planes it has
NPLAN = slf.getNPLAN()

# verify that variable ELEVATION or COTE are in the *.slf file 
if (NPLAN > 1):
  el_idx = -1
  for i in range(len(variables)):
    if ((variables[i].find('ELEVATION') > -1)): 
      el_idx = i
    elif ((variables[i].find('COTE Z') > -1)):
      el_idx = i
  if (el_idx < 0):
    print('Variable \'ELEVATION Z\' or \'COTE Z\' not in file')
    sys.exit()

# the IKLE array starts at element 1, but matplotlib needs it to start
# at zero
IKLE[:,:] = IKLE[:,:] - 1

# to accomodate code pasting
ikle = IKLE

# to create a list of files
file_out = list()

# list of time indices in *.slf file
idx_times = np.arange(len(times))

# initialize the index list of time steps to extract
idx_list = list()

# create a list of filenames based on time records in the slf file
filenames = list()
for i in range(t_start, t_end+1, 1):
  filenames.append(output_file.split('.',1)[0] + "{:0>5d}".format(i) + '.vtk')
  idx_list.append(i)

# to check if the idx_list is within times list
if (idx_list[0] not in idx_times):
  print('Starting time specified not in *.slf file. Exiting.')
  sys.exit()
elif (idx_list[-1] not in idx_times):
  print('Ending time specified not in *.slf file. Exiting.')
  sys.exit()

# to create the multiple output files
for count, item in enumerate(filenames):
  print('Writting file: ' + item)
  file_out.append(item)
  file_out[count] = open(item,'wb')
  
  # item is the actual file name, which corresponds to each time step
  slf.readVariables(idx_list[count])
  
  # these are the results for all variables, for time step count
  master_results = slf.getVarValues() 

  file_out[count].write(pack('>26s', '# vtk DataFile Version 2.0'.encode()))
  file_out[count].write(pack('>c', b'\n'))
  file_out[count].write(pack('>20s', 'Created with PPUTILS'.encode()))
  file_out[count].write(pack('>c', b'\n'))
  file_out[count].write(pack('>6s', 'BINARY'.encode()))
  file_out[count].write(pack('>c', b'\n'))
  file_out[count].write(pack('>25s', 'DATASET UNSTRUCTURED_GRID'.encode()))
  file_out[count].write(pack('>c', b'\n'))

  # re-construct the points string
  pts_str = 'POINTS ' + str(len(x)) + ' double'
  pts_fmt = '>' + str(len(pts_str)) + 's'
  
  # write the points string
  file_out[count].write(pack(pts_fmt, pts_str.encode()))
  file_out[count].write(pack('>c', b'\n'))
  
  # now write the x y z points
  for i in range(len(x)):
    if (NPLAN > 1):
      file_out[count].write(pack('>d', x[i]))
      file_out[count].write(pack('>d', y[i]))
      file_out[count].write(pack('>d', master_results[el_idx][i]))
    else:
      file_out[count].write(pack('>d', x[i]))
      file_out[count].write(pack('>d', y[i]))
      file_out[count].write(pack('>d', 0.0))
      
  # empty line  
  file_out[count].write(pack('>c', b'\n'))
  
  # re-construct the cells string
  if (NPLAN > 1):
    cells_str = 'CELLS ' + str(len(ikle)) + ' ' + str(len(ikle)*7)
    cells_fmt = '>' + str(len(cells_str)) + 's'
  else:    
    cells_str = 'CELLS ' + str(len(ikle)) + ' ' + str(len(ikle)*4)
    cells_fmt = '>' + str(len(cells_str)) + 's'
  
  # write the cells string
  file_out[count].write(pack(cells_fmt, cells_str.encode()))
  file_out[count].write(pack('>c', b'\n'))

  # now write the ikle array
  for i in range(len(ikle)):
    if (NPLAN > 1):
      file_out[count].write(pack('>i', 6))
      file_out[count].write(pack('>i', ikle[i,0]))
      file_out[count].write(pack('>i', ikle[i,1]))  
      file_out[count].write(pack('>i', ikle[i,2]))
      file_out[count].write(pack('>i', ikle[i,3]))
      file_out[count].write(pack('>i', ikle[i,4]))
      file_out[count].write(pack('>i', ikle[i,5]))
    else:
      file_out[count].write(pack('>i', 3))
      file_out[count].write(pack('>i', ikle[i,0]))
      file_out[count].write(pack('>i', ikle[i,1]))  
      file_out[count].write(pack('>i', ikle[i,2]))
      
  # empty line  
  file_out[count].write(pack('>c', b'\n'))

  # re-construct the cell_types string
  cell_types_str = 'CELL_TYPES ' + str(len(ikle))
  cell_types_fmt = '>' + str(len(cell_types_str)) + 's'

  # write the cell_types string
  file_out[count].write(pack(cell_types_fmt, cell_types_str.encode()))
  file_out[count].write(pack('>c', b'\n'))
  
  # now write the cell_types
  for i in range(len(ikle)):
    if (NPLAN > 1):
      file_out[count].write(pack('>i', 13 ))
    else:
      file_out[count].write(pack('>i', 5 ))

  # empty line  
  file_out[count].write(pack('>c', b'\n'))

  # write the point data string
  point_data_str = 'POINT_DATA ' + str(len(x))
  point_data_fmt = '>' + str(len(point_data_str)) + 's'

  # write the point_data string
  file_out[count].write(pack(point_data_fmt, point_data_str.encode()))
  file_out[count].write(pack('>c', b'\n'))
  
  # these are the indices of the variable names to search
  idx_written = list()
  idx_vel_u = -1000
  idx_vel_v = -1000
  idx_vel_z = -1000
  
  # for tomawac
  idx_mean_dir = -1000
  idx_wave_height = -1000
  
  # for artemis
  idx_art_wave_inc = -1000
  idx_art_wave_height = -1000

  # from the list of variables, find v and u
  for i in range(len(variables)):
    if (NPLAN > 1):
      if (variables[i].find('VELOCITY U') > -1):
        idx_vel_u = i
      elif (variables[i].find('VELOCITY V') > -1):
        idx_vel_v = i
      elif (variables[i].find('VELOCITY W') > -1):
        idx_vel_z = i
    else:
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
    
    # in case the variables are in french
  for i in range(len(variables)):
    if (NPLAN > 1):
      if (variables[i].find('VITESSE U') > -1):
        idx_vel_u = i
      elif (variables[i].find('VITESSE V') > -1):
        idx_vel_v = i
      elif (variables[i].find('VITESSE W') > -1):
        idx_vel_z = i
    else:
      if (variables[i].find('VITESSE U') > -1):
        idx_vel_u = i
      elif (variables[i].find('VITESSE V') > -1):
        idx_vel_v = i
      elif (variables[i].find('DIRECTION MOY') > -1):
        idx_mean_dir = i
      elif (variables[i].find('HAUTEUR HM0') > -1):
        idx_wave_height = i
      
  if ( (idx_vel_u > -1000) and (idx_vel_v > -1000) ):
    # write velocity vectors data

    # write the vector data string
    vector_data_str = 'VECTORS Velocity double'
    vector_data_fmt = '>' + str(len(vector_data_str)) + 's'
    
    # write the point_data string
    file_out[count].write(pack(vector_data_fmt, vector_data_str.encode()))
    file_out[count].write(pack('>c', b'\n'))
    
    for i in range(len(x)):
      if (NPLAN > 1):
        file_out[count].write(pack('>d',master_results[idx_vel_u][i]))
        file_out[count].write(pack('>d',master_results[idx_vel_v][i]))
        file_out[count].write(pack('>d',master_results[idx_vel_z][i]))
      else:
        file_out[count].write(pack('>d',master_results[idx_vel_u][i]))
        file_out[count].write(pack('>d',master_results[idx_vel_v][i]))
        file_out[count].write(pack('>d',0.0))

    # empty line    
    file_out[count].write(pack('>c', b'\n'))
        
  if ( (idx_mean_dir > -1000) and (idx_wave_height > -1000) ):
    # write wave height vectors data
    
    # write the vector data string
    vector_data_str = 'VECTORS Wavedir double'
    vector_data_fmt = '>' + str(len(vector_data_str)) + 's'
    
    # write the point_data string
    file_out[count].write(pack(vector_data_fmt, vector_data_str.encode()))
    file_out[count].write(pack('>c', b'\n'))
    
    for i in range(len(x)):
      wave_x = np.sin(master_results[idx_mean_dir][i] * np.pi / 180.0) * master_results[idx_wave_height][i]
      wave_y = np.cos(master_results[idx_mean_dir][i] * np.pi / 180.0) * master_results[idx_wave_height][i]

      file_out[count].write(pack('>d',wave_x))
      file_out[count].write(pack('>d',wave_y))
      file_out[count].write(pack('>d',0.0))
    
    # empty line    
    file_out[count].write(pack('>c', b'\n'))
    
  if ( (idx_art_wave_height > -1000) and (idx_art_wave_inc > -1000) ):
    # write wave height vectors data
    vector_data_str = 'VECTORS Wavedir double'
    vector_data_fmt = '>' + str(len(vector_data_str)) + 's'
    
    # write the point_data string
    file_out[count].write(pack(vector_data_fmt, vector_data_str.encode()))
    file_out[count].write(pack('>c', b'\n'))
    
    for i in range(len(x)):
      wave_x = np.cos(master_results[idx_art_wave_inc][i] * np.pi / 180.0) * master_results[idx_art_wave_height][i]
      wave_y = np.sin(master_results[idx_art_wave_inc][i] * np.pi / 180.0) * master_results[idx_art_wave_height][i]

      file_out[count].write(pack('>d',wave_x))
      file_out[count].write(pack('>d',wave_y))
      file_out[count].write(pack('>d',0.0))
    
    # empty line    
    file_out[count].write(pack('>c', b'\n'))
         
  # write the rest of the variables
  for i in range(len(variables)):
    scalar_data_str = 'SCALARS ' + variables[i].replace(' ', '_')
    scalar_data_fmt = '>' + str(len(scalar_data_str)) + 's'
    
    # write the point_data string
    file_out[count].write(pack(scalar_data_fmt, scalar_data_str.encode()))
    file_out[count].write(pack('>c', b'\n'))

    # write the double string
    file_out[count].write(pack('>6s', 'double'.encode()))
    file_out[count].write(pack('>c', b'\n'))

    file_out[count].write(pack('>20s', 'LOOKUP_TABLE default'.encode()))
    file_out[count].write(pack('>c', b'\n'))

    # write the data
    for j in range(len(x)):
      file_out[count].write(pack('>d',master_results[i][j]))
  
  file_out[count].close()
  
print('All done!')

