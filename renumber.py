#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 renumber.py                           # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Feb 18, 2016
#
# Purpose: Script takes in a mesh in ADCIRC format, and renumbers the mesh
# using John Burkardt's implementation of the Reverse-Cuthill-McKee 
# algorithm. The script uses Python's subprocess to call the binaries that
# were compiled with gfortran.
#
# Revised: Apr 29, 2017
# Changed how different system architectures are called; made it run
# for the raspberry pi system.
#
# Only works on Linux/Unix; TODO: make it work under windows
#
# Uses: Python 2 or 3
#
# Example:
#
# python renumber.py -i out.grd -o out_rcm.grd
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
try:
  # this only works when the paths are sourced!
  pputils_path = os.environ['PPUTILS']
except:
  pputils_path = curdir
  
  # this is to maintain legacy support
  if (sys.version_info > (3, 0)):
    version = 3
    pystr = 'python3'
  elif (sys.version_info > (2, 7)):
    version = 2
    pystr = 'python'
#
# I/O
if len(sys.argv) != 5 :
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python renumber.py -i out.grd -o out_rcm.grd')
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

if (os.name == 'posix'):
  # determines processor type
  # for linux32 its i686
  # for linux64 its x86_64
  # for raspberry pi 32 its armv7l
  
  proctype = os.uname()[4][:]
  
  # this assumes chmod +x has already been applied to the binaries
  if (proctype == 'i686'):
    callstr = pputils_path + '/renumber/bin/triangulation_rcm_32 out'
  elif (proctype == 'x86_64'):
    callstr = pputils_path + '/renumber/bin/triangulation_rcm_64 out'
  elif (proctype == 'armv7l'):
    callstr = pputils_path + '/renumber/bin/triangulation_rcm_pi32 out'
  else:
    print('OS not supported!')
    print('Exiting!')
    sys.exit()
  
  # run the binary executable (this was compiled in gfortran)
  subprocess.call(callstr, shell=True)
     
  # use subprocess to call ren2adcirc.py
  # TODO: port ren2adcirc.py code here, as opposed to calling it 
  # as a subprocess
  try:
    # this only works when the paths are sourced!
    callstr = str('ren2adcirc.py -i out_rcm_nodes.txt ' +
      'out_rcm_elements.txt -o ' + output_file + ' -s ' +
      str(xref) + ' ' + str(yref))
    
    call_list = callstr.split()
    subprocess.call(call_list)
  except:
    callstr = str(pystr + ' ren2adcirc.py -i out_rcm_nodes.txt ' +
      'out_rcm_elements.txt -o ' + output_file + ' -s ' +
      str(xref) + ' ' + str(yref))

    call_list = callstr.split()
    subprocess.call(call_list)
  
  # remove the intermediate files
  os.remove("out_nodes.txt")
  os.remove("out_rcm_nodes.txt")
  os.remove("out_elements.txt")
  os.remove("out_rcm_elements.txt")
  
  # use subprocess to call adcirc2wkt.py
  # strip the extension from output file string
  wkt_file = output_file.split('.',1)[0]

  try:
    # this only works when the paths are sourced!
    callstr = str('adcirc2wkt.py -i ' + output_file + ' -o ' + wkt_file + 'WKT.csv')
    call_list = callstr.split()
    subprocess.call(call_list)
    
  except:
    callstr = str(pystr + ' adcirc2wkt.py -i ' + output_file + ' -o ' + wkt_file + 'WKT.csv')  
    call_list = callstr.split()
    subprocess.call(call_list)
