#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 mkwavescen_wind.py                    # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Aug 2, 2022
#
# Purpose: This script creates the scenarios for the wave transformation
# library. Its inputs are the TOMAWAC base *.cas file, and the combinations
# of scenarios. The script will then write an individual *.cas file for each
# combination, as well as the bash script file to excecute the scenarios. 
#
# This is same as mkwavescen.py, except the scenarios are made by varying
# wind speed and direction only. This is applicable for wind generated
# waves in deep water, where WL variation is not important (i.e., a 
# a large lake, or a deep harbour). 
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python mkwavescen_wind.py -i base.cas -s scenarios.csv
# where:
# -i input TOMAWAC steering file (*.cas) for the base case scenario
# -s scenarios to include in the generation of library *.cas files; it must
# have first row with the following columns: 
# id,uv,vv
# the scenario file must be comma delimited; id column is integer, rest
# are reals (u is wind along x, and v is wind along y, according to the
# cartesian coordinate system --that is what TOMAWAC needs).
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import numpy as np
#
# I/O
if len(sys.argv) == 5:
  base_case = sys.argv[2]
  scenarios_file = sys.argv[4]
else:
  print('Wrong number of arguments ... stopping now ...')
  print('Usage:')
  print('python mkwavescen_wind.py -i base.cas -s scenarios.csv')
  sys.exit()
  
# to open the file that has all of the scenarios
scenarios = np.loadtxt(scenarios_file, delimiter=',', skiprows=1, unpack=True)

# scenario ids as integers
scen_id = scenarios[0,:].astype(int)
u = scenarios[1,:]
v = scenarios[2,:]

n_scen = len(scen_id)

# to create a list of files 
filenames = list()
for i in range(n_scen):
  filenames.append("{:0>5d}".format(scen_id[i]) + ".cas")

# open the base case file, store contents of the base case file in a list
# where each line is a record
master = list();
with open(base_case, "r") as fp:
  for line in fp:
    master.append(line);
    
# to create a list of files
file_out = list()

# initialize the file counter 
x = 0
for item in filenames:
  file_out.append(item)
  file_out[x] = open(item,'w')

  for i in range(len(master)):
    if (str(master[i]).find("2D RESULTS FILE =") == 0):
      file_out[x].write("2D RESULTS FILE " + str('= ') + 
        str("{:0>5d}".format(scen_id[x])) + '.slf' + '\n')

    elif (str(master[i]).find("PUNCTUAL RESULTS FILE =") == 0):
      file_out[x].write("PUNCTUAL RESULTS FILE " + str('= ') + 
        str("{:0>5d}".format(scen_id[x])) + '.spe' + '\n')

    elif (str(master[i]).find("WIND VELOCITY ALONG X =") == 0):
      file_out[x].write("WIND VELOCITY ALONG X " + str('= ') + 
        str(u[x]) + '\n')

    elif (str(master[i]).find("WIND VELOCITY ALONG Y =") == 0):
      file_out[x].write("WIND VELOCITY ALONG Y " + str('= ') + 
      str(v[x]) + '\n')    

    else:
      file_out[x].write(str(master[i]))
  file_out[x].close()
  x = x + 1

# now to create a bash script file that will run all the scenarios
fs = open("run_scenarios.sh", "w")
for item in filenames:
  fs.write("runcode.py tomawac -s --ncsize=6 " + item + "\n")
  fs.write("rm *.sortie" + "\n")
  fs.write("rm *.zip" + "\n")
