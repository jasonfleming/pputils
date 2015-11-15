#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 adcirc2asc2.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Aug 29, 2015
#
# Purpose: Script takes in a tin in ADCIRC format, and generates an ESRI *.asc 
# file for easy visualization by a GIS.
#
# Uses brute force to locate which grid point lies in which element, which 
# leads to impractical execution times. DO NOT USE!
#
# Uses: Python2.7.9, Matplotlib v1.4.2, Numpy v1.8.2
#
# Example:
#
# python adcirc2asc.py -i tin.14 -s 10 -o tin.asc
# where:
# -i input adcirc mesh file
# -s spacing (in m) of the *.asc grid file
# -o generated *.asc grid file
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import matplotlib.tri    as mtri           # matplotlib triangulations
import numpy             as np             # numpy
from scipy import linalg
import matplotlib.path as mplPath
from utils.progressbar import ProgressBar  # progress bar
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Functions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def read_adcirc(adcirc_file):
	#{{{
	# define lists
	x = list()
	y = list()
	z = list()
	e1 = list()
	e2 = list()
	e3 = list()
	
	# each line in the file is a list object
	line = list()
	with open(adcirc_file, "r") as f1:
		for i in f1:
			line.append(i)
		
	# to write to a temp file nodes and 2d elements only
	#temp_nodes_file ="temp_nodes.csv"
	#temp_elements_file ="temp_elements.csv"
	
	#fout_nodes = open(temp_nodes_file,"w")
	#fout_elements = open(temp_elements_file,"w")
	
	# read how elements and nodes from second line of adcirc file (line(2)
	ele_nod_str = line[1]
	ele_nod_list = ele_nod_str.split() 
	e = ele_nod_list[0]
	e = int(e)
	n = ele_nod_list[1]
	n = int(n)
	
	node_str = str("")
	# write the temp nodes file
	for i in range(2,n+2):
		#fout_nodes.write(line[i])
		node_str = line[i]
		node_str_list = node_str.split()
		x.append(node_str_list[1])
		y.append(node_str_list[2])
		z.append(node_str_list[3])
		
	
	# write the temp elements file
	for i in range(n+2,n+2+e):
		#fout_elements.write(line[i])
		ele_str = line[i]
		ele_str_list = ele_str.split()
		e1.append(ele_str_list[2])
		e2.append(ele_str_list[3])
		e3.append(ele_str_list[4])
		
	# turn these into numpy arrays
	xx = np.zeros(n)
	yy = np.zeros(n)
	zz = np.zeros(n)
	e11 = np.zeros(e)
	e22 = np.zeros(e)
	e33 = np.zeros(e)
	
	for i in range(0,n):
		xx[i] = x[i]
		yy[i] = y[i]
		zz[i] = z[i]
		
	# -1 to change index of elements; min node number now starts at zero
	
	# matplotlib triangulation requires node numbering to start at zero,
	# whereas my adcirc node numbering start at 1
	for i in range(0,e):
		e11[i] = int(e1[i])-1
		e22[i] = int(e2[i])-1
		e33[i] = int(e3[i])-1
		
	# stack the elements
	ikle = np.column_stack((e11,e22,e33))  
	
	ikle = ikle.astype(np.int32)
	
	#print ikle.shape
	#print ikle.dtype
	
	#print xx.shape
	#print xx.dtype
	#}}}
	return n,e,xx,yy,zz,ikle
#
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
curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 7 :
	print 'Wrong number of Arguments, stopping now...'
	print 'Usage:'
	print 'python adcirc2asc.py -i tin.14 -s 10 -o tin.asc'
	sys.exit()
dummy1 =  sys.argv[1]
adcirc_file = sys.argv[2]
dummy2 =  sys.argv[3]
spacing = sys.argv[4]
spacing = float(spacing)
dummy3 =  sys.argv[5]
output_file = sys.argv[6] # output *.asc grid

# to create the output file
fout = open(output_file,"w")

# read the adcirc file
n,e,x,y,z,ikle = read_adcirc(adcirc_file)

# find max and min of z from the tin
minz = np.amin(z)
maxz = np.amax(z)

