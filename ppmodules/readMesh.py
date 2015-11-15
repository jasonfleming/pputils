#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import numpy             as np             # numpy
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Functions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def readAdcirc(adcirc_file):
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

