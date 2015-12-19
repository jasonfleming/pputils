#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 probe.py                              # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
#
# Date: May 20, 2015
#
# Purpose: Probes the selafin file, and outputs file's metadata. 
#
# Using: Python2.7.9, Matplotlib v1.4.2, Numpy v1.8.2
#
# Example: python probe.py -i input.slf
# 
# where:
#       --> -i is the telemac *.slf file being probed
#
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
from os import path
import numpy             as np             # numpy
from ppmodules.selafin_io import *  
#
pytel = os.getcwd()
sys.path.append(path.join(path.dirname(sys.argv[0]),pytel))
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
	print '---------------------------------'
	print '     v     variable_name'
	print '---------------------------------'
	for i in range(len(slf.VARNAMES)):
		print '    ',i, '-->', slf.VARNAMES[i]
	print '#################################'
	
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
	cores = slf.tags["cores"]
	print "number of records in input file : " + str(nrecs)
	print '---------------------------------'
	#print "Available time steps to choose from: "
	
	records = np.arange(len(times))
	#print "Available records to choose from: "
	#print records
	
	if (len(times) < 2):
		print "    t    time (s)"
		print '---------------------------------'
		print str(records[0]) + " -->" + str("{:10.1f}".format(times[0]))
	elif(len(times) < 3):
		print "    t    time (s)"
		print '---------------------------------'
		print str(records[0]) + " -->" + str("{:10.1f}".format(times[0]))
		print str(records[1]) + " -->" + str("{:10.1f}".format(times[1]))
	elif (len(times) < 4):	
		print "    t    time (s)"
		print '---------------------------------'
		print str(records[0]) + " -->" + str("{:10.1f}".format(times[0]))
		print str(records[1]) + " -->" + str("{:10.1f}".format(times[1]))
		print str(records[2]) + " -->" + str("{:10.1f}".format(times[2]))
	else:
		print "t        time (s)"
		print '---------------------------------'
		print str(records[0]) + " -->" + str("{:10.1f}".format(times[0]))
		print str(records[1]) + " -->" + str("{:10.1f}".format(times[1]))
		print str(records[2]) + " -->" + str("{:10.1f}".format(times[2]))
		print str(records[3]) + " -->" + str("{:10.1f}".format(times[3]))
		print '     ......'
		print str(records[nrecs-1]) +"-->" + str("{:10.1f}".format(times[nrecs-1])) 
		print '#################################'
	
	
	#for i in range(len(times)):
	#	print str(cores[i])
	
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
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MAIN
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
if len(sys.argv) != 3:
	print 'Wrong number of Arguments, stopping now...'
	print 'Example usage:'
	print 'python probe.py -i input.slf'
	sys.exit()

# I/O
input_file       = sys.argv[2]   # input *.slf file
print "The input file being probed: " + input_file
#
# Read the header of the selafin result file and get geometry and
# variable names and units
slf,x,y,ikle,numvars,nrecs,times = read_selafin()
variables, units = get_var_names_and_units()

