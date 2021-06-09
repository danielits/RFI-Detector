import matplotlib
import struct
import numexpr
import time

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import Tkinter as tk
from matplotlib import animation
from detector_parameters import *
import calandigital as cd
import math

matplotlib.use("TkAgg")

roach = cd.initialize_roach(roach_ip, boffile=boffile, upload=True)
# roach = cd.initialize_roach(roach_ip)
roach.write_int(acc_len_reg, acc_len)
roach.write_int(detector_gain_reg, detector_gain)
roach.write_int(cnt_rst_reg, 1)
roach.write_int(cnt_rst_reg, 0)
roach.write_int(adq_trigger_reg, 1)
roach.write_int(adq_trigger_reg, 0)

root = tk.Tk()
root.configure(bg='white')
fig = Figure(figsize=(16, 8), dpi=120)
fig.set_tight_layout('True')
ax1 = fig.add_subplot(321)
ax2 = fig.add_subplot(322)
ax3 = fig.add_subplot(323)
ax4 = fig.add_subplot(324)
ax5 = fig.add_subplot(325)
ax6 = fig.add_subplot(326)
axes = [ax1, ax2, ax3, ax4, ax5, ax6]
titles = ["Primary signal",
          "Reference signal",
          "Crosscorr magnitude after integration",
          "Crosscorr magnitude before integration",
          "Channel scores",
          "Channel scores sum"
          ]
lines = []
scoredata = []
detdata = []
t = []
scoresum = []


def add_reg_entry(roach, root, reg):

    # add frame
    frame = tk.Frame(master=root, bg="white")
    frame.pack(side = tk.TOP, anchor="w")
    # add label
    label = tk.Label(frame, text=reg+":", bg="white")
    label.pack(side=tk.LEFT)
    # add entry
    entry = tk.Entry(frame, bg="white")
    entry.insert(tk.END, roach.read_uint(reg))
    entry.pack(side=tk.LEFT)
    button_double = tk.Button(frame, text='x2', command=lambda: double_reg(), bg="white")
    button_double.pack(side=tk.LEFT)
    button_half = tk.Button(frame, text='/2', command=lambda: half_reg(), bg="white")
    button_half.pack(side=tk.LEFT)

    def double_reg():
        val = int(numexpr.evaluate(entry.get())) * 2
        entry.delete(0, "end")
        entry.insert(0, val)
        roach.write_int(reg, val)
        roach.write_int(cnt_rst_reg, 1)
        roach.write_int(cnt_rst_reg, 0)

    def half_reg():
        val = int(numexpr.evaluate(entry.get())) / 2
        entry.delete(0, "end")
        entry.insert(0, val)
        roach.write_int(reg, val)
        roach.write_int(cnt_rst_reg, 1)
        roach.write_int(cnt_rst_reg, 0)

add_reg_entry(roach, root, acc_len_reg)
add_reg_entry(roach, root, detector_gain_reg)


for ax in axes:
    line, = ax.plot([], [], 'c', lw=1.3)
    lines.append(line)
# lineDet = ax5.vlines([], 0, tempMax, 'r', lw=1.3)
lineScore, = ax5.plot([], [], 'c', lw=1.3)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


def init():
    for ax, title in zip(axes, titles):
        ax.set_xlim(0, bandwidth)
        ax.set_ylim(-dBFS - 2, 0)
        ax.set_xlabel('Frequency (MHz)')
        ax.set_ylabel('Power (dBFS)')
        ax.set_title(title)
        ax.grid()
    ax6.set_ylim((0, nchannels))
    ax6.set_xlim(0, 60)
    ax6.set_ylabel('Sum score')
    ax6.set_xlabel('Time (s)')
    ax5.set_ylabel('Score')
    ax5.set_ylim(-0.2, 1.2)
    return lines


def run(i):
    acc_len = roach.read_uint(acc_len_reg)
    detector_gain = roach.read_uint(detector_gain_reg)
    # Get spectrometers data
    specdata1 = cd.read_interleave_data(roach, specbrams_list[0], spec_addr_width, spec_word_width, spec_data_type)
    specdata2 = cd.read_interleave_data(roach, specbrams_list[1], spec_addr_width, spec_word_width, spec_data_type)
    specdata1 = np.delete(specdata1, len(specdata1) / 2)
    specdata2 = np.delete(specdata2, len(specdata2) / 2)

    crossdata = cd.read_interleave_data(roach, crossbrams_list, spec_addr_width, spec_word_width, spec_data_type) * (2 ** 56 / detector_gain ** 2)
    powsdata = cd.read_interleave_data(roach, pows_list, spec_addr_width, spec_word_width, spec_data_type) * (2 ** 56 / detector_gain ** 2)
    scoredata = cd.read_interleave_data(roach, score_list, spec_addr_width, spec_word_width, spec_data_type) / 2 ** 28
    crossdata = np.delete(crossdata, len(crossdata) / 2)
    powsdata = np.delete(powsdata, len(powsdata) / 2)
    scoredata = (np.delete(scoredata, len(scoredata) / 2))

    scorepy = 1.0 * crossdata / powsdata

    specdata1db = cd.scale_and_dBFS_specdata(specdata1, acc_len, dBFS)
    specdata2db = cd.scale_and_dBFS_specdata(specdata2, acc_len, dBFS)
    multdatadb = [(specdata1db[j] + specdata2db[j]) / 2 for j in range(len(specdata1db))]
    crossdatadb = cd.scale_and_dBFS_specdata(np.sqrt(np.asarray(crossdata, dtype=float)), acc_len, dBFS)
    powsdatadb = cd.scale_and_dBFS_specdata(np.sqrt(np.asarray(powsdata, dtype=float)), acc_len, dBFS)

    t.append(time.time() - time_start)
    scoresum.append(np.sum(scoredata))

    roach.write_int(adq_trigger_reg, 1)
    roach.write_int(adq_trigger_reg, 0)

    # Update fig lines
    lines[0].set_data(freqs, specdata1db)
    lines[1].set_data(freqs, specdata2db)
    lines[2].set_data(freqs, crossdatadb)
    lines[3].set_data(freqs, powsdatadb)
    # lineScore.set_data(freqs, scoredata)
    lines[4].set_data(freqs, scoredata)
    lines[5].set_data(t, scoresum)

    if t[-1] > 60:
        ax6.set_xlim(t[-1] - 60, t[-1])
    return lines


time_start = time.time()
ani = animation.FuncAnimation(fig, run, interval=10, init_func=init)
root.mainloop()
