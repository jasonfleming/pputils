#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 interpBreakline_kd.py                 # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Nov 19, 2016
#
# Purpose: Script takes in a tin (in ADCIRC format), and a pputils lines 
# file (shapeid,x,y), and interpolates z values from tin. When extracting
# cross sections, the lines file should be resampled at a large number 
# of nodes (say 100), or at specific features in order to get a properly
# extracted cross section for hydraulic modeling. This version of the 
# script works for TINs that Matplotlib will think are invalid (i.e., 
# ones that have zero area elements). Much of the code parallels my
# interp_kd.py script. This script is much less efficient than the
# interp.py script, but it can handle TINs with zero area elements.
#
# This script can not handle breakline nodes that lie outside of the TIN.
# The logic used is identical to that used in interp_kd.py script.
#
# Uses: Python 2 or 3, Numpy, Scipy
#
# Example:
#
# python interpBreakline.py -t tin.grd -l lines.csv -o lines_z.csv -n 100
# where:
# -t tin surface
# -l resampled cross section lines file (in pputils format, shapeid,x,y)
# -o cross section lines file (shapeid,x,y,z,sta)
# -n number of nearest search nodes
#
# the script also outputs an additional *.csv file in hec-ras format
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy             as np             # numpy
from scipy import spatial                  # kd tree for searching coords
from scipy import linalg                   # linear algebra package
from ppmodules.readMesh import *           # to get all readMesh functions
from ppmodules.utilities import *
from progressbar import ProgressBar, Bar, Percentage, ETA
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
# I/O
if len(sys.argv) != 9 :
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python interpBreakline.py -t tin.grd -l lines.csv -o lines_z.csv -n 100')
	sys.exit()

tin_file = sys.argv[2]
lines_file = sys.argv[4]
output_file = sys.argv[6] 
neigh = int(sys.argv[8])

if (neigh < 2):
	print('Number of neighbours must be greater than 1 ... Exiting')
	sys.exit()

# read the adcirc tin file
print('Reading TIN ...')
t_n,t_e,t_x,t_y,t_z,t_ikle = readAdcirc(tin_file)

# used for error checking
minz = np.amin(t_z)
maxz = np.amax(t_z)

# compute centroids of each tin element
centroid_x = np.zeros(t_e)
centroid_y = np.zeros(t_e)

for i in range(t_e):
	centroid_x[i] = (t_x[t_ikle[i,0]] +t_x[t_ikle[i,1]] + \
		t_x[t_ikle[i,2]]) / 3.0  
	centroid_y[i] = (t_y[t_ikle[i,0]] +t_y[t_ikle[i,1]] + \
		t_y[t_ikle[i,2]]) / 3.0

# read the lines file
lines_data = np.loadtxt(lines_file, delimiter=',',skiprows=0,unpack=True)
shapeid = lines_data[0,:]
#shapeid = shapeid.astype(np.int32)
x = lines_data[1,:]
y = lines_data[2,:]

# number of items in the lines file
n = len(x)

# create the new output variables
z = np.zeros(n)
sta = np.zeros(n)
tempid = np.zeros(n)
dist = np.zeros(n)
		
# construct the KDTree from the centroid nodes
print('Constructing KDTree object from centroid nodes ...')
source = np.column_stack((centroid_x,centroid_y))
tree = spatial.KDTree(source)

# used for FEM shape function
ones = np.ones(3)

# the list that stores the triangle polygon for a particular TIN element
poly = list()

# for the progress bar
w = [Percentage(), Bar(), ETA()]
pbar = ProgressBar(widgets=w, maxval=n).start()

print('Searching using KDTree ...')
for i in range(len(x)): # just do for one node for now
	d,idx = tree.query( (x[i],y[i]), k = neigh)
	
	# instead of specifying number of neighbours, specify search radius
	#idx = tree.query_ball_point( (m_x[i],m_y[i]), neigh)
	
	# reconstruct a poly out of the tin element for each idx 
	not_found = 0
	for j in range(len(idx)):
		poly = [ (t_x[t_ikle[idx[j],0]], t_y[t_ikle[idx[j],0]]), 
			(t_x[t_ikle[idx[j],1]], t_y[t_ikle[idx[j],1]]),
			(t_x[t_ikle[idx[j],2]], t_y[t_ikle[idx[j],2]])  ]
			
		if (point_in_poly(x[i], y[i], poly) == 'IN'):
			
			#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
			# construct the FEM interpolation function and interpolate
			ikle_1 = t_ikle[idx[j]]
			x_1 = t_x[ikle_1] 
			y_1 = t_y[ikle_1]
			z_1 = t_z[ikle_1]
			M = np.column_stack((ones,x_1,y_1))
			
			#Minv = linalg.inv(M)
			#Minv = minverse(M)
			
			# solve for the parameters
			p_1 = linalg.solve(M,z_1)
			
			# interpolate for z
			z[i] = p_1[0] + p_1[1]*x[i] + p_1[2]*y[i]
			
			if ((z[i] < minz) and (z[i] > maxz)):
				z[i] = -999.0
			#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
			break
		else:
			not_found = not_found + 1
			
		# re-set poly as empty list
		poly = []
	
	if (not_found == len(idx)):
		print('Breakline node at line ' + str(i+1) + ' not found inside TIN!')
		print('Increase number of neighbours ... Exiting!')
		sys.exit()
		
	# reset not_found count variable	
	not_found = 0
	pbar.update(i+1)
pbar.finish()

# to create the output file
fout = open(output_file,"w")

# to create the sta array
sta[0] = 0.0
tempid = shapeid
dist[0] = 0.0

for i in range(1,n):
	if (tempid[i] - shapeid[i-1] < 0.001):
		xdist = x[i] - x[i-1]
		ydist = y[i] - y[i-1]
		dist[i] = np.sqrt(np.power(xdist,2.0) + np.power(ydist,2.0))
		sta[i] = sta[i-1] + dist[i]

# to round the numpy arrays to three decimal spaces
x = np.around(x,decimals=3)
y = np.around(y,decimals=3)
z = np.around(z,decimals=3)
dist = np.around(dist,decimals=3)
sta = np.around(sta,decimals=3)

# now to write the output lines file (with xs information)
for i in range(n):
	fout.write(str(shapeid[i]) + ',' + str(x[i]) + ',' + 
		str(y[i]) + ',' + str(z[i]) + ',' +	str(sta[i]) + '\n')

# create an alternate output csv file that is used by hec-ras
output_file2 = output_file.rsplit('.',1)[0] + '_hec-ras.csv'

# opens the alternate output file
f2 = open(output_file2,'w')

# writes the header lines
f2.write('River,Reach,RS,X,Y,Z' + '\n')
for i in range(n):
	f2.write('river_name,reach_name,' + str(shapeid[i]) + ','+
		str(x[i]) + ',' + str(y[i]) + ',' + str(z[i]) + '\n')

print('All done!')
