#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 mkwavelibts.py                        # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Jun 17, 2016
#
# Purpose: This script takes the master wave library file, offshore time
# series *.csv file and the library dictionary file (that says what each
# record in the master wave library file is), and it creates a *.slf
# result file for each time step of the time series data. Essentially, the
# script finds the record in the master wave library file that most closely
# corresponds to the time series data, and creates a *.slf file for each
# time step in the offshore time series. The resulting *.slf file is then
# to be used by prosou.f and condim_sisyphe.f subroutines to feed a
# Telemac2D/Sisyphe coupled model with wave library data.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python mkwavelibts.py -i master_wave_lib.slf -t offshore_time_seris.csv
#   -k library_dictionary_file.csv -o wave_lib_ts.slf
# where:
# -i is the master wave library file (each record is a scenario)
#
# -t is the time series *.csv (comma delimited, first record as header)
#    with the following headings: yyyy,mm,dd,hh,minute,t2d_time,wl,hm0,tp,wdir
#
# -k is the wave library dictionary file (*.csv, comma delimited), with
#    the following headings: id,water_level,wave_dir,wave_height,wave_period
#    this file is a metadata for master the wave library file (i.e., it
#    tells us which condition each record corresponds to
#
# -o is the output *.slf file created from the master library file 
#    corresponding to each time step in the time series file.
#
# Note this script has no input parameters; it uses python's glob function
# to get a list of all *.slf files in the present directory.
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import numpy as np
from ppmodules.selafin_io_pp import *
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# I/O
if len(sys.argv) == 9:
	master_lib_file = sys.argv[2]
	offshore_ts_file = sys.argv[4]
	lib_dict_file = sys.argv[6]
	output_file = sys.argv[8]
else:
	print('Wrong number of arguments ... stopping now ...')
	print('Usage:')
	print('python mkwavelibts.py -i wave_lib.slf -t offshore_ts.csv')
	print('     -k lib_dict.csv -o wave_lib_ts.slf')
	sys.exit()

# prints the data files that were read
print(master_lib_file)
print(offshore_ts_file)
print(lib_dict_file)
print(output_file)

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

# reads the dictionary keys file
lib_dict_data = np.loadtxt(lib_dict_file, delimiter=',', skiprows=1, unpack=True)

# id,water_level,wave_dir,wave_height,wave_period
lib_id = lib_dict_data[0,:].astype(int)
lib_wl = lib_dict_data[1,:]
lib_wdir = lib_dict_data[2,:]
lib_hm0 = lib_dict_data[3,:]
lib_tp = lib_dict_data[4,:]

# now we have to use the data from the *.csv files to extract from the 
# master wave library file a record that corresponds to each time step in
# the offshore time series file

# I did this in my SWAN wave library files ...

num_ts_points = len(yyyy)
dist = np.zeros(num_ts_points)
rec = 0

fout = open('wave_lib_temp_output.csv','w')
header_str = 'yyyy,mm,dd,hh,minute,t2d_time,wl,hm0,tp,wdir,'
header_str = header_str + 'lib_id,lib_wl,lib_hm0,lib_tp,lib_wdir'

fout.write(header_str + '\n')

for i in range(num_ts_points):
	if ( (wl[i] < -900) or (hm0[i] < -900) or (tp[i] < -999) or (wdir[i] < 0) ):
		print('Time series input data is invalid. Exiting.')
		sys.exit()
	else:
		# compute a straight out euclidian distance 
		dist = np.sqrt( (lib_wl - wl[i])**2 + 
			(lib_wdir - wdir[i])**2 + (lib_hm0 - hm0[i])**2 +
			(lib_tp - tp[i])**2  )
		# this is the record in the master library file that correspons	
		# to the time step i
		rec = np.argmin(dist)
		
		# write temporary output to a text file
		fout.write(str(yyyy[i]) + ',' + str(mm[i]) + ',' + str(dd[i]) + ',' +
			str(hh[i]) + ',' + str(minute[i]) + ',' + str(t2d_time[i]) + ',' +
			str(wl[i]) + ',' + str(hm0[i]) + ',' + str(tp[i]) + ',' + 
			str(wdir[i]) + ',' + str(lib_id[rec]) + ',' + str(lib_wl[rec]) + ',' + 
			str(lib_hm0[rec]) + ',' +str(lib_tp[rec]) + ',' + str(lib_wdir[rec]) + '\n')
		







