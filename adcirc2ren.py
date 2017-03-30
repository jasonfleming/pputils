#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 adcirc2ren.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Feb 18, 2016
#
# Purpose: Script takes in a mesh in ADCIRC format, and outputs a nodes 
# and elements file for use in John Burkardt's rcm renumbering algorithm.
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python adcirc2ren.py -i out.grd -o out_nodes.txt out_elements.txt
# where:
# -i input adcirc mesh file
# -o output files needed for rcm renumbering
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy             as np             # numpy
from ppmodules.readMesh import *           # to get all readMesh functions
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 6 :
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python adcirc2ren.py -i out.grd -o out_nodes.txt out_elements.txt')
  sys.exit()
dummy1 =  sys.argv[1]
adcirc_file = sys.argv[2]
dummy2 = sys.argv[3]
nodes_file = sys.argv[4]
elements_file = sys.argv[5]

# to create the output files
fn = open(nodes_file,"w")
fe = open(elements_file,"w")

# read the adcirc file
n,e,x,y,z,ikle = readAdcirc(adcirc_file)

# before writing the files, find coordinates of x min (to subtract from)
xref = x[np.argmin(x)] 
yref = y[np.argmin(x)] 

for i in range(n):
  fn.write(str(x[i]-xref) + ' ' + str(y[i]-yref) + ' ' + str(z[i]) + '\n')
  
for i in range(e):
  fe.write(str(ikle[i,0]) + ' ' + str(ikle[i,1]) + ' ' + str(ikle[i,2]) + '\n')
  
  
fo = open('coord_shift.txt','w')  
fo.write(str(xref) + ' ' + str(yref))

