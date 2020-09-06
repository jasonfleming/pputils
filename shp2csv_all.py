#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 shp2csv_all.py                        # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Feb 7, 2019
#
# Purpose: This script takes all *.shp files, and converts each to *.csv.
# I found that I was often running shp2csv.py too many times; this script
# simply automates this task.
#
# Uses: Python 2 or 3
#
# Example:
#
# python shp2csv_all.py
#
# there are no input arguments to this script; it looks for all *.shp
# files, and converts each to *.csv using shp2csv.py script
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys,glob,subprocess
#
curdir = os.getcwd()
#
try:
  # this only works when the paths are sourced!
  pputils_path = os.environ['PPUTILS']
except:
  pputils_path = curdir
  
  # this is to maintain legacy support
  if (sys.version_info > (3, 0)):
    version = 3
    pystr = 'python3'
  elif (sys.version_info > (2, 7)):
    version = 2
    pystr = 'python'
#
# I/O
# gets a listing of all *.shp in the folder, and stores it in a list
shp_list = list()
shp_list = glob.glob('*.shp')

# sort the list
shp_list.sort()

# construct the file names for the output (replace *.shp with *.csv)
csv_list = list()

for i in range(len(shp_list)):
  csv_list.append(shp_list[i].rsplit('.',1)[0] + '.csv')

# now call shp2csv.py for each *.shp file in the list
for i in range(len(shp_list)):
  print('converting ' + shp_list[i])
  try:
    subprocess.call(['shp2csv.py', '-i', shp_list[i], '-o', csv_list[i]])
  except:
    subprocess.call([pystr, 'shp2csv.py', '-i', shp_list[i], '-o', csv_list[i]])
    
  

print('All done!')
