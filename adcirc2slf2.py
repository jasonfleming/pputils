#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 adcirc2slf.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: February 15, 2016
#
# Purpose: Script takes in a mesh in ADCIRC format, and converts it to
# TELEMAC's SELAFIN format. Made it to depend on selafin_io_pp, which
# works under python 2 and 3!
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python adcirc2sel.py -i mesh.grd -o mesh.slf
# where:
# -i input adcirc mesh file
# -o converted *.slf mesh file
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy as np                         # numpy
import struct                              # to determine sys architecture
import subprocess                          # to execute binaries
from ppmodules.selafin_io_pp import *      # pp's SELAFIN io
from ppmodules.readMesh import *           # for the readAdcirc function
#
# this is the function that returns True if the elements is oriented CCW
#def CCW((x1,y1),(x2,y2),(x3,y3)):
#	return (y3-y1)*(x2-x1) > (y2-y1)*(x3-x1)

# this works for python 2 and 3
def CCW(x1,y1,x2,y2,x3,y3):
   return (y3-y1)*(x2-x1) > (y2-y1)*(x3-x1)	
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 5 :
	print('Wrong number of Arguments, stopping now...')
	print('Usage:')
	print('python adcirc2sel.py -i mesh.grd -o mesh.slf')
	sys.exit()
dummy1 =  sys.argv[1]
adcirc_file = sys.argv[2]
dummy2 =  sys.argv[3]
output_file = sys.argv[4]

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
	print("Under windows, need more testing ...")
	sys.exit()
	# callstr = ".\\boundary\\bin\\bnd_extr_pp_32.exe"
	# subprocess.call([callstr, adcirc_file])
	
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
# indexes to start at zero, add 1 to all elements in ikle array
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
cli_file = output_file.split('.',1)[0] + '.cli'

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

#######################################################################
# it gets these from readAdcirc function
NELEM = e
NPOIN = n
NDP = 3 # always 3 for triangular elements
IKLE = ikle	
IPOBO = ppIPOB

slf = ppSELAFIN(output_file)
slf.setPrecision('f',4) # single precision
slf.setTitle('created with pputils')
slf.setVarNames(['BOTTOM          '])
slf.setVarUnits(['M               '])
slf.setIPARAM([1, 0, 0, 0, 0, 0, 0, 0, 0, 1])
slf.setMesh(NELEM, NPOIN, NDP, IKLE, IPOBO, x, y)
slf.writeHeader()

# if writing only 1 variable, must have numpy array of size (1,NPOIN)
# for 2 variables, must have numpy array of size (2,NPOIN), and so on.
zz = np.zeros((1,NPOIN))
zz[0,:] = z

slf.writeVariables([0.0], zz)
#######################################################################

'''
# when I used hrw's selafin_io, I used code below to write the *.slf files
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
slf2d.IPOB2 = ppIPOB
slf2d.IPOB3 = ppIPOB

#print '     +> Set SELAFIN IKLE'
slf2d.IKLE2 = ikle
slf2d.IKLE3 = ikle

#print '     +> Set SELAFIN times and cores'
# these two lists are empty after constructor is instantiated
slf2d.tags['cores'].append(0)
slf2d.tags['times'].append(0)

#slf2d.tags = { 'times':[0] } # time (sec)
#slf2d.DATETIME = sel.DATETIME
# Aug 29, 1997 2:15 am EST (date when skynet became self-aware)
slf2d.DATETIME = [1997, 8, 29, 2, 15, 0]
#slf2d.tags = { 'cores':[long(0)] } # time frame 

#print '     +> Write SELAFIN headers'
slf2d.fole.update({ 'hook': open(output_file,'w') })
slf2d.fole.update({ 'name': 'Converted from ADCIRC with pputils' })
slf2d.fole.update({ 'endian': ">" })     # big endian
slf2d.fole.update({ 'float': ('f',4) })  # ('f',4) is single precision 
#                                        # ('d',8) is double precision

slf2d.appendHeaderSLF()
slf2d.appendCoreTimeSLF(0) 
slf2d.appendCoreVarsSLF([z])
'''

