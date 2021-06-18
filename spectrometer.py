import matplotlib
import numexpr
import struct

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import Tkinter as tk
from matplotlib import animation
from matplotlib import patches
from spec_parameters import *
import calandigital as cd
import math

matplotlib.use("TkAgg")

roach = cd.initialize_roach(roach_ip, boffile=boffile, upload=True)
# roach = cd.initialize_roach('192.168.1.12')
roach.write_int(acc_len_reg, acc_len)
#roach.write_int(detector_gain_reg, detector_gain)
roach.write_int(cnt_rst_reg, 1)
roach.write_int(cnt_rst_reg, 0)

root = tk.Tk()
root.configure(bg='white')
fig = Figure(figsize=(16, 8), dpi=120)
fig.set_tight_layout('True')
ax1 = fig.add_subplot(311)
ax2 = fig.add_subplot(312)
axes = [ax1, ax2]
titles = ["Signal full bits",
          "Signal 18 bits"
          ]
lines = []
scoredata = []
detdata = []
t = []


def add_reg_entry(roach, root, reg):
    # add frame
    frame = tk.Frame(master=root, bg="white")
    frame.pack(side=tk.TOP, anchor="w")
    # add label
    label = tk.Label(frame, text=reg + ":", bg="white")
    label.pack(side=tk.LEFT)
    # add entry
    entry = tk.Entry(frame, bg="white")
    entry.insert(tk.END, roach.read_uint(reg))
    entry.pack(side=tk.LEFT)
    button_double = tk.Button(frame, text='x2', command=lambda: reg_double(), bg="white")
    button_double.pack(side=tk.LEFT)
    button_half = tk.Button(frame, text='/2', command=lambda: reg_half(), bg="white")
    button_half.pack(side=tk.LEFT)
    button_add = tk.Button(frame, text='+1', command=lambda: reg_add(), bg="white")
    button_add.pack(side=tk.LEFT)
    button_sub = tk.Button(frame, text='-1', command=lambda: reg_subtract(), bg="white")
    button_sub.pack(side=tk.LEFT)

    def reg_double():
        val = int(numexpr.evaluate(entry.get())) * 2
        entry.delete(0, "end")
        entry.insert(0, val)
        roach.write_int(reg, val)
        roach.write_int(cnt_rst_reg, 1)
        roach.write_int(cnt_rst_reg, 0)

    def reg_half():
        val = int(numexpr.evaluate(entry.get())) / 2
        entry.delete(0, "end")
        entry.insert(0, val)
        roach.write_int(reg, val)
        roach.write_int(cnt_rst_reg, 1)
        roach.write_int(cnt_rst_reg, 0)

    def reg_add():
        val = int(numexpr.evaluate(entry.get())) + 1
        entry.delete(0, "end")
        entry.insert(0, val)
        roach.write_int(reg, val)
        roach.write_int(cnt_rst_reg, 1)
        roach.write_int(cnt_rst_reg, 0)

    def reg_subtract():
        val = int(numexpr.evaluate(entry.get())) - 1
        entry.delete(0, "end")
        entry.insert(0, val)
        roach.write_int(reg, val)
        roach.write_int(cnt_rst_reg, 1)
        roach.write_int(cnt_rst_reg, 0)


add_reg_entry(roach, root, acc_len_reg)
#add_reg_entry(roach, root, detector_gain_reg)

for ax in axes:
    line, = ax.plot([], [], 'c', lw=1.3)
    lines.append(line)

patch = patches.Rectangle((0, 0), 1200, 0, alpha=0.1, facecolor='red')
ax2.add_patch(patch)


canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

def init():
    # Initialize axes parameters
    for ax, title in zip(axes, titles):
        ax.set_xlim(0, bandwidth)
        ax.set_ylim(-dBFS - 2, 0)
        ax.set_xlabel('Frequency (MHz)')
        ax.set_ylabel('Power (dBFS)')
        ax.set_title(title)
        ax.grid()
    return lines


def run(i):
    # Update values from register
    acc_len = roach.read_uint(acc_len_reg)
    #detector_gain = roach.read_uint(detector_gain_reg)

    # Spectrometer data
    pow_factor = pwr_sliced_bits - detector_gain
    specdata1 = cd.read_interleave_data(roach, specbrams_list[0], spec_addr_width, spec_word_width, spec_data_type)
    #specdata2 = (cd.read_interleave_data(roach, specbrams_list[1], score_addr_width, score_word_width,
     #                                    score_data_type)) * (2 ** (pow_factor))
    specdata1 = np.delete(specdata1, len(specdata1) / 2)
    #specdata2 = np.delete(specdata2, len(specdata2) / 2)
    specdata1db = cd.scale_and_dBFS_specdata(specdata1, acc_len, dBFS)
    #specdata2db = cd.scale_and_dBFS_specdata(specdata2, acc_len, dBFS)

    # Update fig lines
    lines[0].set_data(freqs, specdata1db)
   # lines[1].set_data(freqs, specdata2db)

    # Update rectangle patch
    y0 = 10 * np.log10(2 ** (pow_factor - np.log2(acc_len))) - dBFS
    height = 10 * np.log10(2 ** 18)
    patch.set_y(y0)
    patch.set_height(height)

    return lines


ani = animation.FuncAnimation(fig, run, interval=10, init_func=init)
root.mainloop()
