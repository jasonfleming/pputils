import os,sys     
import numpy as np
import struct     
import subprocess
from collections import OrderedDict
from scipy import spatial
from ppmodules.readMesh import *
from progressbar import ProgressBar, Bar, Percentage, ETA

def remove_duplicate_nodes(x,y,z):
	# this still needs testing!
	
	# crop all the points to three decimals only
	x = np.around(x,decimals=3)
	y = np.around(y,decimals=3)
	z = np.around(z,decimals=3)
	
	# this piece of code uses OrderedDict to remove duplicate nodes
	# source "http://stackoverflow.com/questions/12698987"
	# ###################################################################
	tmp = OrderedDict()
	for point in zip(x, y):
	  tmp.setdefault(point[:1], point)
	
	# in python 3 tmp.values() is a view object that needs to be 
	# converted to a list
	mypoints = list(tmp.values()) 
	# ###################################################################
	
	n_rev = len(mypoints)
	
	x_new = np.zeros(n_rev)
	y_new = np.zeros(n_rev)
	z_new = np.zeros(n_rev)
	
	for i in range(len(mypoints)):
		x_new[i] = mypoints[i][0]
		y_new[i] = mypoints[i][1]
	
	# now that we have unique x and y, we need to assign a z to each node
	# use a cKDTree search to do this
	source = np.column_stack((x,y))
	tree = spatial.cKDTree(source)
	
	w = [Percentage(), Bar(), ETA()]
	pbar = ProgressBar(widgets=w, maxval=n_rev).start()
	for i in range(n_rev):
		d,idx = tree.query( (x_new[i],y_new[i]), k = 1)
		z_new[i] = z[idx]
		pbar.update(i+1)
	pbar.finish()	
	
	return x_new,y_new,z_new

def adjustTriangulation(n,e,x,y,z,ikle):
	
	# this is the eps shift to be applied to the nodes
	eps = 1.0e-6
	
	# find area of each element
	for i in range(e):
		x1 = x[ikle[i,0]]
		y1 = y[ikle[i,0]]
		x2 = x[ikle[i,1]]
		y2 = y[ikle[i,1]]
		x3 = x[ikle[i,2]]
		y3 = y[ikle[i,2]]
		
		twoA = (x2*y3 - x3*y2) - (x1*y3-x3*y1) + (x1*y2 - x2*y1)
		area = twoA / 2.0
		
		# assume that if area of the element is less than 1.0e-6 then 
		# it will be an element that will require shifting of nodes
		if (area < eps):
			# calculate edge lengths
			l12 = np.sqrt( np.power(abs(x1-x2),2) + np.power(abs(y1-y2),2))
			l23 = np.sqrt( np.power(abs(x2-x3),2) + np.power(abs(y2-y3),2))
			l31 = np.sqrt( np.power(abs(x3-x1),2) + np.power(abs(y3-y1),2))
			
			if ((l23 > l31) and (l23 > l12)):
				# node 1 is middle, shift it by +ve delta
				x1 = x1 + eps
				y1 = y1 + eps
				
				# shift nodes 2 and 2 by a -ve delta
				x2 = x2 - eps
				y2 = y2 - eps

				x3 = x3 - eps
				y3 = y3 - eps
				
			elif ((l31 > l12) and (l31 > l23)):
				# node 2 is middle, shift it by +ve delta
				x2 = x2 + eps
				y2 = y2 + eps
				
				# shift nodes 1 and 3 by a -ve delta
				x1 = x1 - eps
				y1 = y1 - eps

				x3 = x3 - eps
				y3 = y3 - eps
				
			elif ((l12 > l23) and (l12 > l31)):
				# node 3 is middle, shift it by +ve delta
				x3 = x3 + eps
				y3 = y3 + eps
				
				# shift nodes 1 and 2 by a -ve delta
				x1 = x1 - eps
				y1 = y1 - eps

				x2 = x2 - eps
				y2 = y2 - eps
				
			else:
				# this is needed as the part of the code that removes
				# duplicate nodes allows for two nodes at the same location
				# as long as they have a different z! 
				
				# this has to be fixed in the scripts that generate the tin
				# (i.e., gis2triangle.py and gis2triangle_kd.py)
				
				# print('element ' + str(i+1))
				# print((l12,l23,l31))
				
				if (l12 < eps):
					x1 = x1 + eps
					y1 = y1 + eps
				elif (l23 < eps):
					x2 = x2 + eps
					y2 = y2 + eps
				elif (l31 < eps):
					x3 = x3 + eps
					y3 = y3 + eps
					
			# update the coordinates in the input arrays
			x[ikle[i,0]] = x1
			y[ikle[i,0]] = y1
			x[ikle[i,1]] = x2
			y[ikle[i,1]] = y2
			x[ikle[i,2]] = x3
			y[ikle[i,2]] = y3			
					
	# returns the shifted x and y coordinates			
	return x, y

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

