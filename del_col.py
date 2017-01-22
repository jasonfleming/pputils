#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 del_col.py                           # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Jan 22, 2017
#
# Purpose: Takes in a comma separated *.csv file and deletes the 
# specified column from the file.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python del_col.py -i input.csv -c 0 -o output.csv
#
# where:
#
# -n original input file (comma delimited)
# -c column to crop (column index starts at zero)
# -o output file with the column cropped
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
	print('python del_col.py -i input.csv -c 0 -o output.csv')
	sys.exit()
	
input_file = sys.argv[2]
col = int(sys.argv[4])
output_file = sys.argv[6]

# to create the output file
# fout = open(output_file,'w')

# read input file
input_data = np.loadtxt(input_file, delimiter=',',skiprows=0,unpack=True)

# delete the specified column from the numpy array input_data
# note the indices to be deleted have to be specified as a list 
output_data = np.delete(input_data, [col], axis=0)

# writes the final output (delimited by a comma, three digits after the decimal
np.savetxt(output_file, np.transpose(output_data), fmt='%.3f', delimiter=',')

