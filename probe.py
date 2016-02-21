#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 probe.py                              # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
#
# Date: Feb 13, 2016
#
# Purpose: Probes the selafin file, and outputs file's metadata. Works for
# Python 2 or Python 3 as it uses selafin_io_pp class ppSELAFIN.
#
# Uses: Python 2 or 3, Numpy
#
# Example: python probe2.py -i input.slf
# 
# where:
#       --> -i is the telemac *.slf file being probed
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from __future__ import absolute_import, division, print_function
import sys
import numpy as np             
from ppmodules.selafin_io_pp import *

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MAIN
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
if len(sys.argv) != 3:
	print('Wrong number of Arguments, stopping now...')
	print('Example usage:')
	print('python probe2.py -i input.slf')
	sys.exit()

# I/O
input_file = sys.argv[2]   # input *.slf file
print("The input file being probed: " + input_file)
#
# constructor for pp_SELAFIN class
slf = ppSELAFIN(input_file)
slf.readHeader()
slf.readTimes()

times = slf.getTimes()
vnames = slf.getVarNames()
vunits = slf.getVarUnits()

# prints variable names
print('#################################')
print('Variables in '+input_file+' are: ')
print('---------------------------------')
print('     v     variable_name'         )
print('---------------------------------')
for i in range(len(vnames)):
	print('    ',i, '-->', vnames[i])
print('#################################')

# prints times

records = np.arange(len(times))
nrecs = len(times)

if (len(times) < 2):
	print("    t    time (s)")
	print('---------------------------------')
	print(str(records[0]) + " -->" + str("{:10.1f}".format(times[0])))
elif(len(times) < 3):
	print("    t    time (s)")
	print('---------------------------------')
	print(str(records[0]) + " -->" + str("{:10.1f}".format(times[0])))
	print(str(records[1]) + " -->" + str("{:10.1f}".format(times[1])))
elif (len(times) < 4):	
	print("    t    time (s)")
	print('---------------------------------')
	print(str(records[0]) + " -->" + str("{:10.1f}".format(times[0])))
	print(str(records[1]) + " -->" + str("{:10.1f}".format(times[1])))
	print(str(records[2]) + " -->" + str("{:10.1f}".format(times[2])))
else:
	print("t        time (s)")
	print('---------------------------------')
	print(str(records[0]) + " -->" + str("{:10.1f}".format(times[0])))
	print(str(records[1]) + " -->" + str("{:10.1f}".format(times[1])))
	print(str(records[2]) + " -->" + str("{:10.1f}".format(times[2])))
	print(str(records[3]) + " -->" + str("{:10.1f}".format(times[3])))
	print('     ......')
	print(str(records[nrecs-1]) +"-->" + str("{:10.1f}".format(times[nrecs-1])))
	
print('#################################')


