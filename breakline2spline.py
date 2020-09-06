#!/usr/bin/env python3
#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                       breakline2spline.py                             # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Oct 18, 2019
#
# Purpose: Takes in a breakline in PPUTILS format, and creates a cubic
# spline with the target number of points.
#
# Uses: Python 2 or 3, Matplotlib, Numpy, Scipy
#
# Example:
#
# python breakline2spline.py -i centerline.csv -n 100 -o centerline_spline.csv
# where:
# -i river centerline
# -n number of points on the spline
# -o the output spline
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys
import numpy as np
import scipy.interpolate as si
import subprocess
# 
# This method takes a polyline, and converts it to a bezier spline using
# the target number of points, and the set degree

# I got this method from the link below
# https://stackoverflow.com/questions/34803197/fast-b-spline-algorithm-with-numpy-scipy
def scipy_bspline(cv, n=100, degree=3, periodic=False):
  """ Calculate n samples on a bspline

    cv :    Array ov control verticeso
    n  :    Number of samples to return
    degree:   Curve degree
    periodic: True - Curve is closed
  """
  cv = np.asarray(cv)
  count = cv.shape[0]

  # Closed curve
  if periodic:
    kv = np.arange(-degree,count+degree+1)
    factor, fraction = divmod(count+degree+1, count)
    cv = np.roll(np.concatenate((cv,) * factor + (cv[:fraction],)),-1,axis=0)
    degree = np.clip(degree,1,degree)

  # Opened curve
  else:
    degree = np.clip(degree,1,count-1)
    kv = np.clip(np.arange(count+degree+1)-degree,0,count-degree)

  # Return samples
  max_param = count - (degree * (1-periodic))
  spl = si.BSpline(kv, cv, degree)
  return spl(np.linspace(0,max_param,n))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# I/O
if len(sys.argv) != 7 :
  print('Wrong number of Arguments, stopping now...')
  print('Usage:')
  print('python breakline2spline.py -i centerline.csv -n 100 -o centerline_spline.csv')
  sys.exit()

centerline_file = sys.argv[2]
number_centerline_points = int(sys.argv[4])
spline_file = sys.argv[6]

# read the input files
centerline_input = np.loadtxt(centerline_file, delimiter=',',skiprows=0,unpack=True)

# this is the output file
fout = open(spline_file, 'w')

# to fit the spline as a bezier polyline using Scipy

# extract the centerline coordinates
centerline_x = centerline_input[1,:]
centerline_y = centerline_input[2,:]

# put the centerline data to a format required by scipy_bspline()
cv = np.vstack((centerline_x, centerline_y)).transpose()

# carry out the fit
d = 3 # degree of fit
n = number_centerline_points # number of points on the spline read
p = scipy_bspline(cv,n,d,False)

# obtain the coordinates of the fitted centerline spline
centerline_spline_x,centerline_spline_y = p.transpose()

# to write the centerline spline as a pputils lines file, along with its stations
# (i.e., its s-coordinate)

for i in range(len(centerline_spline_x)):
  fout.write('0,' + str(centerline_spline_x[i]) + ',' 
    + str(centerline_spline_y[i]) + ',' + '0' + '\n')
fout.close()

# let's write this spline as a wkt file
# I know using subprocess to do this is bad, but for now it will have to do

# create the name for the wkt file
spline_file_wkt = spline_file.rsplit('.',1)[0] + '_WKT.csv'

subprocess.call ( ['python3', 'breaklines2wkt.py', '-i', spline_file, '-o',
  spline_file_wkt])
