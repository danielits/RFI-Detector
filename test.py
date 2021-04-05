import numpy as np

a = np.random.randint(0, 100, 2**10)
b = np.random.randint(0, 2 * np.pi, 2**10)


real = a * np.cos(b)
imag = a * np.sin(b)

print np.mean(real)
print np.mean(imag)