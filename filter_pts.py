#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                           filter_pts.py                               # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Oct 29, 2020
#
# Purpose: The script reads in a points file, reads the values, and 
# retains only values smaller or larger than the threshold value. I am 
# envisioning using this script to filter land elevations from a 
# bathymetric data set.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python filter_pts.py -i in.csv -t 1 -a lt -o out.csv
#
# where:
# -i --> input points file
# -t --> threshold value 
# -a --> action, can be either gt (greater than) or lt (less than)
# -o --> output points file
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy             as np             # numpy

#
if len(sys.argv) == 9 :
  input_file = sys.argv[2]
  threshold = float(sys.argv[4])
  action = sys.argv[6]
  output_file = sys.argv[8]
else:
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python filter_pts.py -i in.csv -t 1 -a gt -o out.csv')
  sys.exit()
  
if ( (action != 'lt') and (action != 'gt') ):
  print('Action can only be gt or lt. Exiting.')
  sys.exit()

# to read the input data using numpy
input_data = np.loadtxt(input_file, delimiter=',',skiprows=0,unpack=True)

fout = open(output_file, 'w')

# poly coords
x = input_data[0,:]
y = input_data[1,:]
z = input_data[2,:]

# number of points
n = len(x)

for i in range(n):
  if (action == 'lt'):
    if (z[i] < threshold):
      fout.write(str(x[i]) + ',' + str(y[i]) + ',' + str(z[i]) + '\n')
  elif (action == 'gt'):
    if (z[i] > threshold):
      fout.write(str(x[i]) + ',' + str(y[i]) + ',' + str(z[i]) + '\n')
  else:
    print('Wrong action. Try again!')

fout.close()
