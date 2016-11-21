#import ppmodules.readMesh as pp
import matplotlib.tri as mtri
import numpy as np
import matplotlib.pyplot as plt

# reads an existing triangulation from a file
#n,e,x,y,z,ikle = pp.readAdcirc('zero_area_element.grd')

# manually construct an invalid triangulation
x = np.array([0.0, 1.0, 1.0, 1.0, 2.0])
y = np.array([1.0, 0.0, 2.0, 1.0, 1.0])
z = np.zeros(5)

# slightly modified from what I originally posted on Matplotlib's mailing list
triangles = np.array( [[0, 1, 4], [2, 3, 4], [0, 3, 2], [0, 3, 4]])

# create a Matplotlib Triangulation
triang = mtri.Triangulation(x,y,triangles)

# ---------- start of new code ----------
xy = np.dstack((triang.x[triang.triangles], triang.y[triang.triangles])) #shape (ntri,3,2)
twice_area = np.cross(xy[:,1,:] - xy[:,0,:], xy[:,2,:] - xy[:,0,:])  # shape (ntri)
mask = twice_area < 1e-10  # shape (ntri)

if np.any(mask):
	triang.set_mask(mask)
# ---------- end of new code ----------

print(mask)

# to perform the linear interpolation
interpolator = mtri.LinearTriInterpolator(triang, z)
m_z = interpolator(1.0, 1.0)
print(m_z)

plt.figure()
plt.gca().set_aspect('equal')
plt.triplot(triang, color='black')
plt.show()
