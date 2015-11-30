#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 renumber.py                           # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: November 29, 2015
#
# Purpose: Script takes in a mesh in ADCIRC format, and renumbers the mesh
# using John Burkardt's implementation of the Reverse-Cuthill-McKee 
# algorithm. The script uses Python's subprocess to call the binaries that
# were compiled with gfortran.
#
# Uses: Python2.7.9, Matplotlib v1.4.2, Numpy v1.8.2
#
# Example:
#
# python renumber.py -i out.grd -o renumberMesh.sh
# where:
# -i input adcirc mesh file
# -o adcirc mesh file renumbered according to Reverse-Cuthill-McKee algorithm
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import struct                              # to determine sys architecture
from ppmodules.readMesh import *           # readMesh functions
import subprocess
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
	print 'python renumber.py -i out.grd -o out_rcm'
	sys.exit()
	
dummy1 =  sys.argv[1]
input_file = sys.argv[2]
dummy2 = sys.argv[3]
output_file = sys.argv[4]

# to create the temporary output files
fn = open("out_nodes.txt","w")
fe = open("out_elements.txt","w")

# read the adcirc file
n,e,x,y,z,ikle = readAdcirc(input_file)

# before writing the files, find coordinates of x and y min (to subtract from)
xref = x[np.argmin(x)] 
yref = y[np.argmin(x)] 

# write the shifted temporary output files
for i in range(n):
	fn.write(str(x[i]-xref) + ' ' + str(y[i]-yref) + ' ' + str(z[i]) + '\n')

for i in range(e):
	fe.write(str(ikle[i,0]) + ' ' + str(ikle[i,1]) + ' ' + str(ikle[i,2]) + '\n')

fn.close()
fe.close()

# outputs posix if on linux
#print 'Operating system: ' + os.name

# prints whether system is 32 or 64 bit
archtype = struct.calcsize("P") * 8
#print 'Architecture: ' + str(archtype) + ' bit'

# prints current directory
# print 'Current directory: ' + os.getcwd()

if (os.name == 'posix'):
	
	# move the temp files to ./renumber/bin
	subprocess.call('mv out_nodes.txt out_elements.txt ./renumber/bin',shell=True)
	
	# change directory to get to executable
	os.chdir('./renumber/bin')
	
	# run the binary executable (this was compiled in gfortran)
	if (archtype == 32):
		# its 32-bit
		# make sure the binary is allowed to be executed
		subprocess.call('chmod +x triangulation_rcm_32',shell=True)
		
		# execute the binary to generate the renumbered nodes and elements
		subprocess.call(['./triangulation_rcm_32', 'out'])
		
	else:
		# its 64-bit
		# make sure the binary is allowed to be executed
		subprocess.call('chmod +x triangulation_rcm_64',shell=True)
		
		# execute the binary to generate the renumbered nodes and elements
		subprocess.call(['./triangulation_rcm_64', 'out'])
		
	# move the files back
	subprocess.call('mv *.txt ' + curdir, shell=True)
	
	# change directory back
	os.chdir(curdir)
	
	# this is the name of the renumbered *.grd file
	rcm_grd = input_file.split('.',1)[0] + '_rcm.grd'
	
	# use subprocess to call ren2adcirc.py
	# TODO: port ren2adcirc.py code here, as opposed to calling it 
	# as a subprocess
	callstr = str('python ren2adcirc.py -i out_rcm_nodes.txt ' +
		'out_rcm_elements.txt -o ' + rcm_grd + ' -s ' +
		str(xref) + ' ' + str(yref))
	
	subprocess.call(callstr, shell=True)
	
	# remove the intermediate files
	os.remove("out_nodes.txt")
	os.remove("out_rcm_nodes.txt")
	os.remove("out_elements.txt")
	os.remove("out_rcm_elements.txt")
	
	# use subprocess to call adcirc2wkt.py
	wkt_file = rcm_grd.split('.',1)[0]
	
	callstr = str('python adcirc2wkt.py -i ' + rcm_grd + ' -o ' +
		wkt_file + 'WKT_e.csv ' + wkt_file + 'WKT_n.csv')
	
	# this creates a list of the callstr, where each parameter is separed
	# by a space
	call_list = callstr.split()
	
	subprocess.call(call_list)

