#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 adcirc2asc.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: March 12, 2017
#
# Purpose: Script takes in a ESRI *.asc file and generates a comma
# delimited *.csv file. 
#
# Revised: September 28, 2021
# Added a progress bar to monitor write progress.
# 
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python asc2csv.py -i grid.asc -o grid.csv
# where:
# -i input *.asc file
# -o output comma separated *.csv file
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy             as np             # numpy
from progressbar import ProgressBar, Bar, Percentage, ETA
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
curdir = os.getcwd()
#
# I/O
if (len(sys.argv) != 5):
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python asc2csv.py -i grid.asc -o grid.csv')
  sys.exit()

asc_file = sys.argv[2]
csv_file = sys.argv[4]

# input file
fin = open(asc_file, 'r')

# to create the output file
fout = open(csv_file,'w')

# reads the header information from the *.asc file
NCOLS = int(fin.readline().split()[1])
NROWS = int(fin.readline().split()[1])
XLLCORNER = float(fin.readline().split()[1])
YLLCORNER = float(fin.readline().split()[1])
CELLSIZE = float(fin.readline().split()[1])
NODATA_VALUE = float(fin.readline().split()[1])

# close the file
fin.close()

# ignore the first 6 header lines, and read the *.asc grid using numpy
grid_data = np.loadtxt(asc_file, skiprows=6,unpack=True)

# re-construct the x and y coordinates from header information
n = NCOLS * NROWS

x = np.zeros(n)
y = np.zeros(n)
z = np.zeros(n)

# stores the grid data into a 1d array
count = 0
for i in range(NROWS):
  for j in range(NCOLS):
    z[count] = grid_data[j,i]
    count = count + 1

# re-create the xy coordinates from the header data
# (this was done through trial and error)

count = 0
x_start = XLLCORNER + (CELLSIZE / 2.0)
y_start = YLLCORNER + NROWS * CELLSIZE - (CELLSIZE / 2.0)

for i in range(NROWS):
  for j in range(NCOLS):
    x[count] = x_start + j * CELLSIZE
    y[count] = y_start - i * CELLSIZE
    
    count = count + 1

# write the header    
#fout.write('x,y,z' + '\n')

print('writing data file ...')
w = [Percentage(), Bar(), ETA()]
pbar = ProgressBar(widgets=w, maxval=n).start()
    
# only retain non-missing values
for i in range(n):
  
  if (not(z[i] - NODATA_VALUE) < 0.001):
    fout.write(str('{:.3f}'.format(x[i])) + ',' + str('{:.3f}'.format(y[i]))
      + ',' + str('{:.3f}'.format(z[i])) + '\n')
  pbar.update(i+1)
pbar.finish()
    
print("All done!")
