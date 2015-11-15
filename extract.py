#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 extract.py                            # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.

# Date: May 20, 2015
#
# Purpose: Script designed to open 2D telemac binary file, read the
# the desired *.slf result variable(s), and simply output it to a text file.
# 
# Using: Python2.7.9, Matplotlib v1.4.2, Numpy v1.8.2
#
# Example:
# 
# when extracting 1 variable
# python extract.py -i input.slf -v 2 -t 23 -o output.xyz
#
# when extracting 2 variables
# python extract.py -i input.slf -v 2 3 -t 23 -o output.xyz
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
import os,sys                              # system parameters
from os import path
import matplotlib.tri    as mtri           # matplotlib triangulations
import numpy             as np             # numpy
from numpy import linspace, dtype          # Writing netcdf files
import math # for the ceil function
#from math import sqrt, pi, sin, cos, tan, atan2 as arctan2  # math objects for coord trans
# Importing pytel tools for SELAFIN parser
pytel = os.getcwd()
#pytel = '/home/user/opentelemac/v7p0r1/scripts/python27/'
sys.path.append(path.join(path.dirname(sys.argv[0]),pytel))
from parsers.parserSELAFIN import SELAFIN  
#
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def read_selafin():
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	# Openning the selafin file
	# This gives the name of the variables, and their index number
	#
	slf = SELAFIN(input_file)
	# Getting coordinates
	x       = slf.MESHX
	y       = slf.MESHY
	# Getting Variables
	print 'Variables in '+input_file+' are:'
	for i in range(len(slf.VARNAMES)):
		print '    ',i, '-->', slf.VARNAMES[i]
	
	#for i,name in enumerate(slf.VARNAMES):
	#	print '    ',i, ' - ',name
	# Get IKLE for mesh regularization
	ikle     = np.array(slf.IKLE2)
	
	# total number of variables in the input file
	numvars = len(slf.VARNAMES)
	
	# total number of time records in the file 
	nrecs = len(slf.tags["times"])
	
	# an array of size nrecs with values of time steps in the input file
	times = slf.tags["times"]
	print "number of records in input file : " + str(nrecs)
	#print "Available time steps to choose from: "
	#for i in range(len(times)):
	#	print str(times[i])
	
	#
	return slf,x,y,ikle,numvars,nrecs,times
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# End of the Function
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def get_var_names_and_units():
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	# two empty lists
	variables = []
	units = []
	for var_names in slf.VARNAMES[0:numvars]:
		#print var_names
		variables.append(var_names)
	for unit_names in slf.VARUNITS[0:numvars]:
		units.append(unit_names)
	return variables, units
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# End of the Function
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
#
def get_values(t):
	VARIABLES = {} # do this as dictionary
	for i, n in enumerate(slf.VARNAMES[0:len(variables)]):
		#print "Reading ", n, " for time index ",t
		values = slf.getVALUES(t)
		VARIABLES[i] = values[i]
	return VARIABLES
	
def read_all_variables(t):
	var_out = [] # do this as a list
	# i is the counter, n is the item
	for i, n in enumerate(slf.VARNAMES[0:len(variables)]):
		#print "Reading ", n, " for time index ",t
		values = slf.getVALUES(t)
		var_out.append(values[i])
	return var_out
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# End of the Function
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#

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
	print 'Wrong number of arguments ... stopping now ...'
	print ' '
	print 'For extracting 1 variable try this :'
	print 'python extract.py -i input.slf -v 2 -t 23 -o output.xyz'
	print ' '
	print 'For extracting 2 variable try this :'
	print 'python extract.py -i input.slf -v 2 3 -t 23 -o output.xyz'
	sys.exit()

# create the output file
fout = open(output_file, "w")
#
# Read the header of the selafin result file and get geometry and
# variable names and units
slf,x,y,ikle,numvars,nrecs,times = read_selafin()
variables, units = get_var_names_and_units()

# reads all variables for time desired (in the case below, it is t=0)
master_results = read_all_variables(t)

var1 = master_results[var1_idx]
var2 = master_results[var2_idx]

print 'Writing output to text file ...'

if len(sys.argv) == 10:
	for i in range(len(var1)):
		fout.write(str("{:.3f}".format(x[i])) + ", " + str("{:.3f}".format(y[i])) +
			", " + str("{:.3f}".format(var1[i])) + ", " +
			str("{:.3f}".format(var2[i])) + "\n")
elif len(sys.argv) == 9:
		for i in range(len(var1)):
			fout.write(str("{:.3f}".format(x[i])) + ", " + str("{:.3f}".format(y[i])) +
				", " + str("{:.3f}".format(var1[i])) + "\n")

print "Done"
