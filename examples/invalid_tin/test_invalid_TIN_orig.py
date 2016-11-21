
# +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
import matplotlib.tri as mtri
import numpy as np

# manually construct an invalid triangulation having a zero area element
x = np.array([0.0, 1.0, 1.0, 1.0, 2.0])
y = np.array([1.0, 0.0, 2.0, 1.0, 1.0])
z = np.zeros(5)

triangles = np.array( [[0, 1, 2], [1, 3, 2], [1, 4, 2], [0, 4, 1]])

# create a Matplotlib Triangulation
triang = mtri.Triangulation(x,y,triangles)

# ---------- start of new code ----------
xy = np.dstack((triang.x[triang.triangles], triang.y[triang.triangles]))  # shape (ntri,3,2)
twice_area = np.cross(xy[:,1,:] - xy[:,0,:], xy[:,2,:] - xy[:,0,:])  # shape (ntri)
mask = twice_area < 1e-10  # shape (ntri)

if np.any(mask):
    triang.set_mask(mask)
# ---------- end of new code ----------

# to perform the linear interpolation
interpolator = mtri.LinearTriInterpolator(triang, z)
m_z = interpolator(1.0, 1.0)
