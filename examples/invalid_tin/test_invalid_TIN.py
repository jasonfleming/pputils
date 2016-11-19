#import ppmodules.readMesh as pp
import matplotlib.tri as mtri
import numpy as np

# reads an existing triangulation from a file
#n,e,x,y,z,ikle = pp.readAdcirc('zero_area_element.grd')

# manually construct an invalid triangulation
x = np.array([0.0, 1.0, 1.0, 1.0, 2.0])
y = np.array([1.0, 0.0, 2.0, 1.0, 1.0])
z = np.zeros(5)

triangles = np.array( [[0, 1, 2], [1, 3, 2], [1, 4, 2], [0, 4, 1]])

# create a Matplotlib Triangulation
triang = mtri.Triangulation(x,y,triangles)

# to perform the linear interpolation
interpolator = mtri.LinearTriInterpolator(triang, z)
m_z = interpolator(1.0, 1.0)
