#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 sections2dxf.py                       # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Jan 6, 2017
#
# Purpose: Takes a pputils lines that has id,x,y,z,sta and writes
# each breakline to a *.dxf file so that it may be visualized in CAD.
# The script will offset each cross section line 100 m away from each
# other in case there are multiple cross section lines in the file.
# 
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python sections2dxf.py -l sections.csv -o sections.dxf
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy             as np             # numpy
from dxfwrite import DXFEngine as dxf      # for dxf export
curdir = os.getcwd()
#
# I/O
if len(sys.argv) == 5 :
	lines_file = sys.argv[2]
	output_file = sys.argv[4]
else:
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python sections2dxf.py -l lines.csv -o lines.dxf')
	sys.exit()

# to create the output file
drawing = dxf.drawing(output_file)

# use numpy to read the file
# each column in the file is a row in data read by np.loadtxt method
lines_data = np.loadtxt(lines_file, delimiter=',',skiprows=0,unpack=True)

shapeid_lns = lines_data[0,:]
shapeid_lns = np.asarray(shapeid_lns, dtype=np.int32)

x_lns = lines_data[1,:]
y_lns = lines_data[2,:]
z_lns = lines_data[3,:]
sta = lines_data[4,:]
	
# round lines nodes to three decimals
x_lns = np.around(x_lns,decimals=3)
y_lns = np.around(y_lns,decimals=3)
z_lns = np.around(z_lns,decimals=3)
sta = np.around(sta,decimals=3)

# number of nodes in the lines file
n_lns = len(x_lns)

# finds out how many unique breaklines there are
n_unique_lns = np.unique(shapeid_lns)

# shift the sta array so that each cross sections is plotted 100 m away from
# each other

# the value to shift the sta variable
sta_shift = 0
sta_shift_list = list()

#for the first line, no station shift
sta_shift_list.append(0)

# calculate the sta_shift for each line in the file
for i in range(n_lns):
	if (shapeid_lns[i] != 0):
		cur_lns_shapeid = shapeid_lns[i]
		prev_lns_shapeid = shapeid_lns[i-1]

		if (cur_lns_shapeid - prev_lns_shapeid > 0.001):
			sta_shift = sta_shift + 100
			sta_shift_list.append(sta_shift)

# modify the sta array according to the shift
new_sta = np.zeros(n_lns)
shapeid_counter = 0

#fout = open('test.txt', 'w')
for i in range(n_lns):
	new_sta[i] = sta[i] + sta_shift_list[shapeid_lns[i]]
	
	#fout.write(str(shapeid_lns[i]) + ',' + str(sta[i]) + ',' + str(new_sta[i]) + '\n')

# write the breaklines
poly = dxf.polyline()

for i in range(0,n_lns):
	if (i>0):
		cur_lns_shapeid = shapeid_lns[i]
		prev_lns_shapeid = shapeid_lns[i-1]
		
		if (cur_lns_shapeid - prev_lns_shapeid < 0.001):
			# create tupples for vertexes to add
			v0 = (new_sta[i-1], z_lns[i-1], 0.0)
			v1 = (new_sta[i], z_lns[i], 0.0)
			poly.add_vertices( [v0, v1] )
			
			# this is needed, as the else below is never executed
			# for the last line in the lines file!
			if (i == n_lns-1):
				drawing.add(poly)
		else:
			drawing.add(poly)
			poly = dxf.polyline()

############################################################################
drawing.save()

