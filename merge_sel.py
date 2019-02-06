#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 merge_sel.py                          # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Feb 6, 2019
#
# Purpose: Script takes in two *.slf files, having the same variable
# names (and the same order of variable names), and merges them
# to a single file. 
#
# Uses: Python 2 or 3, Matplotlib, Numpy
#
# Example:
#
# python shift_sel.py -a a.slf -b b.slf -o merged.slf
# where:
# -a first *.slf file
# -b second *.slf file
# -o merged *.slf file
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
from ppmodules.selafin_io_pp import *
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 7 :
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python shift_sel.py -a a.slf -b b.slf -o merged.slf')
  sys.exit()

a_file = sys.argv[2]
b_file = sys.argv[4]
merged_file = sys.argv[6]

# reads the front matter from file a
########################################################################

# reads the a.slf file (first slf file)
a = ppSELAFIN(a_file)
a.readHeader()
a.readTimes()

# get times of the selafin file, and the variable names
a_times = a.getTimes()
a_variables = a.getVarNames()
a_units = a.getVarUnits()
a_float_type,a_float_size = a.getPrecision()

# number of variables
a_NVAR = len(a_variables)

# gets some mesh properties from the *.slf file
a_NELEM, a_NPOIN, a_NDP, a_IKLE, a_IPOBO, a_x, a_y = a.getMesh()

########################################################################

# reads the front matter from file b
########################################################################

# reads the b.slf file (first slf file)
b = ppSELAFIN(b_file)
b.readHeader()
b.readTimes()

# get times of the selafin file, and the variable names
b_times = b.getTimes()
b_variables = b.getVarNames()
b_units = b.getVarUnits()
b_float_type,b_float_size = b.getPrecision()

# number of variables
b_NVAR = len(b_variables)

# gets some mesh properties from the *.slf file
b_NELEM, b_NPOIN, b_NDP, b_IKLE, b_IPOBO, b_x, b_y = b.getMesh()

########################################################################

# now perform some rough checks to ensure the variable names and units
# are identical in both files; note, we assume here that the order of 
# variables is the same for both files; for now this will have to do, 
# but could be relaxed if need be

# check that the number of nodes are the same
if (a_NPOIN != b_NPOIN):
  print('Number of nodes are not the same. Exiting!')
  sys.exit()

# check that the number of elements are the same
if (a_NELEM != b_NELEM):
  print('Number of elements are not the same. Exiting!')
  sys.exit()

# check that the number of variables are the same
if (a_NVAR != b_NVAR):
  print('Number of variables are not the same. Exiting!')
  sys.exit()

# compare the x coordinates
sum_diff_x = sum(a_x - b_x)
if (sum_diff_x > 1.0E-6):
  print('Mismatch in x coordinates are not the same. Exiting!')
  sys.exit()	

# compare the y coordinates
sum_diff_y = sum(a_y - b_y)
if (sum_diff_y > 1.0E-6):
  print('Mismatch in y coordinates are not the same. Exiting!')
  sys.exit()

# stores the matches from list a and list b
match_list = set(a_variables) & set(b_variables)

# for two files to have identical variables, there would have to be the
# number of matches that is the same as the number of variables
if (len(match_list) != a_NVAR):
  print('Variables between two files do not match. Exiting!')
  sys.exit()

# to check the order of the variables
for i in range(a_NVAR):
  if (a_variables[i] != b_variables[i]):
    print('Order of variables do not match. Exiting!')
    sys.exit()

# now we are ready to merge the files
# write the front matter of the output *.slf file
merged = ppSELAFIN(merged_file)
merged.setPrecision(a_float_type, a_float_size)
merged.setTitle('created with pputils')
merged.setVarNames(a_variables)
merged.setVarUnits(a_units)
merged.setIPARAM([1, 0, 0, 0, 0, 0, 0, 0, 0, 1])
merged.setMesh(a_NELEM, a_NPOIN, a_NDP, a_IKLE, a_IPOBO, a_x, a_y)
merged.writeHeader()

# read the results from a, and write it to the merged
for t in range(len(a_times)):
  a.readVariables(t)
  res = a.getVarValues()
  
  merged.writeVariables(a_times[t], res)
  
# read the results from b, and write it to the merged  
for t in range(len(a_times)):
  a.readVariables(t)
  res = a.getVarValues()
  
  merged.writeVariables(a_times[t], res)

a.close()
b.close()
merged.close()

print('All done!')

