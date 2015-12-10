from scipy.interpolate import griddata
import numpy as np
import matplotlib.pyplot as plt

# this is the original xyz data
x=np.linspace(1.,10.,20)
y=np.linspace(1.,10.,20)
z=z = np.random.random(20)

# this is the output grid
xi=np.linspace(1.,10.,10)
yi=np.linspace(1.,10.,10)
X,Y= np.meshgrid(xi,yi)

# interpolate the z
Z = griddata((x, y), z, (X, Y),method='linear', fill_value=-999.0)

plt.contourf(X,Y,Z)
plt.show()
