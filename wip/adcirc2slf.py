#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 adcirc2slf.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: June 29, 2015
#
# Purpose: Script takes in a mesh in ADCIRC format, and converts it to
# TELEMAC's SELAFIN format. Does not fill IPOB array properly; it simply
# writes boundary nodes as the IPOB array, with no knowledge of CW or CCW.
# To be fixed in subsequent version!
#
# Uses: Python2.7.9, Matplotlib v1.4.2, Numpy v1.8.2
#
# Example:
#
# python adcirc2sel.py -i mesh.14 -o mesh.slf
# where:
# -i input adcirc mesh file
# -o converted *.slf mesh file
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
from os import path
import matplotlib.tri    as mtri           # matplotlib triangulations
import numpy             as np             # numpy
import math                                # for the ceil function
# Importing pytel tools for SELAFIN parser
pytel = os.getcwd()
#pytel = '/home/user/opentelemac/v7p0r1/scripts/python27/'
sys.path.append(path.join(path.dirname(sys.argv[0]),pytel))
from parsers.parserSELAFIN import SELAFIN  
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
	
	ikle = ikle.astype(np.int16)
	
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
if len(sys.argv) != 5 :
	print 'Wrong number of Arguments, stopping now...'
	print 'Usage:'
	print 'python adcirc2sel.py -i mesh.14 -o mesh.slf'
	sys.exit()
dummy1 =  sys.argv[1]
adcirc_file = sys.argv[2]
dummy2 =  sys.argv[3]
output_file = sys.argv[4]

# read the adcirc file
n,e,x,y,z,ikle = read_adcirc(adcirc_file)

# writes the slf2d file
slf2d = SELAFIN('')

#print '     +> Set SELAFIN variables'
slf2d.TITLE = 'Converted from ADCIRC with pputils'
slf2d.NBV1 = 1 
slf2d.NVAR = 1
slf2d.VARINDEX = range(slf2d.NVAR)
slf2d.VARNAMES.append('BOTTOM          ')
slf2d.VARUNITS.append('M               ')

#print '     +> Set SELAFIN sizes'
slf2d.NPLAN = 1
slf2d.NDP2 = 3
slf2d.NDP3 = 3
slf2d.NPOIN2 = n
slf2d.NPOIN3 = n
slf2d.NELEM2 = e
slf2d.NELEM3 = e
slf2d.IPARAM = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]

#print '     +> Set SELAFIN mesh'
slf2d.MESHX = x
slf2d.MESHY = y

#print '     +> Set SELAFIN IPOBO'
#junkIPOB = np.zeros(n)
junkIPOB = np.arange(n)
slf2d.IPOB2 = junkIPOB
slf2d.IPOB3 = junkIPOB

#print '     +> Set SELAFIN IKLE'
slf2d.IKLE2 = ikle
slf2d.IKLE3 = ikle

#print '     +> Set SELAFIN times and cores'
# these two lists are empty after constructor is instantiated
slf2d.tags['cores'].append(0)
slf2d.tags['times'].append(0)

#slf2d.tags = { 'times':[0] } # time (sec)
#slf2d.DATETIME = sel.DATETIME
slf2d.DATETIME = [2015, 1, 1, 1, 1, 1]
#slf2d.tags = { 'cores':[long(0)] } # time frame 

#print '     +> Write SELAFIN headers'
slf2d.fole.update({ 'hook': open(output_file,'w') })
slf2d.fole.update({ 'name': 'Converted from ADCIRC with pputils' })
slf2d.fole.update({ 'endian': ">" })     # big endian
slf2d.fole.update({ 'float': ('f',4) })  # single precision

slf2d.appendHeaderSLF()
slf2d.appendCoreTimeSLF(0) 
slf2d.appendCoreVarsSLF([z])

