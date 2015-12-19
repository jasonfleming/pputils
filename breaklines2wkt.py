#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 breaklines2wkt.py                     # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Sept 25, 2015
#
# Purpose: Takes a pputils 3d breakline and exports it to wkt format. This
# script parallels my breaklines2dxf script. Sometimes for merging breaklines
# it is easier to copy and past lines in a WKT file, than it is to merge via
# GIS or CAD programs.
#
# To create the 3d breakline from xyz and lines.csv, run mkbreakline.py
# 
# Uses: Python2.7.9, Numpy v1.8.2 or later
#
# Example:
#
# python breaklines2wkt.py -l lines3d.csv -o lines3dWKT.csv
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy             as np             # numpy
from ppmodules.ProgressBar import *        # progress bar
curdir = os.getcwd()
#
#
# I/O
if len(sys.argv) == 5 :
	dummy2 =  sys.argv[1]
	lines_file = sys.argv[2]
	dummy3 =  sys.argv[3]
	output_file = sys.argv[4]
else:
	print 'Wrong number of Arguments, stopping now...'
	print 'Usage:'
	print 'python breaklines2wkt.py -l lines3d.csv -o lines3dWKT.csv'
	sys.exit()

# to create the output file
#drawing = dxf.drawing(output_file)
temp_file = "tempWKT.csv"
fout = open(temp_file,"w")

# use numpy to read the file
# each column in the file is a row in data read by np.loadtxt method
lines_data = np.loadtxt(lines_file, delimiter=',',skiprows=0,unpack=True)

# find out if the lines file is id,x,y,z or id,x,y
with open(lines_file, 'r') as f:
	line = next(f) # read 1 line
	n_attr = len(line.split(','))
 
f.close()

if (n_attr == 3):
	shapeid_lns = lines_data[0,:]
	x_lns = lines_data[1,:]
	y_lns = lines_data[2,:]
	z_lns = np.zeros(len(shapeid_lns))
else:
	shapeid_lns = lines_data[0,:]
	x_lns = lines_data[1,:]
	y_lns = lines_data[2,:]
	z_lns = lines_data[3,:]
	
# round lines nodes to three decimals
x_lns = np.around(x_lns,decimals=3)
y_lns = np.around(y_lns,decimals=3)
z_lns = np.around(z_lns,decimals=3)

# finds out how many unique breaklines there are
n_unique_lns = np.unique(shapeid_lns)

# number of nodes in the lines file
n_lns = len(x_lns)

pbar = ProgressBar(maxval=n_lns).start()

# write the header of the WKT file
fout.write(str('WKT,cat' + '\n'))

# number of segments in a linestring
segment_count = 0

for i in range(0,n_lns):
	pbar.update(i+1)
	if (i == 0):
		# write the first linestring
		fout.write(str('"LINESTRING ('))
	
	if (i>0):
		cur_lns_shapeid = shapeid_lns[i]
		prev_lns_shapeid = shapeid_lns[i-1]
		
		if (cur_lns_shapeid - prev_lns_shapeid < 0.001):
		
			# update the segment_count
			segment_count = segment_count + 1
			
			# create tupples for vertexes to add
			v0 = (x_lns[i-1], y_lns[i-1], z_lns[i-1])
			v1 = (x_lns[i], y_lns[i], z_lns[i])
			
			if (segment_count == 1):			
				fout.write(str(x_lns[i-1]) + ' ' + str(y_lns[i-1]) + ' ' + str(z_lns[i-1]) )
				fout.write(',')
				fout.write(str(x_lns[i]) + ' ' + str(y_lns[i]) + ' ' + str(z_lns[i]) )
				fout.write(',')
			else:
				fout.write(str(x_lns[i]) + ' ' + str(y_lns[i]) + ' ' + str(z_lns[i]) )
				fout.write(',')
			
			# this is needed, as the else below is never executed
			# for the last line in the lines file!
			if (i == n_lns-1):
				fout.write(')",' + str(shapeid_lns[i]))
		else:
			# new linestring
			fout.write(')",' + str(shapeid_lns[i]-1))
			fout.write('\n')
			fout.write(str('"LINESTRING ('))
			
			# re-set the segment_count
			segment_count = 0

############################################################################

# closes the temp file
fout.close()

# creates the output file
fout2 = open(output_file,"w")

# each element of this list will be a line of the file read
master = list()

# open the temp file, and replace ',)' with ')'
with open(temp_file, 'r') as f:
	for line in f:
		master.append(line)
		
for i in range(len(master)):
	new = master[i].replace(',)', ')')
	fout2.write(new)
	
# remove the temp file
os.remove(temp_file)

pbar.finish()	

