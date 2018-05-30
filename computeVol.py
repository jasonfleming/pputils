#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 computeVol.py                         # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: May 30, 2018
#
# Purpose: Script takes in a *.grd mesh or tin file along a reference
# elevation to computes the volume of the surface between the reference
# elevation and the surface.
#
# Note: This script does not know how to calculate volume in the case
# when the reference plane and a particular element intersect. An error
# is thrown in this case, and the script terminates!
#
# Uses: Python 2 or 3, Numpy
#
# Example:
#
# python computeVol.py -i tin.grd -r 100
# where:
#
# -i ==> digital surface in a *.grd file (i.e., an ADCIRC mesh or tin)
# -r ==> reference elevation above which the volume is to be computed
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import numpy             as np             # numpy 
from ppmodules.utilities import *          # to get the utilities
from ppmodules.readMesh import *           # to get the readAdcirc fun
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
#
def element_area(x1,y1,x2,y2,x3,y3):
	# signs in eqs work when the elements are CCW
	twoA = (x2*y3 - x3*y2) - (x1*y3-x3*y1) + (x1*y2 - x2*y1)
	area = twoA / 2.0
	return area
  
# this works for python 2 and 3
def CCW(x1,y1,x2,y2,x3,y3):
   return (y3-y1)*(x2-x1) > (y2-y1)*(x3-x1)
#
def computeVolume(input_file, ref_level):
  # now read the input mesh file (ikle are zero based)
  n,e,x,y,z,ikle = readAdcirc(input_file)
  
  # find the min of z
  minz = np.min(z)

  # The reference level could be intersecting an element,
  # which means the element volume would not be a truncated
  # right triangular prism. This script doesn't deal with this. As a
  # workaround, grid the TIN, and compute the volume using SAGA GIS.
  if (ref_level >= minz):
    print('Reference level too high. Reduce it, and try again. Exiting.')
    sys.exit()
  
  # make sure the elements are oriented in CCW fashion
  # go through each element, and make sure it is oriented in CCW fashion
  for i in range(len(ikle)):
    
    # if the element is not CCW then must change its orientation
    if not CCW( x[ikle[i,0]], y[ikle[i,0]], x[ikle[i,1]], y[ikle[i,1]], 
      x[ikle[i,2]], y[ikle[i,2]] ):
    
      t0 = ikle[i,0]
      t1 = ikle[i,1]
      t2 = ikle[i,2]
      
      # switch orientation
      ikle[i,0] = t2
      ikle[i,2] = t0
  
  # compute the area and volume of each element in the mesh (or tin) file
  area = np.zeros(e)
  vol = np.zeros(e)
  
  for i in range(e):
    area[i] = element_area(x[ikle[i,0]], y[ikle[i,0]], 
      x[ikle[i,1]], y[ikle[i,1]], x[ikle[i,2]], y[ikle[i,2]])
      
    # the volume between the reference level and the surface in a tin model
    # is the same as the volume of truncated right triangular prism
    vol[i] = (area[i] / 3.0) * ( (z[ikle[i,0]] - ref_level) +
      (z[ikle[i,1]] - ref_level) + (z[ikle[i,2]] - ref_level) )
    
  # the total volume is the sum of the the individual vol[i]
  volTotal = np.sum(vol)
  
  return volTotal

# main starts here
if len(sys.argv) != 5:
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python computeVol.py -i tin.grd -r 100.0')
  sys.exit()

input_file = sys.argv[2]
ref_level = float(sys.argv[4])

# the call to the function above
input_file_volume = computeVolume(input_file, ref_level)

# print the computed mesh volume (truncate the result to three decimals)
print('Volume is: ' + str('{:.3f}'.format(input_file_volume)))
