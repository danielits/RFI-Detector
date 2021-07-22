import matplotlib
import numexpr
import math
import pandas as pd
import time
from matplotlib import patches as pat
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import Tkinter as tk
from matplotlib import animation
from detector_parameters import *
import calandigital as cd

matplotlib.use("TkAgg")

root = tk.Tk()
root.configure(bg='white')

fig = Figure(figsize=(16, 8), dpi=120)
fig.set_tight_layout('True')
ax1 = fig.add_subplot(421)
ax2 = fig.add_subplot(422)
ax3 = fig.add_subplot(423)
ax4 = fig.add_subplot(424)
ax5 = fig.add_subplot(425)
ax6 = fig.add_subplot(426)
ax7 = fig.add_subplot(427)
axes = [ax1, ax2, ax3, ax4, ax5, ax6, ax7]
titles = ["Primary signal",
          "Reference signal",
          "Cross-Power Spectral Density",
          "Power Spectral Density Multiplied",
          "Channel scores",
          "Channel scores sum",
          "Score derivative"]
lines = []
lines_full = []
t = []
scoresum = []
score_der_last = np.zeros(nchannels - 1)

config = 'data/cfg3_'
filenames = ['specdata1.txt', 'specdata2.txt', 'specdata_sl1.txt', 'specdata_sl2.txt', 'numdata.txt',
             'denomdata.txt', 'scoredata.txt', 'timedata.txt']
files = []
for name in filenames:
    files.append(open(config+name))

# Define plots patches
patches = []
for i in range(0, 4):
    patches.append(pat.Rectangle((0, 0), 1200, 0, alpha=0.1, facecolor='red'))
    axes[i].add_patch(patches[i])

# Define plots lines
for ax in axes[:4]:
    line, = ax.plot([], [], 'r', lw=0.7, label='full bits')
    lines_full.append(line)
for ax in axes:
    line, = ax.plot([], [], 'c', lw=1.3, label='sliced')
    lines.append(line)
    if ax != ax5 and ax != ax6 and ax != ax3 and ax != ax7:
        ax.legend()

# Place canvas of plots and toolbar
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


def init():
    # Initialize plots
    for ax, title in zip(axes, titles):
        ax.set_xlim(1200, bandwidth + 1200)
        ax.set_ylim(-dBFS - 2, 0)
        ax.set_xlabel('Frequency (MHz)')
        ax.set_ylabel('Power (dBFS)')
        ax.set_title(title)
        ax.grid()
    ax5.set_ylim(-0.2, 1.2)
    ax5.set_ylabel('Score')
    ax6.set_xlim(0, 30)
    ax6.set_xlabel('Time (s)')
    ax6.set_ylim(-100, nchannels + 100)
    ax6.set_ylabel('Sum score')
    ax7.set_ylim(-1.2, 1.2)
    ax7.set_ylabel('Score derivative')
    return lines

def run(i):
    # Get data
    data = []
    for file in files:
        temp = np.asarray(file.readline()[:-2].split(' '), dtype=float)
        data.append(temp)
    specdata1 = data[0]
    specdata2 = data[1]
    specdata_sl1 = data[2]
    specdata_sl2 = data[3]
    numdata = data[4]
    denomdata = data[5]
    scoredata = data[6]
    print scoredata

    # Moments calculations


    # Score derivative
    global score_der_last
    score_der = scoredata - score_der_last
    score_der_last = scoredata

    # Normalize data by acc_len and convert to dBFS
    specdata1db = cd.scale_and_dBFS_specdata(specdata1, acc_len, dBFS)
    specdata2db = cd.scale_and_dBFS_specdata(specdata2, acc_len, dBFS)
    specdata_sl1db = cd.scale_and_dBFS_specdata(specdata_sl1, acc_len, dBFS)
    specdata_sl2db = cd.scale_and_dBFS_specdata(specdata_sl2, acc_len, dBFS)
    numdatadb = cd.scale_and_dBFS_specdata(numdata, acc_len, dBFS)
    denomdatadb = cd.scale_and_dBFS_specdata(denomdata, acc_len, dBFS)

    # Power Spectral Density full bits, the product and squared root are calculated in python
    multdatadb = [(specdata1db[j] + specdata2db[j]) / 2 for j in range(len(specdata1db))]

    # Add last score sum and time data
    t.append(time.time() - time_start)
    scoresum.append(np.sum(scoredata))

    # Update fig lines
    lines[0].set_data(freqs, specdata_sl1db)
    lines[1].set_data(freqs, specdata_sl2db)
    lines[2].set_data(freqs, numdatadb)
    lines[3].set_data(freqs, denomdatadb)
    lines[4].set_data(freqs, scoredata)
    lines[5].set_data(t, scoresum)
    lines[6].set_data(freqs, score_der)
    lines_full[0].set_data(freqs, specdata1db)
    lines_full[1].set_data(freqs, specdata2db)
    lines_full[3].set_data(freqs, multdatadb)

    # Update x-limits of plots  with time to see the last 30 seconds
    if t[-1] > 30:
        ax6.set_xlim(t[-1] - 30, t[-1])

    # Update rectangle patches
    pow_factor = pwr_sliced_bits - detector_gain
    for i in range(0, len(patches)):
        if i < 2:
            y0 = 10 * np.log10(2 ** (pow_factor - np.log2(acc_len))) - dBFS
            height = 10 * np.log10(2 ** 18)
        else:
            y0 = 10 * np.log10(2 ** (pow_factor + 2 - np.log2(acc_len))) - dBFS
            height = 10 * np.log10(2 ** 16)

        patches[i].set_y(y0)
        patches[i].set_height(height)
    return lines


time_start = time.time()
ani = animation.FuncAnimation(fig, run, interval=10, init_func=init)
root.mainloop()
