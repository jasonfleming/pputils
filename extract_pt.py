#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 extract_pt.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: May 2, 2016
#
# Purpose: Script takes in a *.slf file, and x,y node coordinates, and
# extracts all values for that node, for all time steps in the file. Works
# equally well for *.slf 2d and 3d files.
#
# Revised: Jun 21, 2016
# Added a method in selafin_io_pp.py that significantly improves the 
# speed of data extraction at a single point.
#
# Revised: Jul 18, 2016
# Changed the formatting of the output data (i.e., made the output 
# variables have 12 digits after the decimal point). Added the coordinate
# location to the output file.
#
# Revised: Nov 21, 2016
# Changed KDTree to cKDTree to improve performance.
#
# Revised: Sep 26, 2017
# Changed the definition of x2d and y2d to make sure the index is an 
# integer. This was changed in the latest numpy release.
#
# Revised: Dec 5, 2017
# Changed how parsing is done in formatting for the 3d ascii output.
#
# Revised: Oct 24, 2020
# Deleted the first three lines from the output that were used to output
# metadata; added the date and time to the time series output. The code
# for 3d files had to be adjusted, so that output remained the same as
# before.
#
# Uses: Python 2 or 3, Matplotlib, Numpy
#
# Example:
#
# python extract_pt.py -i in.slf -x 100.0 -y 200.0 -o out.txt
# where:
# -i input *.slf file
# -x, y coordinates of the node for which to extract data
# -o output text file
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
from scipy import spatial
import numpy as np
from datetime import datetime, date, time, timedelta
from ppmodules.selafin_io_pp import *
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 9 :
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python extract_pt.py -i in.slf -x 100.0 -y 200.0 -o out.txt')
  sys.exit()

input_file = sys.argv[2]
xu = float(sys.argv[4])
yu = float(sys.argv[6])
output_file = sys.argv[8]

# the output file
fout = open(output_file, 'w')

# reads the *.slf file
slf = ppSELAFIN(input_file)
slf.readHeader()
slf.readTimes()

# get times of the selafin file, and the variable names
times = slf.getTimes()
variables = slf.getVarNames()
units = slf.getVarUnits()

# get the start date from the result file 
# this is a numpy array of [yyyy mm dd hh mm ss]
date = slf.getDATE()
year = date[0]
month = date[1]
day = date[2]
hour = date[3]
minute = date[4]
second = date[5]

# use the date info from the above array to construct a python datetime
# object, in order to display day/time
try:
  pydate = datetime(year, month, day, hour, minute, second)
except:
  print('Date in file invalid. Printing default date in output file.')
  pydate = datetime(1997, 8, 29, 2, 15, 0)

# this is the time step in seconds, as read from the file
# assumes the time steps are regular
if (len(times) > 1):
  pydelta = times[1] - times[0]
else:
  pydelta = 0.0

# number of variables
NVAR = len(variables)

# to remove duplicate spaces from variables and units
for i in range(NVAR):
  variables[i] = ' '.join(variables[i].split())
  units[i] = ' '.join(units[i].split())

# gets some of the mesh properties from the *.slf file
NELEM, NPOIN, NDP, IKLE, IPOBO, x, y = slf.getMesh()

# determine if the *.slf file is 2d or 3d by reading how many planes it has
NPLAN = slf.getNPLAN()
#fout.write('The file has ' + str(NPLAN) + ' planes' + '\n')

# store just the x and y coords
x2d = x[0:int(len(x)/NPLAN)]
y2d = y[0:int(len(x)/NPLAN)]

# create a KDTree object
source = np.column_stack((x2d,y2d))
tree = spatial.cKDTree(source)

# find the index of the node the user is seeking
d, idx = tree.query((xu,yu), k = 1)

# print the node location to the output file
#fout.write('Extraction performed at: ' + str(x[idx]) + ' ' + str(y[idx]) + '\n')
#fout.write('Note this is the closest node to the input coordinate!' + '\n')

