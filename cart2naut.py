#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 cart2naut.py                          # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Apr 27, 2016
#
# Purpose: Script takes in a (x,y,u,v) cartesian file, and converts it to
# nautical direction convention producing (x,y,mag,dir). The file producing
# (x,y,u,v) is obtained from extract.py script that extracts velocity data
# from a telemac file.
#
# The nautical convention is one where directions are referenced CW from N. 
# For example, dir 0 in naut convention implies the current is approaching 
# from the north; dir 90 in naut convention means the current is approaching
# from the east; and so on.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python cart2naut.py -i cart.txt -o naut.txt
# where:
# -i input (x,y,u,v) cartesion *.txt file, with 1st line as header
# -o output (x,y,mag,dir) nautical *.txt file, with 1st line as header
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
curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 5 :
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python cart2naut.py -i cart.txt -o naut.txt')
	sys.exit()
dummy1 =  sys.argv[1]
input_file = sys.argv[2]
dummy2 =  sys.argv[3]
output_file = sys.argv[4] 

# converts cartesian vector quantities to nautical direction convention
def toNautical(u,v):
	mag = np.sqrt(u**2 + v**2)
	
	# quadrants are defined as follows
	# IV  | I
	# ---------
	# III | II
	
	# error checking
	if (abs(v) < 1.0E-6):
		v = 1.0E-6
	if (abs(u) < 1.0E-6):
		u = 1.0E-6
		
	# compute the cartesian angle
	theta_cart = np.arctan(abs(v)/abs(u)) * 360.0 / (2.0 * np.pi)
	
	# quadrant I
	if (u >= 0.0 and v >= 0.0):
		theta_naut = 270.0 - theta_cart 
	# quadrant II
	elif (u > 0.0 and v < 0.0):
		theta_naut = 270.0 + theta_cart
	# quadrant III
	elif (u < 0.0 and v < 0.0):
		theta_naut = 90.0 - theta_cart
	# quadrant IV
	elif (u < 0.0 and v > 0.0):
		theta_naut = 90.0 + theta_cart
	else:
		theta_naut = 0.0
	
	dir = theta_naut
	
	return mag,dir

# load file
input_file = np.loadtxt(input_file, delimiter=',',skiprows=1,unpack=True)

x = input_file[0,:]
y = input_file[1,:]

u = input_file[2,:]
v = input_file[3,:]

n = len(x)

# open file
fout = open(output_file, 'w')

# write header
fout.write('x,y,mag,dir' + '\n')

# return vector mag and dir, and write to file
for i in range(n):
	mag,dir = toNautical(u[i],v[i])
	fout.write(str(x[i]) + ', ' + str(y[i]) + ', '+ str(mag) + ', ' + 
		str(dir) + '\n')

