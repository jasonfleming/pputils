#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 flip_col.py                           # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Jan 22, 2017
#
# Purpose: Takes in a comma separated *.csv file, and a column index
# (zero based), and writes that column first, then the rest of the 
# columns in the data set.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python flip_col.py -i input.csv -c 2 -o output.csv
#
# where:
#
# -n original input file (comma delimited)
# -c column to flip as the first column (column index starts at zero)
# -o output file with the selected column moved as the first
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
  print('python flip_col.py -i input.csv -c 0 -o output.csv')
  sys.exit()
  
input_file = sys.argv[2]
col = int(sys.argv[4])
output_file = sys.argv[6]

# read input file
input_data = np.loadtxt(input_file, delimiter=',',skiprows=0,unpack=True)

num_cols = len(input_data[:,0])

first_col = input_data[col,:]

# the remaining columns are these
rest_cols = np.transpose( np.delete(input_data, [col], axis=0))

# stack everything together
output_data = np.column_stack( (first_col, rest_cols))

# writes the final output (delimited by a comma, three digits after the decimal
np.savetxt(output_file, output_data, fmt='%.3f', delimiter=',')

