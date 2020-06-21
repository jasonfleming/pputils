#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 interp1d_profile.py                   # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: May 28, 2019
#
# Purpose: Takes an existing profile in *.csv format (comma delimited 
# x,y), and a spacing, and gives an interpolated profile (also in x,y
# format).
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python interp1d_profile -i beach.csv -s 1.0 -o beach_1m.csv
# where:
#
# -i ==> input profile
# -s ==> spacing along which interpolation is to take place 
# -o ==> output profile 
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy as np                         # numpy
from scipy.interpolate import interp1d     # interp1d
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
  print('python interp1d_profile -i beach.csv -s 1.0 -o beach_1m.csv')
  sys.exit()

input_file = sys.argv[2]
spacing = float(sys.argv[4])
output_file = sys.argv[6]

# read the input
input_data = np.loadtxt(input_file, delimiter=',',skiprows=0,unpack=True)
x = input_data[0,:]
y = input_data[1,:]

f = interp1d(x,y)

# I should fix this
xmin = min(x)
xmax = round(max(x)) - spacing

# to generate the xnew
xnew = xmin
xnew_list = list()
xnew_list.append(xnew)

while xnew < xmax:
  xnew = xnew + spacing
  xnew_list.append(xnew)

n = len(xnew_list)

# convert list to a numpy array
xnew_array = np.asarray(xnew_list)

# carry out the 1d interpolation
ynew = f(xnew_array)

# write the output to a *.csv file
fout = open(output_file, 'w')

for i in range(n):
  fout.write(str(xnew_array[i]) + ',' + str(ynew[i]) + '\n')

print('All done!')

