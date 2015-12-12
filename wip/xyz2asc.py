from scipy.interpolate import griddata
import numpy as np
import matplotlib.pyplot as plt
import struct

# this is the original xyz data
x=np.linspace(1.,10.,20)
y=np.linspace(1.,10.,20)
z=z = np.random.random(20)

# this is the output grid
xi=np.linspace(1.,10.,10)
yi=np.linspace(1.,10.,10)
X,Y= np.meshgrid(xi,yi)

# interpolate the z
# based on the above, Z is a 10x10 numpy array
Z = griddata((x, y), z, (X, Y),method='nearest', fill_value=-999.0)

# Z write to a binary file
f = open('file.flt', 'wb')
for i in range(len(xi)):
	#for j in range(len(yi)):
	s = struct.pack('f'*len(yi), *Z[i,:])
	f.write(s)
f.close()

'''
for i in range(len(xi)):
	for j in range(len(yi)):
		s = struct.pack('f', Z[i,j])
		f.write(s)
f.close()
'''

plt.contourf(X,Y,Z)
plt.show()
