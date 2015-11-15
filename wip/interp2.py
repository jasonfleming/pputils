#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 interp2.py                             # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Aug 28, 2015
#
# Purpose: Script takes in a tin and a mesh file (both in ADCIRC format), 
# and interpolates the nodes of the mesh file from the tin. 
#
# Uses brute force to locate which mesh point (to be interpolated) lies in 
# which tin element, which leads to impractical execution times. DO NOT USE!
#
# Uses: Python2.7.9, Matplotlib v1.4.2, Numpy v1.8.2
#
# Example:
#
# python interp2.py -t tin.14 -m mesh.14 -o mesh_interp.14
# where:
# -t tin surface
# -m mesh (whose nodes are to be interpolated)
# -o interpolated mesh
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import matplotlib.tri    as mtri           # matplotlib triangulations
import numpy             as np             # numpy
from scipy import linalg
from scipy import spatial                  # kd tree for searching coords
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
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 7 :
	print 'Wrong number of Arguments, stopping now...'
	print 'Usage:'
	print 'python interp2.py -t tin.14 -m mesh.14 -o mesh_interp.14'
	sys.exit()

dummy1 =  sys.argv[1]
tin_file = sys.argv[2]
dummy2 =  sys.argv[3]
mesh_file = sys.argv[4]
dummy3 =  sys.argv[5]
output_file = sys.argv[6] # interp_mesh

# read the adcirc tin file
t_n,t_e,t_x,t_y,t_z,t_ikle = read_adcirc(tin_file)

# makes all tin points so that KDTree algorithm can use it
#tin_points = zip(t_x,t_y)
#tree = spatial.KDTree(tin_points)

# read the adcirc mesh file
# this one has z values that are all zeros
m_n,m_e,m_x,m_y,m_z,m_ikle = read_adcirc(mesh_file)

ones = np.ones(3)

# go through each node in the tin file, and locate to which tin element the
# mesh node belongs to
pbar = ProgressBar(maxval=t_e*len(m_z)).start()
count = 0
for i in range(t_e):
	# re-create the element as matplotlib path object
	pth = np.array([[t_x[t_ikle[i,0]], t_y[t_ikle[i,0]]],
			[t_x[t_ikle[i,1]], t_y[t_ikle[i,1]]],
			[t_x[t_ikle[i,2]], t_y[t_ikle[i,2]]]])
	bbPath = mplPath.Path(pth)
	
	for j in range(m_n):
		count = count + 1
		pbar.update(count)
		
		# create a tupple for node j
		node = (m_x[j], m_y[j])
		#print node
		
		# is node in bbPath
		if (bbPath.contains_point(node) == True):
			# construct fem interpolation function and interpolate
			ikle_1 = t_ikle[i]
			x_1 = t_x[ikle_1] 
			y_1 = t_y[ikle_1]
			z_1 = t_z[ikle_1]
			M = np.column_stack((ones,x_1,y_1))
			Minv = linalg.inv(M)

			# solve for the parameters
			p_1 = np.linalg.solve(M,z_1)
			
			# interpolate for z
			m_z[j] = p_1[0] + p_1[1]*m_x[j] + p_1[2]*m_y[j]
			
			#print node 
			#print 'node ' + str(j) + ' is in element ' + str(i)
			#print ''
		else:
			if (m_z[j] == 0):
				m_z[j] = -999.0
pbar.finish()
# if the node is outside of the boundary of the domain, assign value -999.0
# as the interpolated node

minidx = np.argmin(m_z)

if (m_z[minidx] < -998.0):
	print '#####################################################'
	print ''
	print 'WARNING: Some nodes are outside of the TIN boundary!!!'
	print ''
	print 'A value of -999.0 is assigned to those nodes!'
	print ''
	print '#####################################################'

# to create the output file
fout = open(output_file,"w")

# now to write the adcirc mesh file
fout.write("ADCIRC" + "\n")
# writes the number of elements and number of nodes in the header file
fout.write(str(m_e) + " " + str(m_n) + "\n")

# writes the nodes
for i in range(0,m_n):
	fout.write(str(i+1) + " " + str("{:.3f}".format(m_x[i])) + " " + 
		str("{:.3f}".format(m_y[i])) + " " + str("{:.3f}".format(m_z[i])) + "\n")
#
# writes the elements
for i in range(0,m_e):
	fout.write(str(i+1) + " 3 " + str(m_ikle[i,0]+1) + " " + str(m_ikle[i,1]+1) + " " + 
		str(m_ikle[i,2]+1) + "\n")	
#