# now we need this index for all planes
idx_all = np.zeros(NPLAN,dtype=np.int32)

# the first plane
idx_all[0] = idx

# start at second plane and go to the end
for i in range(1,NPLAN,1):
  idx_all[i] = idx_all[i-1] + (NPOIN / NPLAN)

# now we are ready to output the results
# to write the header of the output file
fout.write('DATE, TIME, ')
for i in range(NVAR):
  fout.write(variables[i] + ', ')
fout.write('\n')

fout.write('-, S, ')
for i in range(NVAR):
  fout.write(units[i] + ', ')
fout.write('\n')

########################################################################
# extract results for every plane (if there are multiple planes that is)
for p in range(NPLAN):
  slf.readVariablesAtNode(idx_all[p])
  results = slf.getVarValuesAtNode()
  
  # outputs the results 'd %b %Y %H:%M'
  for i in range(len(times)):
    fout.write(str(pydate.strftime('%Y-%m-%d %H:%M') + ', '))
    fout.write(str("{:.3f}").format(times[i]) + ', ')
    
    # now we need to increment the pydate by the pydelta
    pydate = pydate + timedelta(seconds=pydelta)
    
    for j in range(NVAR):
      fout.write(str("{:.12f}").format(results[i][j]) + ', ')
    fout.write('\n')
########################################################################

# close the output file
fout.close()

# below is what I had previously
# it has a more logical output for 3d files
# if wanting to rely on previous, uncomment between ### and replace with
# code below; if using the code below, also uncomment everything after
# if NPLAN > 1

'''
###############################################################################
# read the results for all variables, for all times
for t in range(len(times)):
  # read variable
  slf.readVariables(t)
  
  # these are the results for all variables, for time step count
  master_results = slf.getVarValues() 
  
  # to store the extracted results in an array of its own
  extracted_results = np.zeros((NVAR,NPLAN))
  
  for i in range(NVAR):
    for j in range(len(idx_all)):
      extracted_results[i][j] = master_results[i][idx_all[j]]
  
  # transpose the extracted_results 
  extracted_results_tr = np.transpose(extracted_results)
  
  
  for i in range(NPLAN):
    fout.write(str("{:.3f}").format(times[t]) + ', ')
    for j in range(NVAR):
      fout.write(str("{:.4f}").format(extracted_results_tr[i][j]) + ', ')
    fout.write('\n')
###############################################################################
'''

# the code below is simply to format the output for 3d *.slf files to make it
# more human readable 

if NPLAN > 1:
  fout2 = open('temp.txt','w')

  master = list() # data as read from the file
  master2 = list() # the one with the trailing comma removed, and headers removed
  
  # use python to read the results file
  # first three lines are headers
  
  header_str = ''
  count = 0
  
  with open(output_file, 'r') as f1:
    for i in f1:
      ls = i.split(',')[1:]
      str2 = ','.join(ls) # join the list into a string, with a comma separator
      
      master.append(str2)
      # first two lines are the header string
      if (count < 2):
        header_str = header_str + master[count]
      count = count + 1

  # remove the output file
  os.remove(output_file)

  for i in range(len(master)):
    #if i > 0:
    master2.append(master[i].rsplit(',',1)[0])
      
  for i in range(len(master2)):
    fout2.write(master2[i] + '\n')
  
  # close the temp file  
  fout2.close()

  # use numpy to read the temp file
  temp_data = np.loadtxt('temp.txt', delimiter=',',skiprows=2,unpack=True)
  
  temp_data_tr = np.transpose(temp_data)
  
  # now use np.lexsort to sort the data by columns
  elev_col = temp_data_tr[:,1]
  time_col = temp_data_tr[:,0]
  
  ind = np.lexsort( (elev_col, time_col))
  
  temp_data_sorted = temp_data_tr[ind,:]
  
  # now write the final output file
  np.savetxt(output_file, temp_data_sorted, fmt='%10.12f', header = header_str, 
    comments = '', delimiter=',')

  # remove the temp file
  os.remove('temp.txt')

