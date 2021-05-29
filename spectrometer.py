import matplotlib
import struct

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import Tkinter as tk
from matplotlib import animation
from spec_parameters import *
import calandigital as cd
import math

matplotlib.use("TkAgg")

roach = cd.initialize_roach(roach_ip, boffile=boffile, upload=True)
# roach = cd.initialize_roach('192.168.1.12')
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
ax1 = fig.add_subplot(311)
ax2 = fig.add_subplot(312)
ax3 = fig.add_subplot(313)
axes = [ax1, ax2, ax3]
titles = ["Signal full bits",
          "Signal 16 bits",
          "Difference between signals"
          ]
lines = []
scoredata = []
detdata = []
t = []

button_frame = tk.Frame(master=root, bg="white")
button_frame.pack(side=tk.TOP, anchor="w")  # ver si se tiene que quedar o no
toggle_button = tk.Button(button_frame, text="Update data")


def adquisition_toggle():
    roach.write_int(adq_trigger_reg, 1)
    roach.write_int(adq_trigger_reg, 0)


toggle_button.config(command=lambda: update_detector_gain())
toggle_button.pack(side=tk.LEFT)
score_label = tk.Label(button_frame, text=detector_gain, bg="white")
score_label.pack(side=tk.LEFT)

for ax in axes:
    line, = ax.plot([], [], 'c', lw=1.3)
    lines.append(line)

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
    ax3.set_ylim(-2, 20)
    return lines


def run(i):
    # Get spectrometers data
    specdata1 = cd.read_interleave_data(roach, specbrams_list[0], spec_addr_width, spec_word_width, spec_data_type)
    specdata2 = cd.read_interleave_data(roach, specbrams_list[1], spec_addr_width, spec_word_width, spec_data_type) * ((2 ** 28)/detector_gain)
    specdata1 = np.delete(specdata1, len(specdata1) / 2)
    specdata2 = np.delete(specdata2, len(specdata2) / 2)

    specdata1db = cd.scale_and_dBFS_specdata(specdata1, acc_len, dBFS)
    specdata2db = cd.scale_and_dBFS_specdata(specdata2, acc_len, dBFS)

    adquisition_toggle()

    # Update fig lines
    lines[0].set_data(freqs, specdata1db)
    lines[1].set_data(freqs, specdata2db)
    lines[2].set_data(freqs, (specdata1 - specdata2) / 2 ** 16)

    return lines


ani = animation.FuncAnimation(fig, run, interval=10, init_func=init)
root.mainloop()
