import numpy as np
import matplotlib.pyplot as plt

x= np.linspace(0, 1, 1000)

plt.plot([], [])
ax = plt.gca()



ax.plot(x, np.arctan(x))

plt.legend()
plt.show()