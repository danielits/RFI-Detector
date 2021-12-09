import numpy as np
import matplotlib.pyplot as plt
from detector_parameters import *
import calandigital as cd

ind = 153
specdata = np.loadtxt('data/cfg3_specdata_sl1.txt', skiprows=ind, max_rows=1)
freqs = np.linspace(0, bandwidth, nchannels, endpoint=False)  # MHz
freqs = np.delete(freqs, len(freqs) / 2)
freqs = [x + 1200 for x in freqs]
specdata = cd.scale_and_dBFS_specdata(specdata, acc_len, dBFS)
fig2, ax = plt.subplots()
fig2.set_tight_layout('True')
ax.plot(freqs, specdata)
ax.set_xlim(1200, 1800)
ax.set_ylim(-dBFS - 2, 0)
ax.set_xlabel('Frequency (MHz)')
ax.set_ylabel('Power (dBFS)')
ax.set_title('Main PSD')
ax.grid()
plt.axvspan(1240, 1300, facecolor='royalblue', alpha=0.5, label='navigation')
plt.axvspan(1300, 1350, facecolor='m', alpha=0.5, label='aeronautics')
plt.axvspan(1350, 1400, facecolor='palegreen', alpha=0.5, label='radiolocation')
plt.axvspan(1429, 1452, facecolor='gold', alpha=0.5, label='fix')
plt.axvspan(1452, 1492, facecolor='darksalmon', alpha=0.5, label='satellite radio')
plt.axvspan(1492, 1518, facecolor='gold', alpha=0.5) #radio satelital
plt.axvspan(1518, 1525, facecolor='r', alpha=0.5, label='satellite mobile')
plt.axvspan(1530, 1559, facecolor='r', alpha=0.5)
plt.axvspan(1559, 1660, facecolor='royalblue', alpha=0.5)

plt.legend()
plt.show()