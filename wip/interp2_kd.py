#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 interp2_kd.py                         # 
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
# Same as interp2.py, but uses kd_algorithm to limit number of elements
# to go through; DOES NOT COMPLETELY WORK! DO NOT USE!
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
#
def point_in_poly(x,y,poly):
	#{{{
   # check if point is a vertex
   if (x,y) in poly: return "IN"

   # check if point is on a boundary
   for i in range(len(poly)):
      p1 = None
      p2 = None
      if i==0:
         p1 = poly[0]
         p2 = poly[1]
      else:
         p1 = poly[i-1]
         p2 = poly[i]
      if p1[1] == p2[1] and p1[1] == y and x > min(p1[0], p2[0]) and x < max(p1[0], p2[0]):
         return "IN"
      
   n = len(poly)
   inside = False

   p1x,p1y = poly[0]
   for i in range(n+1):
      p2x,p2y = poly[i % n]
      if y > min(p1y,p2y):
         if y <= max(p1y,p2y):
            if x <= max(p1x,p2x):
               if p1y != p2y:
                  xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
               if p1x == p2x or x <= xints:
                  inside = not inside
      p1x,p1y = p2x,p2y

   if inside: return "IN"
   else: return "OUT"
   #}}}
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 9 :
	print 'Wrong number of Arguments, stopping now...'
	print 'Usage:'
	print 'python interp2.py -t tin.14 -m mesh.14 -o mesh_interp.14 -r 10'
	sys.exit()

dummy1 =  sys.argv[1]
tin_file = sys.argv[2]
dummy2 =  sys.argv[3]
mesh_file = sys.argv[4]
dummy3 =  sys.argv[5]
output_file = sys.argv[6] # interp_mesh
dummy4 = sys.argv[7]
radius = sys.argv[8]
radius = float(radius)

# read the adcirc tin file
t_n,t_e,t_x,t_y,t_z,t_ikle = read_adcirc(tin_file)

# makes all tin points so that KDTree algorithm can use it
tin_points = zip(t_x,t_y)
tree = spatial.KDTree(tin_points)

# read the adcirc mesh file
# this one has z values that are all zeros
m_n,m_e,m_x,m_y,m_z,m_ikle = read_adcirc(mesh_file)

ones = np.ones(3)

minz = np.amin(t_z)
maxz = np.amax(t_z)

###############################################
# pasted from adcirc2asc2_kd.py
# and replaced zz with m_z ...

# to determine the select nodes for which node j could possibly belong to
idx = np.ones(len(m_z)) * -999.0

# the node used for to find neighbouring tin nodes
# I call it mesh, but it is actually grid node
mesh_node_pt = list()

# to each grid node provide a candidate list of nodes to seach from
cand_nodes = np.zeros(len(m_z)*10)-999.0
cand_nodes = cand_nodes.astype(np.int32)
cand_nodes_matrix = np.reshape(cand_nodes, (len(m_z),10))
cand_nodes_matrix = cand_nodes_matrix.astype(np.int32)

print ' '
print 'Searching for nodes using kd_tree algorithm'
pbar = ProgressBar(maxval=len(m_z)).start()

for j in range(len(m_z)):
	mesh_node_pt.append(m_x[j])
	mesh_node_pt.append(m_y[j])
	
	idx_temp = tree.query_ball_point(mesh_node_pt, radius)
	
	if (len(idx_temp) > 0):
		# store first ten candidate nodes
		for i in range(len(idx_temp)):
			cand_nodes_matrix[j,i] = idx_temp[i] 
		idx[j] = idx_temp[0]
		# print 'grid node ' + str(xx[j]) + ', ' + str(yy[j]) + ' is closest to node '
		# print idx_temp
		# print '###############'
	else:
		print 'Corresponding tin node not found for mesh node ' + str(m_x[j]) + ', ' + str(m_y[j])
		print 'Hint: try increasing kd_tree search radius'
		sys.exit()
	
	# remove the node
	mesh_node_pt.remove(m_x[j])
	mesh_node_pt.remove(m_y[j])
	
	pbar.update(j+1)
pbar.finish()
print ' '

#np.savetxt('out_nod.txt', cand_nodes_matrix, fmt='%6.0f') 

# for each grid node, need to find all corresponding tin elements
# for now, I am assuming only 10 candiate elements to be included
cand_elements = np.zeros(len(m_z)*10)-999.0
cand_elements = cand_elements.astype(np.int32)
cand_elements_matrix = np.reshape(cand_elements, (len(m_z),10))
cand_elements_matrix = cand_elements_matrix.astype(np.int32)

# this is the number of grid points (i.e., number of rows in cand_elements_matrix
n_grid_pts = cand_elements_matrix.shape[0]

# n,e,x,y,z,ikle = read_adcirc(adcirc_file)

for i in range(t_e):
	for j in range(n_grid_pts):
		for k in range(10):
			if (t_ikle[i,0] == cand_nodes_matrix[j,k]):
				cand_elements_matrix[j,k] = i
			if (t_ikle[i,1] == cand_nodes_matrix[j,k]):
				cand_elements_matrix[j,k] = i				
			if (t_ikle[i,2] == cand_nodes_matrix[j,k]):
				cand_elements_matrix[j,k] = i					
#np.savetxt('out_ele.txt', cand_elements_matrix, fmt='%6.0f') 

ep = cand_elements_matrix
###############################################

# go through each node in the tin file, and locate to which tin element the
# mesh node belongs to
pbar = ProgressBar(maxval=10*len(m_z)).start()
count = 0

tmp = -999
tmp_array = np.zeros(10) + -999.0

for j in range(len(m_z)):
	tmp_array = np.unique(ep[j,:])
	
	for k in range(len(tmp_array)):
		count = count + 1
		pbar.update(count)
		if (tmp_array[k] != -999):
			tmp = tmp_array[k]
			
			# re-create the element for point_in_poly function
			poly = [(t_x[t_ikle[tmp,0]], t_y[t_ikle[tmp,0]]),
				(t_x[t_ikle[tmp,1]], t_y[t_ikle[tmp,1]]),
				(t_x[t_ikle[tmp,2]], t_y[t_ikle[tmp,2]]),
				(t_x[t_ikle[tmp,0]], t_y[t_ikle[tmp,0]])]
	  	
			# create a tupple for node j
			node = (m_x[j], m_y[j])
			
			#print node
			
			# is node inside the polygon
			if (point_in_poly(m_x[j],m_y[j],poly) == 'IN'):
				# construct fem interpolation function and interpolate
				ikle_1 = t_ikle[tmp]
				x_1 = t_x[ikle_1] 
				y_1 = t_y[ikle_1]
				z_1 = t_z[ikle_1]
				M = np.column_stack((ones,x_1,y_1))
				
				#Minv = linalg.inv(M)
				Minv = minverse(M)
			
				# solve for the parameters
				p_1 = linalg.solve(M,z_1)
				#p_1 = np.zeros(3)
				
				# interpolate for z
				m_z[j] = p_1[0] + p_1[1]*m_x[j] + p_1[2]*m_y[j]
				
				if ((m_z[j] < minz) and (m_z[j] > maxz)):
					m_z[j] = -999.0
				break
		
pbar.finish()

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