# this function was obtained from
# http://geospatialpython.com/2011/08/point-in-polygon-2-on-line.html

# Improved point in polygon test which includes edge
# and vertex points

def point_in_poly(x,y,poly):

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

# python version of ptInTriangle
# http://stackoverflow.com/questions/2049582
#
def ptInTriangle(pt, tri):
	px = pt[0]
	py = pt[1]
	
	p0x = tri[0,0]
	p0y = tri[0,1]
	
	p1x = tri[1,0]
	p1y = tri[1,1]	
	
	p2x = tri[2,0]
	p2y = tri[2,1]	
	
	dX = px - p2x
	dY = py - p2y
	dX21 = p2x - p1x
	dY12 = p1y - p2y
	D = dY12 * (p0x - p2x) + dX21*(p0y - p2y)
	s = dY12 * dX + dX21 * dY
	t = (p2y - p0y) * dX + (p0x - p2x)*dY
	
	if (D < 0):
		return ((s<=0) and (t<=0) and (s+t>=D))
	else:
		return ((s>=0) and (t>=0) and (s+t<=D))

# this is to test the method
#pt =  np.array([0.5, 0.0])
#tri = np.array([[1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]  )
#print(ptInTriangle(pt, tri))


# identical to my fortran code idwm.f90
# takes as input an xyz array, and a coordinate x,y, and outputs the 
# z values of the input coordinate using my idwm algorithm.
def idwm(elev,x,y):

	# define some presets
	# set min_prev vars to large numbers
	min1cur = 99999.9
	min2cur = 99999.9
	min3cur = 99999.9
	min4cur = 99999.9
	
	min1pre = 99999.9
	min2pre = 99999.9
	min3pre = 99999.9
	min4pre = 99999.9
	
	# initialize min_loc
	min1loc = -1
	min2loc = -1
	min3loc = -1
	min4loc = -1
	
	# finds min and max of the elev data
	# print(np.amin(elev[2,:]), np.amax(elev[2,:]))

	# number of points in the elev data
	n = len(elev[0,:])

	dist = np.zeros(n)
	xdist = np.subtract(elev[0,:],x)
	ydist = np.subtract(elev[1,:],y)
	
	dist = np.sqrt(np.power(xdist,2.0) + np.power(ydist,2.0))
	
	# this is the loop that is really computationally expensive
	for i in range(n):
		# quadrant 1
		if (elev[0,i] >= x and elev[1,i] >= y):
			if (dist[i] < min1pre):
				min1cur = dist[i]
				min1loc = i
		
		# quadrant 2
		if (elev[0,i] < x and elev[1,i] >= y):
			if (dist[i] < min2pre):
				min2cur = dist[i]
				min2loc = i
		
		# quadrant 3
		if (elev[0,i] < x and elev[1,i] < y):
			if (dist[i] < min3pre):
				min3cur = dist[i]
				min3loc = i
    
		# quadrant 4
		if (elev[0,i] > x and elev[1,i] < y):
			if (dist[i] < min4pre):
				min4cur = dist[i]
				min4loc = i
				
		min1pre = min1cur
		min2pre = min2cur
		min3pre = min3cur
		min4pre = min4cur
	
	# to fix the division by zero error (if the point (x,y) is exactly
	# on a node of elev array	
	if (min1cur < 1.0E-6):
		min1cur = 1.0E-6

	if (min2cur < 1.0E-6):
		min2cur = 1.0E-6
		
	if (min3cur < 1.0E-6):
		min3cur = 1.0E-6
		
	if (min4cur < 1.0E-6):
		min4cur = 1.0E-6		

	# calculate the weights
	den = (1.0/(min1cur**2)) +(1.0/(min2cur**2)) +(1.0/(min3cur**2)) +\
		(1.0/(min4cur**2))
	
	#print('distances')
	#print(min1cur,min2cur,min3cur,min4cur)
	
	#print('Den ' + str(den))	
		
	# to calculate the weights
	w1 = (1.0/(min1cur**2))/den
	w2 = (1.0/(min2cur**2))/den
	w3 = (1.0/(min3cur**2))/den
	w4 = (1.0/(min4cur**2))/den	
	
	#print('weights')
	#print(w1,w2,w3,w4)
	
	#print('elevations')
	#print(elev[2,min1loc], elev[2,min2loc], elev[2,min3loc], elev[2,min4loc])
	
	#print('distances')
	#print(min1cur,min2cur,min3cur,min4cur)
	
	#print('minxloc')
	#print(min1loc,min2loc,min3loc,min4loc)
	
	# if minxloc is negative, I don't want to let python use the last
	# item in the array in the calculation (which is what it would do)
	
	if min1loc < 0:
		tmp1 = 0.0
	else:
		tmp1 = elev[2,min1loc]
		
	if min2loc < 0:
		tmp2 = 0.0
	else:
		tmp2 = elev[2,min2loc]
		
	if min3loc < 0:
		tmp3 = 0.0
	else:
		tmp3 = elev[2,min3loc]

	if min4loc < 0:
		tmp4 = 0.0
	else:
		tmp4 = elev[2,min4loc]

	z = w1*tmp1+w2*tmp2+ w3*tmp3+w4*tmp4
		
	return z
   
