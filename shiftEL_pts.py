#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 shiftEL_pts.py                        # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: May 4, 2021
# Purpose: Takes in a pts file, and shifts the elevation values by the
# amount specified.
#
# Uses: Python 2 or 3, Matplotlib, Numpy, Scipy
#
# Example:
#
# python shiftEL_pts.py -n points.csv -s 0.3 -o points_shifted.csv
# where:
# -n original xyz file (comma delimited)
# -s shift amount (can be negative)
# -o output points file (comma delimited)
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import numpy as np
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# I/O
if len(sys.argv) != 7 :
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python shiftEL_pts.py -n points.csv -s 0.3 -o points_shifted.csv')
  sys.exit()
  
input_file = sys.argv[2]
shift = float(sys.argv[4])
output_file = sys.argv[6]

# to create the output file
fout = open(output_file,"w")

# read input file
input_data = np.loadtxt(input_file, delimiter=',',skiprows=0,unpack=True)

# master nodes in the file (from the nodes file)
x = input_data[0,:]
y = input_data[1,:]
z = input_data[2,:]
n = len(x)

# shift the z value
z = z + shift

# crop all the points to three decimals only
x = np.around(x,decimals=3)
y = np.around(y,decimals=3)
z = np.around(z,decimals=3)

for j in range(n):
  fout.write( str(x[j]) + ',' + str(y[j]) + ',' + str(z[j]) + '\n')

print('All done!')


