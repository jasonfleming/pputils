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
# algorithm. As I couldn't figure out Python's subprocess module to call
# executable binaries, this script simply generates a bash script, which
# has to be executed from the command line afterwards to produce the
# renumbered mesh.
#
# Uses: Python2.7.9, Matplotlib v1.4.2, Numpy v1.8.2
#
# Example:
#
# python renumber.py -i out.grd -o renumberMesh.sh
# where:
# -i input adcirc mesh file
# -o output bash script created which is to be executed.
#
# Make the script executable:
# chmod +x renumberMesh.sh
#
# then execute the script:
# ./renumberMesh.sh
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import struct                              # to determine sys architecture
from ppmodules.readMesh import *           # readMesh functions
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
	print 'python renumber.py -i out.grd -o renumberMesh.sh'
	sys.exit()
	
dummy1 =  sys.argv[1]
input_file = sys.argv[2]
dummy2 = sys.argv[3]
output_file = sys.argv[4]

# to create the temporary output files
fn = open("out_nodes.txt","w")
fe = open("out_elements.txt","w")

# this is the shell script
fsh = open(output_file, "w")

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

# write the front matter of the *.sh file
fsh.write('#!/bin/bash' + '\n')

if (os.name == 'posix'):
	
	# move the temp files to ./renumber/bin
	# subprocess.call('mv out_nodes.txt out_elements.txt ./renumber/bin',shell=True)
	fsh.write('mv out_nodes.txt out_elements.txt ./renumber/bin' + '\n')
	
	# change directory to get to executable
	#os.chdir('./renumber/bin')
	fsh.write('cd ./renumber/bin' + '\n')
	
	# run the binary executable (this was compiled in gfortran)
	if (archtype == 32):
		# its 32-bit
		
		# make sure the binary is allowed to be executed
		fsh.write('chmod +x triangulation_rcm_32' + '\n')
		
		# execute the binary to generate the renumbered nodes and elements
		fsh.write('./triangulation_rcm_32 out' + '\n')
		
		# move the files back
		fsh.write('mv *.txt ' + curdir + '\n')
		
		# change directory back
		fsh.write('cd ' + curdir + '\n')
		
		# this is the name of the renumbered *.grd file
		rcm_grd = input_file.split('.',1)[0] + '_rcm.grd'
		
		# now, run ren2adcirc to get the adcirc file back
		fsh.write('python ren2adcirc.py -i out_rcm_nodes.txt ')
		fsh.write('out_rcm_elements.txt -o ' + rcm_grd + ' -s ')
		fsh.write(str(xref) + ' ' + str(yref) + '\n')
		
		# delete the intermediate files
		fsh.write('rm out_nodes.txt out_elements.txt out_rcm_nodes.txt ')
		fsh.write('out_rcm_elements.txt' + '\n')
		
	else:
		# its 64-bit
		# make sure the binary is allowed to be executed
		fsh.write('chmod +x triangulation_rcm_64' + '\n')
		
		# execute the binary to generate the renumbered nodes and elements
		fsh.write('./triangulation_rcm_64 out' + '\n')
		
		# move the files back
		fsh.write('mv *.txt ' + curdir + '\n')
		
		# change directory back
		fsh.write('cd ' + curdir + '\n')
		
		# this is the name of the renumbered *.grd file
		rcm_grd = input_file.split('.',1)[0] + '_rcm.grd'
		
		# now, run ren2adcirc to get the adcirc file back
		fsh.write('python ren2adcirc.py -i out_rcm_nodes.txt ')
		fsh.write('out_rcm_elements.txt -o ' + rcm_grd + ' -s ')
		fsh.write(str(xref) + ' ' + str(yref) + '\n')
		
		# delete the intermediate files
		fsh.write('rm out_nodes.txt out_elements.txt out_rcm_nodes.txt ')
		fsh.write('out_rcm_elements.txt' + '\n')
