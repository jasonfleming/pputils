#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 check_dependencies.py                 # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Nov 21, 2016
#
# Purpose: Checks if numpy, scipy and matplotlib dependencies are 
# installed on the system. If they are, their version is printed. 
#
# Uses: Python 2 or 3
#
# Example:
#
# python check_dependencies.py
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sys

try:
	import numpy as np
	print('Numpy version: ' + str(np.__version__))
except:
	print('Numpy not installed. Exiting.')
	sys.exit(0)

try:
	import scipy as sp
	print('Scipy version: ' + str(sp.__version__))
except:
	print('Scipy not installed. Exiting.')
	sys.exit(0)
	
try:
	import matplotlib as mpl
	print('Matplotlib version: ' + str(mpl.__version__))
except:
	print('Matplotlib not installed. Exiting.')
	sys.exit(0)	

