import numpy as np
import matplotlib.pyplot as plt

# Parameters
A = 10  # Amplitude
freq = 300  # Signal frequency (Mhz)
phi = np.pi / 3  # Offset angle
lenData = 2 ** 13
snr = 5000  # dB
fm = 1080  # Sampling rate (Mhz)
mean_noise = 0

# Define time series and inputs
t = np.flip(np.linspace(lenData / fm, 0, lenData, endpoint=False))
x1 = A * np.cos(2 * np.pi * t * freq)
x2 = A * np.cos(2 * np.pi * t * freq + phi)

# Add noise to inputs
p1 = np.mean(np.abs(x1) ** 2)
sigma_noise = np.sqrt(10 ** (np.log10(p1) - snr / 10))
noise1 = np.random.normal(mean_noise, sigma_noise, lenData)
noise2 = np.random.normal(mean_noise, sigma_noise, lenData)
x1 = x1 + noise1
x2 = x2 + noise2

# FFT and frequency arrays
f = np.fft.rfftfreq(lenData, d=1/fm)
X1 = np.fft.rfft(x1)
X2 = np.fft.rfft(x2)

# Power and cross-correlation
P1 = np.real(X1 * np.conj(X1))
P2 = np.real(X2 * np.conj(X2))
PSD1 = P1 / lenData ** 2
PSD2 = P2 / lenData ** 2
crosscor = X1 * np.conj(X2) / lenData ** 2

# Plot signal 1
plt.subplot(3, 2, 1)
plt.plot(f, PSD1)
plt.title("Main Signal PSD")
plt.xlabel("Frequency (Mhz)")
plt.ylabel("Power (dB)")
plt.yscale('log')

# Plot signal 2
plt.subplot(3, 2, 2)
plt.plot(f, PSD2)
plt.title("Reference Signal PSD")
plt.xlabel("Frequency (Mhz)")
plt.ylabel("Power (dB)")
plt.yscale('log')

# Plot signal 1
plt.subplot(3, 2, 3)
plt.plot(f, np.abs(crosscor))
plt.title("CPSD")
plt.xlabel("Frequency (Mhz)")
plt.ylabel("Power (dB)")
plt.yscale('log')

print("Signal 1 Power")
print("     -Theoretical value: " + str(A ** 2 / 2 + sigma_noise ** 2))
print("     -Time density integration: " + str(np.mean(x1 ** 2)))
print("     -Frequency density integration: " + str(2 * np.sum(np.abs(X1) ** 2) / lenData ** 2))

print(crosscor)

plt.tight_layout()
plt.show()
