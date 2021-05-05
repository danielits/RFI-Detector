import numpy as np
import matplotlib.pyplot as plt

# Parameters
A = 10  # Amplitude
freq = 300  # Signal frequency (Mhz)
phi = np.pi / 3  # Offset angle
dataLen = 2 ** 12  # Size data
accLen = 2 ** 10  # Integration length
snr = 20  # SNR (dB)
fm = 1080.0  # Sampling rate (Mhz)

# Define time series and initialize
t = np.flip(np.linspace(dataLen / fm, 0, dataLen, endpoint=False), 0)
PSD1 = []
PSD2 = []
CPSD = []

# Add noise to inputs
for i in range(0, accLen):
    x1 = A * np.cos(2 * np.pi * t * freq)
    x2 = A * np.cos(2 * np.pi * t * freq + phi)
    # x2 = 0
    p1 = np.mean(np.abs(x1) ** 2)
    sigma_noise = np.sqrt(10 ** (np.log10(p1) - snr / 10))
    noise1 = np.random.normal(0, sigma_noise, dataLen)
    noise2 = np.random.normal(0, sigma_noise, dataLen)
    x1 = x1 + noise1
    x2 = x2 + noise2

    # FFT and frequency arrays
    f = np.fft.rfftfreq(dataLen, d=1 / fm)
    X1 = np.fft.rfft(x1)
    X2 = np.fft.rfft(x2)

    # Power and cross-correlation
    P1 = np.real(X1 * np.conj(X1))
    P2 = np.real(X2 * np.conj(X2))
    crosscor = X1 * np.conj(X2)
    PSD1 = np.append(PSD1, P1 / dataLen ** 2)
    PSD2 = np.append(PSD2, P2 / dataLen ** 2)
    CPSD = np.append(CPSD, crosscor / dataLen ** 2)

PSD1 = np.reshape(PSD1, (accLen, len(f)))
PSD2 = np.reshape(PSD2, (accLen, len(f)))
CPSD = np.reshape(CPSD, (accLen, len(f)))
PSD1mean = np.mean(PSD1, 0)
PSD2mean = np.mean(PSD2, 0)
CPSDmean = np.mean(CPSD, 0)

ylim = ((-80, 20))

# Plot signal 1 PSD
c = 10 * np.log10(PSD1[-1])
plt.subplot(3, 2, 1)
plt.plot(f, c)
plt.title("Main signal PSD")
plt.xlabel("Frequency (Mhz)")
plt.ylabel("Power (dB)")
plt.ylim(ylim)
plt.xlim((0, fm / 2))

# Plot signal 2 PSD
d = 10 * np.log10(PSD2[-1])
plt.subplot(3, 2, 2)
plt.plot(f, d)
plt.title("Reference signal PSD")
plt.xlabel("Frequency (Mhz)")
plt.ylabel("Power (dB)")
plt.ylim(ylim)
plt.xlim((0, fm / 2))

# Plot instantaneous CPSD
a = 10 * np.log10(np.abs(CPSD[-1]))
plt.subplot(3, 1, 2)
plt.plot(f, a)
plt.title("CPSD without integration")
plt.xlabel("Frequency (Mhz)")
plt.ylabel("Power (dB)")
plt.ylim(ylim)
plt.xlim((0, fm / 2))

# Plot integrated CPSD module
b = 10 * np.log10(np.abs(CPSDmean))
plt.subplot(3, 2, 5)
plt.plot(f, b)
plt.title("CPSD module after integration")
plt.xlabel("Frequency (Mhz)")
plt.ylabel("Power (dB)")
plt.ylim(ylim)
plt.xlim((0, fm / 2))

# Plot CPSD integrated power
e = 10 * np.log10(np.mean(np.abs(CPSD), 0))
plt.subplot(3, 2, 6)
plt.plot(f, e)
plt.title("CPSD module before integration")
plt.xlabel("Frequency (Mhz)")
plt.ylabel("Power (dB)")
plt.ylim(ylim)
plt.xlim((0, fm / 2))

print("Signal 1 Power")
print("     -Theoretical value: " + str(A ** 2 / 2 + sigma_noise ** 2))
print("     -Time density integration: " + str(np.mean(x1 ** 2)))
print("     -Frequency density integration: " + str(2 * np.sum(np.abs(X1) ** 2) / dataLen ** 2))

plt.gcf().suptitle("Integration size: " + str(accLen))
plt.gcf().set_size_inches(14.5, 7.5)
plt.tight_layout()
plt.show()
