import numpy as np
import matplotlib.pyplot as plt

# Parameters
A = 10  # Amplitude
freq = 300  # Signal frequency (Mhz)
phi = np.pi / 3  # Offset angle
dataLen = 2 ** 13
accLen = 2 ** 5
snr = 0  # dB
fm = 1080  # Sampling rate (Mhz)
mean_noise = 0

# Define time series and inputs
t = np.flip(np.linspace(dataLen / fm, 0, dataLen, endpoint=False))
x1 = A * np.cos(2 * np.pi * t * freq)
x2 = A * np.cos(2 * np.pi * t * freq + phi)

# Add noise to inputs
p1 = np.mean(np.abs(x1) ** 2)
sigma_noise = np.sqrt(10 ** (np.log10(p1) - snr / 10))
noise1 = np.random.normal(mean_noise, sigma_noise, dataLen)
noise2 = np.random.normal(mean_noise, sigma_noise, dataLen)
x1 = x1 + noise1
x2 = x2 + noise2

# FFT and frequency arrays
f = np.fft.rfftfreq(dataLen, d=1 / fm)
X1 = np.fft.rfft(x1)
X2 = np.fft.rfft(x2)

# Power and cross-correlation
P1 = np.real(X1 * np.conj(X1))
P2 = np.real(X2 * np.conj(X2))
PSD1 = P1 / dataLen ** 2
PSD2 = P2 / dataLen ** 2
crosscor = X1 * np.conj(X2) / dataLen ** 2

# Plot Spectrometer Main Signal
plt.subplot(3, 2, 1)
plt.plot(f, PSD1)
plt.title("Main Signal PSD")
plt.xlabel("Frequency (Mhz)")
plt.ylabel("Power (dB)")
plt.yscale("log")

# Plot Spectrometer Reference Signal
plt.subplot(3, 2, 2)
plt.plot(f, PSD2)
plt.title("Reference Signal PSD")
plt.xlabel("Frequency (Mhz)")
plt.ylabel("Power (dB)")
plt.yscale("log")

# Plot Module CPSD
plt.subplot(3, 2, 3)
plt.plot(f, np.abs(crosscor))
plt.title("CPSD")
plt.xlabel("Frequency (Mhz)")
plt.ylabel("Power (dB)")
plt.yscale("log")

print("Power Main Signal")
print("     -Theoretical value: " + str(A ** 2 / 2 + sigma_noise ** 2))
print("     -Time density integration: " + str(np.mean(x1 ** 2)))
print("     -Frequency density integration: " + str(2 * np.sum(PSD1)))

plt.tight_layout()
plt.show()
