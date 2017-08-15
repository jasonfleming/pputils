#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 mkwavelibts_at_node.py                # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Aug 14, 2017
#
# This script is similar to mkwavelibts.py, but instead of writing the
# data as the *.slf file, it writes the result from the wave library
# at a specified output node only. After running the mkwavelibfile.py
# (and after producing the wave library file), extract the library
# dictionary file at the desired nearshore node using extract_pt.py. Then
# use the offshore time series, and two library dictionary files (one
# for offshore, and one for nearshore), to reconstruct a time series
# at the desired nearshore node (the one that was used in extract_pt.py).
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python mkwavelibts.py -t offshore_time_seris.csv -o offshore_dict_file.csv
#   -n nearshore_dict_file.csv -r MASTER_output.csv
# where:
# -t is the time series *.csv (comma delimited, first record as header)
#    with the following headings: yyyy,mm,dd,hh,minute,t2d_time,wl,hm0,tp,wdir
#
# -o is the wave library dictionary file for the offshore data;
#    The file is (*.csv, comma delimited), with the following headings:
#    id,water_level,wave_dir,wave_height,wave_period
#
# -n is the wave library dictionary file for the nearshore data (i.e., one
#    that was extracted from the wave library file using extract_pt.py;
#    The file is (*.csv, comma delimited), with the following headings:
#    id,water_level,wave_dir,wave_height,wave_period
#
# -r is the MASTER output file that has the time series reconstructed
#    using the wave library
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import random
import numpy as np
#from scipy import spatial
#from ppmodules.selafin_io_pp import *
from progressbar import ProgressBar, Bar, Percentage, ETA
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# I/O
if len(sys.argv) == 9:
  offshore_ts_file = sys.argv[2]
  o_lib_dict_file = sys.argv[4]
  n_lib_dict_file = sys.argv[6]
  output_file = sys.argv[8]
else:
  print('Wrong number of arguments ... stopping now ...')
  print('Usage:')
  print('python mkwavelibts.py -t offshore_time_seris.csv -o offshore_dict_file.csv')
  print('   -n nearshore_dict_file.csv -r MASTER_output.csv')
  sys.exit()

# read the *.csv data first
offshore_ts_data = np.loadtxt(offshore_ts_file, delimiter=',', skiprows=1, unpack=True)

# yyyy,mm,dd,hh,minute,t2d_time,wl,hm0,tp,wdir
yyyy = offshore_ts_data[0,:].astype(int)
mm = offshore_ts_data[1,:].astype(int)
dd = offshore_ts_data[2,:].astype(int)
hh = offshore_ts_data[3,:].astype(int)
minute = offshore_ts_data[4,:].astype(int)
t2d_time = offshore_ts_data[5,:].astype(int)
wl = offshore_ts_data[6,:]
hm0 = offshore_ts_data[7,:]
tp = offshore_ts_data[8,:]
wdir = offshore_ts_data[9,:]

# reads the offshore dictionary keys file
o_lib_dict_data = np.loadtxt(o_lib_dict_file, delimiter=',', skiprows=1, unpack=True)

# id,water_level,wave_dir,wave_height,wave_period
o_lib_id = o_lib_dict_data[0,:].astype(int)
o_lib_wl = o_lib_dict_data[1,:]
o_lib_wdir = o_lib_dict_data[2,:]
o_lib_hm0 = o_lib_dict_data[3,:]
o_lib_tp = o_lib_dict_data[4,:]

# reads the n dictionary keys file
n_lib_dict_data = np.loadtxt(n_lib_dict_file, delimiter=',', skiprows=1, unpack=True)

# id,water_level,wave_dir,wave_height,wave_period
n_lib_id = n_lib_dict_data[0,:].astype(int)
n_lib_wl = n_lib_dict_data[1,:]
n_lib_wdir = n_lib_dict_data[2,:]
n_lib_hm0 = n_lib_dict_data[3,:]
n_lib_tp = n_lib_dict_data[4,:]

# this is the master output file
fout = open(output_file,'w')

# now we have to use the data from the *.csv files to extract from the 
# master wave library file a record that corresponds to each time step in
# the offshore time series file

# number of time steps in the offshore data
num_ts_points = len(yyyy)

# distance array
dist = np.zeros(num_ts_points)

# record to extract for a particular time step
rec = 0

# output file that tells us which lib case was selected for each time
# step in the final output
header_str = 'yyyy,mm,dd,hh,minute,t2d_time,wl,hm0,tp,wdir,'
header_str = header_str + 'o_lib_id,o_lib_wl,o_lib_hm0,o_lib_tp,o_lib_wdir,'
header_str = header_str + 'n_lib_id,n_lib_wl,n_lib_hm0,n_lib_tp,n_lib_wdir'

fout.write(header_str + '\n')

# widget for the progress bar
w = [Percentage(), Bar(), ETA()]
pbar = ProgressBar(widgets=w, maxval=num_ts_points).start()

for i in range(num_ts_points):
  if ( (wl[i] < -900) or (hm0[i] < 0) or (tp[i] < 0) or (wdir[i] < 0) ):
    print('Time series input data is invalid. Exiting.')
    sys.exit()
  else:
    # compute a straight out euclidian distance 
    dist = np.sqrt( (o_lib_wl - wl[i])**2 + 
      (o_lib_wdir - wdir[i])**2 + (o_lib_hm0 - hm0[i])**2 +
      (o_lib_tp - tp[i])**2  )
    # this is the record in the master library file that correspons  
    # to the time step i
    # rec is the index of the minimum dist
    rec = np.argmin(dist)
      
    # write the offshore time series output to a *.csv file
    # this is what we can use to judge if the discretization is valid
    fout.write(str(yyyy[i]) + ',' + str(mm[i]) + ',' + str(dd[i]) + ',' +
      str(hh[i]) + ',' + str(minute[i]) + ',' + str(t2d_time[i]) + ',' +
      str(wl[i]) + ',' + str(hm0[i]) + ',' + str(tp[i]) + ',' + 
      str(wdir[i]) + ',' + str(o_lib_id[rec]) + ',' + str(o_lib_wl[rec]) + ',' + 
      str(o_lib_hm0[rec]) + ',' +str(o_lib_tp[rec]) + ',' + str(o_lib_wdir[rec]) + ',' +
      str(n_lib_id[rec]) + ',' + str(n_lib_wl[rec]) + ',' + 
      str(n_lib_hm0[rec]) + ',' +str(n_lib_tp[rec]) + ',' + str(n_lib_wdir[rec]) + '\n')
    
    pbar.update(i+1)
    
# finish the progress bar
pbar.finish()