# this works for python 2 and 3
def CCW(x1,y1,x2,y2,x3,y3):
   return (y3-y1)*(x2-x1) > (y2-y1)*(x3-x1)

# this method takes in an adcirc file, and returns the IPOBO and IKLE arrays
# and also generates temp.cli file
# This method is exactly as what is in my adcirc2sel.py code ... 
# I will keep the code duplication until I fully test it ...
def getIPOBO_IKLE(adcirc_file):	
	########################################################################
	# this part of the code uses python's subprocess to call externally
	# compiled version of the fortran program bnd_extr_pp.f
	# 
	# if subprocess fails, run the bnd_extr_pp.f externally, and obtain
	# gredit.bnd file for use in this script! Delete everythng between the
	# lines bound by ###
	########################################################################
	# to determine if the system is 32 or 64 bit
	archtype = struct.calcsize("P") * 8
	
	curdir = os.getcwd()
	print(curdir)
	
	# to determine the IPOBO array, call pre-compiled binary bnd_extr_pp
	if (os.name == 'posix'):
		# to move the adcirc file to ./boundary/bin
		callstr = 'mv ' + str(adcirc_file) + ' ./boundary/bin'
		subprocess.call(callstr, shell=True)
	
		# change directory to get to executable
		os.chdir('./boundary/bin')
		
		if (archtype == 32):
			# make sure the binary is allowed to be executed
			subprocess.call(['chmod', '+x', 'bnd_extr_pp_32'])
			
			# execute the binary to generate the renumbered nodes and elements
			print('Executing bnd_extr_pp program ...')
			subprocess.call(['./bnd_extr_pp_32', adcirc_file])
		if (archtype == 64):
			# make sure the binary is allowed to be executed
			subprocess.call(['chmod', '+x', 'bnd_extr_pp_64'])
			
			# execute the binary to generate the renumbered nodes and elements
			print('Executing bnd_extr_pp program ...')
			subprocess.call(['./bnd_extr_pp_64', adcirc_file])
	
		# move the files back
		subprocess.call('mv *.bnd ' + curdir, shell=True)
		subprocess.call('mv ' + adcirc_file + ' ' + curdir, shell=True)
		
		# change directory back
		os.chdir(curdir)
		
	if (os.name == 'nt'):
		# nt is for windows
		#print("Under windows, need more testing ...")
		#sys.exit()
		callstr = ".\\boundary\\bin\\bnd_extr_pp_32.exe"
		subprocess.call([callstr, adcirc_file])
		
	########################################################################
	
	# if we are here, this means gredit.bnd file is generated and moved to 
	# root dir of pputils
	if (os.path.isfile('gredit.bnd') == False):
		print('Fortran compiled program bnd_exr_pp.f did not generate gredit.bnd!')
		print('Exiting ...')
		sys.exit()
	
	# now open gredit.bnd and read the boundary data
	# read the contents of the gredit.bnd file into a master list, where each
	# item in the list is a line
	master = list()
	with open('gredit.bnd','r') as f:
		for i in f:
			master.append(i)
	f.close()
	
	# delete the gredit.bnd file
	os.remove('gredit.bnd')
	
	# this is the number of boundaries read from the gredit.bnd file
	# first line is ADCIRC, second line is num_bnd 
	num_bnd = int(master[1].split()[0])
	
	# delete the first two records in the master
	del master[0]
	del master[0]
	
	# create a list for each boundary
	# bnd is a list of lists
	bnd = list()
	for i in range(num_bnd):
		bnd.append(list())
	
	# total boundary nodes for each boundary
	bnd_nodes = list()
	
	# initialize count
	count = -1
	
	# get how many arrays are in each boundary and store each
	# boundary into its own list
	# this is where interpretive languages are great!
	for i in range(len(master)):
		tmp = master[i].split()
		if (len(tmp) == 2):
			bnd_nodes.append(tmp[0])
			count = count + 1
		else:
			bnd[count].append(tmp[0])
	
	# bnd[0] is the main land boundary
	# convert the bnd[0] to a numpy array
	land_bnd = np.asarray(bnd[0],dtype=np.int32)
	
	# read the adcirc file
	n,e,x,y,z,ikle = readAdcirc(adcirc_file)
	
	# the readAdcirc function returns ikle that starts with index 0; to get
	# indexes to start at one, add 1 to all elements in ikle array
	ikle[:,0] = ikle[:,0]+1
	ikle[:,1] = ikle[:,1]+1
	ikle[:,2] = ikle[:,2]+1
	
	# go through each element, and make sure it is oriented in CCW fashion
	for i in range(len(ikle)):
		
		# if the element is not CCW then must change its orientation
		if not CCW( x[ikle[i,0]-1], y[ikle[i,0]-1], x[ikle[i,1]-1], y[ikle[i,1]-1], 
			x[ikle[i,2]-1], y[ikle[i,2]-1] ):
			
			t0 = ikle[i,0]
			t1 = ikle[i,1]
			t2 = ikle[i,2]
			
			# switch orientation
			ikle[i,0] = t2
			ikle[i,2] = t0
			
			#print('switching orientation for element: ' +str(i+1))
	
	# note that the nodes here are indexed starting at zero
	node = np.arange(n)+1
	
	# find lower left corner of the boundary
	# algorithm is this: find the distance of each land_bnd node from 
	# (-10000000,-10000000)
	# the boundary node with the smallest distance is the lower left node
	xdist = np.subtract(x,-10000000.0)
	ydist = np.subtract(y,-10000000.0)
	dist = np.sqrt(np.power(xdist,2.0) + np.power(ydist,2.0))
	
	# find the location of the LL node in the mesh
	LLnode = np.argmin(dist)
	# print 'LL node in mesh is at index: ',LLnode
	
	# find the index of the LLnode in land_bnd
	start_idx = 0
	for i in range(len(land_bnd)):
		if (land_bnd[i] == LLnode+1):
			start_idx = i
	#print 'Index in land_bnd with the LLnode is ', start_idx		
	
	# this makes sure the LLnode is at the start of the array
	land_bnd_rolled = np.roll(land_bnd, len(land_bnd) - start_idx)
	
	# return the land_bnd_rolled back to bnd[0]
	for i in range(len(bnd[0])):
		bnd[0][i] = land_bnd_rolled[i]
		
	# *.cli file name string	
	cli_file = 'temp.cli'
	
	# create the *.cli file
	fcli = open(cli_file, 'w')
	
	# this is the base data for *.cli file
	cli_base = str('2 2 2 0.000 0.000 0.000 0.000 2 0.000 0.000 0.000 ')
	
	# print all boundary nodes according to what TELEMAC needs
	a = -1
	# store it all_bnd
	# all_bnd is arranged so that it can be written to the *.cli file
	all_bnd = list()
	for i in range(num_bnd):
		for item in bnd[i]:
			a = a + 1
			all_bnd.append(item)
			fcli.write(cli_base + str(item) + ' ' + str(a+1) + '\n')
	fcli.close()
	
	# convert all_bnd from a list to a numpy array
	all_bnd_array = np.asarray(all_bnd)
	
	# now we can populate the ppIPOB array
	ppIPOB = np.zeros(n,dtype=np.int32)
	
	# we have an all_bnd_array, that lists nodes of the boundary
	# this just might work; must test
	ipob_count = 0
	
	for i in range(len(all_bnd)):
		ipob_count = ipob_count + 1
		ppIPOB[int(all_bnd[i])-1] = ipob_count
	
	return ppIPOB, ikle
	#######################################################################
