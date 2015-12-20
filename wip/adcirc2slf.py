#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 adcirc2slf.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: December 20, 2015
#
# Purpose: Script takes in a mesh in ADCIRC format, and converts it to
# TELEMAC's SELAFIN format.
#
# Uses: Python2.7.9, Numpy v1.8.2
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
from ppmodules.selafin_io import *         # SELAFIN io
from ppmodules.readMesh import *           # for the readAdcirc function
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
	print 'python adcirc2sel.py -i mesh.grd -o mesh.slf'
	sys.exit()
dummy1 =  sys.argv[1]
adcirc_file = sys.argv[2]
dummy2 =  sys.argv[3]
output_file = sys.argv[4]

########################################################################
# this part of the code uses python's subprocess to call external,
# compiled version of the program bnd_extr_pp.f
# 
# if subprocess fails, run the bnd_extr_pp.f externally, and obtain
# gredit.bnd file for use in this script!
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
		subprocess.call('chmod +x bnd_extr_pp_32',shell=True)
		
		# execute the binary to generate the renumbered nodes and elements
		subprocess.call(['./bnd_extr_pp_32', adcirc_file])
	if (archtype == 64):
		# make sure the binary is allowed to be executed
		subprocess.call('chmod +x bnd_extr_pp_64',shell=True)
		
		# execute the binary to generate the renumbered nodes and elements
		subprocess.call(['./bnd_extr_pp_64', adcirc_file])

# move the files back
subprocess.call('mv *.bnd ' + curdir, shell=True)
subprocess.call('mv ' + adcirc_file + ' ' + curdir, shell=True)
	
# change directory back
os.chdir(curdir)
########################################################################

# if we are here, this means gredit.bnd file is generated and moved to 
# root dir of pputils
if (os.path.isfile('gredit.bnd') == False):
	print 'fortran compiled program bnd_exr_pp.f was not executed!'
	print 'Exiting ...'
	sys.exit()

# now open gredit.bnd and read the boundary data
# read the contents of the gredit.bnd file into a master list, where each
# item in the list is a line
master = list()
with open('gredit.bnd','r') as f:
	for i in f:
		master.append(i)
f.close()

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

# get how many arrays are in each boundary
for i in range(len(master)):
	tmp = master[i].split()
	if (len(tmp) == 2):
		bnd_nodes.append(tmp[0])
		count = count + 1
	else:
		bnd[count].append(tmp[0])

# bnd[0] is the main land boundary
# 


'''
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
'''
