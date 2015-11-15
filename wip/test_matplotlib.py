import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

x = np.linspace(-6, 6, 1024)
plt.figure(figsize=(8,5))
plt.xlim(-6,6)
plt.ylim(-.5, 1.5)
plt.title('Some plot titlegoes here')
plt.xlabel('distance [m]')
plt.ylabel('value [m2]')
plt.text(0,1,'some text label here')
plt.plot(x, np.sinc(x), c = 'b', lw = 2, label = 'x-val')
plt.plot(x, np.sinc(x*1.1), c = 'g', lw = 1.5, marker='o', markevery=20, label = 'y-val')
plt.legend()

ax = plt.axes()
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.5))

ax.yaxis.set_major_locator(ticker.MultipleLocator(0.25))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.125))

plt.grid(True, which='both')

plt.savefig('test_figure.png', c = 'k')
plt.show()
