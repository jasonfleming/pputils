#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 every_nth.py                          # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Apr 27, 2016
#
# Purpose: Script takes in text file, and retains every nth line. This is
# useful when reducing the number of data points from a large point clound
# data set.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python every_nth.py -i file.txt -n 5 -o file_every_5th.txt

# where:
# -i file.txt some text file
# -o file_every_nth.txt the input file that retains every nth line
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
if len(sys.argv) != 7 :
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python every_nth.py -i file.txt -f 5 -o file_every_5th.txt')
	sys.exit()
dummy1 =  sys.argv[1]
input_file = sys.argv[2]
dummy2 =  sys.argv[3]
f =  int(sys.argv[4])
dummy3 = sys.argv[5]
output_file = sys.argv[6] 

# open the input file
fin = open(input_file, 'r')

# reads all of the lines in the file
master = fin.readlines()

# the output file
fout = open(output_file, 'w')

for i in range(0, len(master), f):
	fout.write(str(master[i]))