# determine the spacing of the regular grid
range_in_x = x.max() - x.min()
range_in_y = y.max() - y.min()

max_range = max(range_in_x, range_in_y)

# first index is integer divider, second is remainder
num_x_pts = divmod(range_in_x, spacing)
num_y_pts = divmod(range_in_y, spacing)

print "Size of output matrix is : " + str(int(num_x_pts[0])) + " x " + str(int(num_y_pts[0]))
print "Grid resolution is : " + str(spacing) + " m"

# creates the regular grid
xreg, yreg = np.meshgrid(np.linspace(x.min(), x.max(), int(num_x_pts[0])),
	np.linspace(y.min(), y.max(), int(num_y_pts[0])))
x_regs = xreg[1,:]
y_regs = yreg[:,1]

# create 1d arrays using numpy reshape function
xx = np.reshape(xreg, xreg.shape[0] * xreg.shape[1])
yy = np.reshape(yreg, yreg.shape[0] * yreg.shape[1])

# z is the 1d array to be interpolated
zz = np.ones(len(xx)) * -999.0

# perform the triangulation
# do this using shapefunctions, and not using matplotlib
ones = np.ones(3)

# go through each node in the tin file, and locate to which tin element the
# mesh node belongs to

pbar = ProgressBar(maxval=e*len(zz)).start()
count = 0
for i in range(e):
	# re-create the element as matplotlib path object
	pth = np.array([[x[ikle[i,0]], y[ikle[i,0]]],
			[x[ikle[i,1]], y[ikle[i,1]]],
			[x[ikle[i,2]], y[ikle[i,2]]]])
	bbPath = mplPath.Path(pth)
	
	for j in range(len(zz)):
		count = count + 1
		pbar.update(count)
		# create a tupple for node j
		node = (xx[j], yy[j])
		#print node
		
		# is node in bbPath
		if (bbPath.contains_point(node) == True):
			# construct fem interpolation function and interpolate
			ikle_1 = ikle[i]
			x_1 = x[ikle_1] 
			y_1 = y[ikle_1]
			z_1 = z[ikle_1]
			M = np.column_stack((ones,x_1,y_1))
			
			# Minv = linalg.inv(M)
			Minv = minverse(M)
		
			# solve for the parameters
			p_1 = linalg.solve(M,z_1)
			#p_1 = Minv.dot(z_1)
			
			# interpolate for z
			zz[j] = p_1[0] + p_1[1]*xx[j] + p_1[2]*yy[j]
			
			if ((zz[j] < minz) and (zz[j] > maxz)):
				zz[j] = -999.0
			
			#print node 
			#print 'node ' + str(j) + ' is in element ' + str(i)
			#print ''
		else:
			if (zz[j] == 0):
				zz[j] = -999.0
pbar.finish()
# reshape the zz array to create a 2d array
interp_zz = np.reshape(zz, (xreg.shape[0], xreg.shape[1]))

print "Shape of array z: " + str(interp_zz.shape[0])

print "Shape of arrays xreg and yreg: " + str(x_regs.shape) + " " + str(y_regs.shape) 

where_are_NaNs = np.isnan(interp_zz)
interp_zz[where_are_NaNs] = -999.0

#np.savetxt("temp.out", z, fmt='%.2f', delimiter='') # this has no max spaces
np.savetxt('temp.out', np.flipud(interp_zz), fmt='%10.3f', delimiter='') # this has 10 char spaces, 2 after decimal

# open the output *.asc file, and write the header info
fout.write("NCOLS " + str(interp_zz.shape[1]) + "\n")
fout.write("NROWS " + str(interp_zz.shape[0]) + "\n")
fout.write("XLLCORNER " + str(xreg[0,0]) + "\n")
fout.write("YLLCORNER " + str(yreg[0,0]) + "\n")
fout.write("CELLSIZE " + str(spacing) + "\n")
fout.write("NODATA_VALUE " + str(-999.00) + "\n")

# read the file, and write every line in fout
with open("temp.out") as fp:
	for line in fp:
		fout.write(line);
# remove the temp file
print "Removing temporary files ..."
os.remove("temp.out")
print "Done"



