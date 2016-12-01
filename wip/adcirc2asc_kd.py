#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 adcirc2asc_kd.py                      # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Nov 30, 2016
#
# Purpose: Script takes in a tin in ADCIRC format, and generates an 
# ESRI *.asc file for easy visualization by a GIS. This version of the
# script works for valid and invalid TINs; it also takes in a boundary
# as the input parameter (rather than generating the grid for the entire
# TIN boundary). This script is not efficient, but it works for creating
# grids from invalid TINs. The script uses the entire TIN in its search
# space, even though only the elements bound within the polygon would do.
# TODO: fix this inefficiency! I AM NOT HAPPY WITH THE EXECUTION TIMES
# OF THIS SCRIPT, BUT IT DOES WORK. IT COULD BE USEFUL FOR INVALID TINS.
# BUT, IT WILL JUST BE EASIER TO CLEAN THE INPUT TOPOLOGY RATHER THAN
# DEALING WITH INVALID TINS. I AM PUTTING THIS SCRIPT UNDER THE WORK IN
# PROGRESS DIRECTORY FOR NOW.
#
# Uses: Python 2 or 3, Matplotlib, Numpy
#
# Example:
#
# python adcirc2asc_kd.py -i tin.grd -b boundary.csv -s 10 -n 1000 -o tin.asc
# where:
# -i input adcirc mesh file
# -b boundary file in pputils format
# -s spacing (in m) of the *.asc grid file
# -o generated *.asc grid file
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy             as np             # numpy
import matplotlib.path as mplPath          # matplotlib path object
from ppmodules.readMesh import *           # to get all readMesh functions
from ppmodules.utilities import *          # to get point_in_poly
from scipy import spatial                  # kd tree for searching coords
from scipy import linalg                   # linear algebra package
from progressbar import ProgressBar, Bar, Percentage, ETA
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 11 :
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python adcirc2asc_kd.py -i tin.grd -b boundary.csv -s 10 -n 1000 -o tin.asc')
	sys.exit()
	
adcirc_file = sys.argv[2]
boundary_file = sys.argv[4]
spacing = sys.argv[6]
spacing = float(spacing)
neigh = int(sys.argv[8]) # num of neighbours to search
output_file = sys.argv[10] # output *.asc grid

if (neigh < 2):
	print('Number of neighbours must be greater than 1 ... Exiting')
	sys.exit()

# to create the output file
fout = open(output_file,'w')

# read the adcirc file
print('Reading TIN ...')
n,e,x,y,z,ikle = readAdcirc(adcirc_file)

# read polygon file
poly_data = np.loadtxt(boundary_file, delimiter=',',skiprows=0,unpack=True)

# polygon data
shapeid_poly = poly_data[0,:]
x_poly = poly_data[1,:]
y_poly = poly_data[2,:]

# crop all the polygon points to three decimals only
x_poly = np.around(x_poly,decimals=3)
y_poly = np.around(y_poly,decimals=3)

# get the unique polygon ids
polygon_ids = np.unique(shapeid_poly)

# find out how many different polygons there are
n_polygons = len(polygon_ids)

if (n_polygons > 1):
	print('Number of polygons in input file greater than 1. Exiting.')
	sys.exit()
	
# construct a polygon as mpl object
poly = list()
for i in range(len(shapeid_poly)):
	poly.append( (x_poly[i], y_poly[i]) )
	
# convert poly list to a numpy array
poly_array = np.asarray(poly)

# create a mathplotlib path object
path = mplPath.Path(poly_array)

# determine the spacing of the regular grid
range_in_x = x_poly.max() - x_poly.min()
range_in_y = y_poly.max() - y_poly.min()

max_range = max(range_in_x, range_in_y)

# first index is integer divider, second is remainder
num_x_pts = divmod(range_in_x, spacing)
num_y_pts = divmod(range_in_y, spacing)

print("Size of output matrix is : " + str(int(num_x_pts[0])) + " x " + str(int(num_y_pts[0])))
print("Grid resolution is : " + str(spacing) + " m")

# creates the regular grid
print('Creating the grid ...')
xreg, yreg = np.meshgrid(np.linspace(x_poly.min(), x_poly.max(), int(num_x_pts[0])),
	np.linspace(y_poly.min(), y_poly.max(), int(num_y_pts[0])))
x_regs = xreg[1,:]
y_regs = yreg[:,1]

# to make the gridded 2d points arrays into 1d arrays (i.e., unravel the
# 2d points into 1d grids
x_grid_pts = np.ravel(xreg)
y_grid_pts = np.ravel(yreg)

# for now, the z array is zero
z_grid_pts = np.zeros(len(x_grid_pts))
z_grid_pts_nan = np.zeros(len(x_grid_pts), dtype=bool)

