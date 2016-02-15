#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 extract2.py                           # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.

# Date: Feb 15, 2016
#
# Purpose: Script designed to open 2D telemac binary file, read the
# the desired *.slf result variable(s), and simply output it to a text file.
# 
# Works for Python 2 or Python 3 as it uses selafin_io_pp class ppSELAFIN.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
# 
# when extracting 1 variable
# python extract2.py -i input.slf -v 2 -t 23 -o output.xyz
#
# when extracting 2 variables
# python extract2.py -i input.slf -v 2 3 -t 23 -o output.xyz
#
# where:
#       --> -i is the *.slf file from which to extract text data
#
#       --> -v is the index of the variable to extract; when extracting
#                        two variables, the second index is of the second 
#                        variable; see probe.py for index codes
#
#       --> -t is the index of the time step to extract
#
#       --> -o is the text output file
#
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sys
import numpy as np
from ppmodules.selafin_io_pp import *
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MAIN
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
# I/O
if len(sys.argv) == 9:
	# python extract.py -i input.slf -v 2 -t 23 -o output.xyz
	input_file = sys.argv[2]         # input *.slf file
	var1_idx = int(sys.argv[4])      # index of variable 1
	var2_idx = 0                     # variable 2 is nothing here ...
	t = int(sys.argv[6])             # index of time record
	output_file  = sys.argv[8]       # output vector file

elif len(sys.argv) == 10:
	# python extract.py -i input.slf -v 2 3 -t 23 -o output.xyz
	input_file = sys.argv[2]         # input *.slf file
	var1_idx = int(sys.argv[4])      # index of variable 1
	var2_idx = int(sys.argv[5])      # index of variable 2
	t = int(sys.argv[7])             # index of time record
	output_file  = sys.argv[9]       # output vector file
else:
	print('Wrong number of arguments ... stopping now ...')
	print(' ')
	print('For extracting 1 variable try this :')
	print('python extract2.py -i input.slf -v 2 -t 23 -o output.xyz')
	print(' ')
	print('For extracting 2 variable try this :')
	print('python extract2.py -i input.slf -v 2 3 -t 23 -o output.xyz')
	sys.exit()

# create the output file
fout = open(output_file, "w")
#
# Read the header of the selafin result file and get geometry and
# variable names and units

# use selafin_io_pp class ppSELAFIN
slf = ppSELAFIN(input_file)
slf.readHeader()
slf.readTimes()
slf.readVariables(t)

times = slf.getTimes()
vnames = slf.getVarNames()
vunits = slf.getVarUnits()
master_results = slf.getVarValues()
x = slf.getMeshX()
y = slf.getMeshY()

var1 = master_results[var1_idx]
var2 = master_results[var2_idx]

# print('Writing output to text file ...')

if len(sys.argv) == 10:
	fout.write('x, y, ' + vnames[var1_idx] + ', ' + vnames[var2_idx] + '\n')
	for i in range(len(var1)):
		fout.write(str("{:.3f}".format(x[i])) + ", " + str("{:.3f}".format(y[i])) +
			", " + str("{:.3f}".format(var1[i])) + ", " +
			str("{:.3f}".format(var2[i])) + "\n")
elif len(sys.argv) == 9:
		fout.write('x, y, ' + vnames[var1_idx] + '\n')
		for i in range(len(var1)):
			fout.write(str("{:.3f}".format(x[i])) + ", " + str("{:.3f}".format(y[i])) +
				", " + str("{:.3f}".format(var1[i])) + "\n")

# print("All Done!")
