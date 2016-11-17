#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 interp_kd.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Nov 16, 2016
#
# Purpose: Script takes in a tin and a mesh file (both in ADCIRC format), 
# and interpolates the nodes of the mesh file from the tin. This script
# does not use Matplotlib's Triangulation Class as interp.py does. 
# Instead, this script uses a rather less efficient way of searching
# using the KDTree algorithm. The advantage with this method is that
# it can handle invalid TIN's on which Matplotlib's Triangulation Object
# crashes! 
#
# Note: if there are rogue nodes in the TIN (i.e., nodes that are not
# associated with any element), these must be removed from the TIN. 
# MeshLab has a filter that can do this! To do this, convert the invalid
# TIN to *.ply format, apply repair filters in MeshLab, save the 
# modified TIN, then convert it to *.grd format.
#
# PPUTILS now has a way to handle what Matplotlib's Triangulation Class
# calls invalid TIN's.
#
# Uses: Python2.7.9, Matplotlib v1.4.2, Numpy v1.8.2
#
# Example:
#
# python interp_kd.py -t tin.grd -m mesh.grd -o mesh_interp.grd -n 100
# where:
# -t tin surface
# -m mesh (whose nodes are to be interpolated)
# -o interpolated mesh
# -n number of closest neighbours to keep in the KDTree search
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy             as np             # numpy
from scipy import spatial                  # kd tree for searching coords
from scipy import linalg                   # linear algebra package
import matplotlib.path as mplPath          # matplotlib for mplPath
from ppmodules.readMesh import *           # to get all readMesh functions
from ppmodules.utilities import * 
from progressbar import ProgressBar, Bar, Percentage, ETA
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Functions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def minverse(M):
	#{{{
	# convert M into a one-d array for easy referencing
	mm = np.reshape(M,9)
	
	x1 = mm[1]
	y1 = mm[2]
	x2 = mm[4]
	y2 = mm[5]
	x3 = mm[7]
	y3 = mm[8]
	
	twoA = (x2*y3 - x3*y2) - (x1*y3-x3*y1) + (x1*y2 - x2*y1)
	if (twoA < 1.0E-6):
		print('zero area triangle used for interpolation')
	
	minv = np.zeros(9)
	
	minv[0] = (1.0/twoA) * (y2-y3)
	minv[1] = (1.0/twoA) * (y3-y1)
	minv[2]= (1.0/twoA) * (y1-y2)
	
	minv[3] = (1.0/twoA) * (x3-x2)
	minv[4] = (1.0/twoA) * (x1-x3)
	minv[5] = (1.0/twoA) * (x2-x1)
	
	minv[6] = (1.0/twoA) * (x2*y3-x3*y2)
	minv[7] = (1.0/twoA) * (x3*y1-x1*y3)
	minv[8] = (1.0/twoA) * (x1*y2-x2*y1)

	# convert minv to a two-d array
	minv_matrix = np.reshape(minv,(3,3))
	#}}}
	return minv_matrix
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
#
# I/O
if len(sys.argv) != 9 :
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python interp_kd.py -t tin.grd -m mesh.grd -o mesh_interp.grd -n 100')
	sys.exit()

tin_file = sys.argv[2]
mesh_file = sys.argv[4]
output_file = sys.argv[6]
neigh = int(sys.argv[8])

if (neigh < 2):
	print('Number of neighbours must be greater than 1 ... Exiting')
	sys.exit()

# to create the output file
fout = open(output_file,'w')

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
	
# read the adcirc mesh file
print('Reading mesh ...')
m_n,m_e,m_x,m_y,m_z,m_ikle = readAdcirc(mesh_file)

# reset the elevation of the mesh to zero
m_z = np.zeros(m_n)

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
pbar = ProgressBar(widgets=w, maxval=m_n).start()

print('Searching using KDTree ...')
for i in range(m_n): # just do for one node for now
	d,idx = tree.query( (m_x[i],m_y[i]), k = neigh)
	
	# instead of specifying number of neighbours, specify search radius
	#idx = tree.query_ball_point( (m_x[i],m_y[i]), neigh)
	
	# reconstruct a poly out of the tin element for each idx 
	not_found = 0
	for j in range(len(idx)):
		poly = [ (t_x[t_ikle[idx[j],0]], t_y[t_ikle[idx[j],0]]), 
			(t_x[t_ikle[idx[j],1]], t_y[t_ikle[idx[j],1]]),
			(t_x[t_ikle[idx[j],2]], t_y[t_ikle[idx[j],2]])  ]
			
		if (point_in_poly(m_x[i], m_y[i], poly) == 'IN'):
			
			#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
			# construct the FEM interpolation function and interpolate
			ikle_1 = t_ikle[idx[j]]
			x_1 = t_x[ikle_1] 
			y_1 = t_y[ikle_1]
			z_1 = t_z[ikle_1]
			M = np.column_stack((ones,x_1,y_1))
			
			#Minv = linalg.inv(M)
			Minv = minverse(M)
			
			# solve for the parameters
			p_1 = linalg.solve(M,z_1)
			
			# interpolate for z
			m_z[i] = p_1[0] + p_1[1]*m_x[i] + p_1[2]*m_y[i]
			
			if ((m_z[i] < minz) and (m_z[i] > maxz)):
				m_z[i] = -999.0
			#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
			break
		else:
			not_found = not_found + 1
			
		# re-set poly as empty list
		poly = []
	
	if (not_found == len(idx)):
		print('Mesh node ' + str(i+1) + ' not found inside TIN!')
		print('Increase number of neighbours ... Exiting!')
		sys.exit()
		
	# reset not_found count variable	
	not_found = 0
	pbar.update(i+1)
pbar.finish()

# now write the adcirc mesh file
print('Writing results to file ...')
# to create the output file (this is the interpolated mesh)
fout = open(output_file,'w')

# now to write the adcirc mesh file
fout.write('ADCIRC' + '\n')
# writes the number of elements and number of nodes in the header file
fout.write(str(m_e) + ' ' + str(m_n) + '\n')

# writes the nodes
for i in range(0,m_n):
	fout.write(str(i+1) + ' ' + str('{:.3f}'.format(m_x[i])) + ' ' + 
		str('{:.3f}'.format(m_y[i])) + ' ' + str('{:.3f}'.format(m_z[i])) + '\n')
#
# writes the elements
for i in range(0,m_e):
	fout.write(str(i+1) + ' 3 ' + str(m_ikle[i,0]+1) + ' ' + str(m_ikle[i,1]+1) + ' ' + 
		str(m_ikle[i,2]+1) + '\n')

print('All done')	
	