# loop through each point of the unraveled arrays, and assign a NaN to
# one that lies outside of the boundary
for i in range(len(x_grid_pts)):
	poly_test = path.contains_point( (x_grid_pts[i], y_grid_pts[i]) )
	if (poly_test == False):
		z_grid_pts[i] = -999.00
		z_grid_pts_nan[i] = True

# now we need to interpolate the x_grid_pts, y_grid_pts from the TIN

# compute centroids of each tin element
centroid_x = np.zeros(e)
centroid_y = np.zeros(e)

for i in range(e):
	centroid_x[i] = (x[ikle[i,0]] +x[ikle[i,1]] + \
		x[ikle[i,2]]) / 3.0  
	centroid_y[i] = (y[ikle[i,0]] +y[ikle[i,1]] + \
		y[ikle[i,2]]) / 3.0

# construct the KDTree from the centroid nodes
# the inefficiency here is that the entire TIN is used for the KDTree
# search space; need somehow to restrict the search space and not use
# the elements of the entire TIN
# TODO: only use TIN elements that are in the boundary polygon

print('Constructing KDTree object from centroid nodes ...')
source = np.column_stack((centroid_x,centroid_y))
tree = spatial.cKDTree(source)

# used for FEM shape function
ones = np.ones(3)

# the list that stores the triangle polygon for a particular TIN element
poly = list()

# for the progress bar
w = [Percentage(), Bar(), ETA()]
pbar = ProgressBar(widgets=w, maxval=len(x_grid_pts)).start()

print('Searching using KDTree ...')
for i in range(len(x_grid_pts)): 
	if (z_grid_pts_nan[i] == False): 
		d,idx = tree.query( (x_grid_pts[i],y_grid_pts[i]), k = neigh)
	
		# instead of specifying number of neighbours, specify search radius
		#idx = tree.query_ball_point( (m_x[i],m_y[i]), neigh)
	
		# reconstruct a poly out of the tin element for each idx 
		not_found = 0
		for j in range(len(idx)):
			
			# find the area of each triangle in the search space
			x1 = x[ikle[idx[j],0]]
			y1 = y[ikle[idx[j],0]]
			x2 = x[ikle[idx[j],1]]
			y2 = y[ikle[idx[j],1]]
			x3 = x[ikle[idx[j],2]]
			y3 = y[ikle[idx[j],2]]
			
			twoA = twoA = (x2*y3 - x3*y2) - (x1*y3-x3*y1) + (x1*y2 - x2*y1)
			A = twoA / 2.0
			
			if (abs(A) < 1.0E-6):
				A = 1.0E-6	
			
			poly = [(x1, y1), (x2, y2), (x3, y3)]
				
			if (point_in_poly(x_grid_pts[i],y_grid_pts[i], poly) == 'IN'):
				
				#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
				# construct the FEM interpolation function and interpolate
				ikle_1 = ikle[idx[j]]
				x_1 = x[ikle_1] 
				y_1 = y[ikle_1]
				z_1 = z[ikle_1]
				M = np.column_stack((ones,x_1,y_1))
				
				# solve for the parameters
				p_1 = linalg.solve(M,z_1)
				
				# interpolate for z
				z_grid_pts[i] = p_1[0] + p_1[1]*x_grid_pts[i] + p_1[2]*y_grid_pts[i]
				
				#if ((z[i] < minz) or (z[i] > maxz)):
				#	z[i] = -999.0
				#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
				break
			else:
				not_found = not_found + 1
				
			# re-set poly as empty list
			poly = []
		
		if (not_found == len(idx)):
			print('Grid node at ' + str(x_grid_pts[i]) + ', ' + str(y_grid_pts[i]))
			print(' not found. Increase number of neighbours ... Exiting!')
			sys.exit()
			
		# reset not_found count variable	
		not_found = 0
	pbar.update(i+1)
pbar.finish()

# this writes the grid to *.asc file format
#######################################################################
# to reshape z into a 2d array
# xreg.shape gives a tupple of the array size (numx,numy)
z_grid_pts = np.reshape(z_grid_pts, xreg.shape)

# write the header string
header_str = "NCOLS " + str(z_grid_pts.shape[1]) + "\n"
header_str = header_str + "NROWS " + str(z_grid_pts.shape[0]) + "\n"
header_str = header_str + "XLLCORNER " + str(x_regs[0]) + "\n"
header_str = header_str + "YLLCORNER " + str(y_regs[0]) + "\n"
header_str = header_str + "CELLSIZE " + str(spacing) + "\n"
header_str = header_str + "NODATA_VALUE " + str(-999.00)

#np.savetxt("temp.out", z, fmt='%.2f', delimiter='') # this has no max spaces
np.savetxt(output_file, np.flipud(z_grid_pts), fmt='%10.3f', header = header_str, 
	comments = '', delimiter='') # this has 10 char spaces, 3 after decimal
#######################################################################

print("All done!")
