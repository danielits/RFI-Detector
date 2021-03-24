import matplotlib
import time
import struct
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import Tkinter as tk
import matplotlib.animation as animation
from matplotlib import style, animation
import numpy as np
from detector_parameters import *
import calandigital as cd

roach = cd.initialize_roach(roach_ip, boffile=boffile, upload=True)
#roach = cd.initialize_roach('192.168.1.12')
roach.write_int(acc_len_reg, acc_len)
roach.write_int(cnt_rst_reg, 1)
roach.write_int(cnt_rst_reg, 0)

root = tk.Tk()
fig = Figure(figsize=(16, 8), dpi=120)
fig.set_tight_layout(True)
ax1 = fig.add_subplot(321)
ax2 = fig.add_subplot(322)
ax3 = fig.add_subplot(323)
ax4 = fig.add_subplot(324)
ax5 = fig.add_subplot(313)
axes = [ax1, ax2, ax3, ax4, ax5]
lines = []
scoredata=[]
t=[]

for ax in axes:
    line, = ax.plot([], [],'c', lw=1.3)
    lines.append(line)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

def init():
    titles = ["Main signal", "Referece signal", "Cross-correlation magnitude", "Cross multiplied power",
              "Detector threshold 3 STD over log(score)"]
    for ax, title in zip(axes, titles):
        ax.set_xlim(0, bandwidth)
        ax.set_ylim(-dBFS - 2, 0)
        ax.set_xlabel('Frequency (MHz)')
        ax.set_ylabel('Power (dBFS)')
        ax.set_title(title)
        ax.grid()
    ax5.set_xlabel('Time')
    ax5.set_ylabel('Score')
    ax5.set_ylim(0, 829691120*2)
    ax5.set_xlim(0, 300)
    return lines


def run(i):
    # Get data spectrometers
    specdata1 = cd.read_interleave_data(roach, specbrams_list[0], spec_addr_width, spec_word_width, spec_data_type)
    specdata2 = cd.read_interleave_data(roach, specbrams_list[1], spec_addr_width, spec_word_width, spec_data_type)
    specdata1 = cd.scale_and_dBFS_specdata(specdata1, acc_len, dBFS)
    specdata2 = cd.scale_and_dBFS_specdata(specdata2, acc_len, dBFS)

    # Get cross-correlation and power multiplied data
    multdata = [specdata1[j] + specdata2[j] + 82 for j in range(len(specdata2))]
    crossdata = []
    for bram in speccross_list:
        bramdata = struct.unpack('>256Q', roach.read(bram, 2 ** speccross_addr_width * speccross_word_width / 8))
        for j in np.arange(0, 256, 2):
            aux = (bramdata[j] << 64) + bramdata[j + 1]
            crossdata.append(aux)
    crossdata = np.resize(crossdata, (len(speccross_list), len(crossdata) / len(speccross_list)))
    crossdata = np.vstack(crossdata).reshape((-1,), order='F')
    crossdata = cd.scale_and_dBFS_specdata(crossdata, acc_len, dBFS)

    # Score data
    bramscore = struct.unpack('>1024Q', roach.read(score_name_bram, 2 ** score_addr_width * score_word_width / 8))
    scorelist = []
    for j in np.arange(0, 1024, 2):
        aux = (bramscore[j] << 0) + bramscore[j + 1]
        scorelist.append(aux)
    # print('Score FPGA: ' + str(max(score_data)) +', Score Python: ' + str(np.sum(data)
    score = np.mean(scorelist)
    scoredata.append(score)
    t.append(i)


    # Update fig lines
    lines[0].set_data(freqs, specdata1)
    lines[1].set_data(freqs, specdata2)
    lines[2].set_data(freqs, crossdata)
    lines[3].set_data(freqs, multdata)
    lines[4].set_data(t, scoredata)

    #Updating ax5 horizontal limits
    if i > 300:
        ax5.set_xlim(i-300, i)

    return lines


ani = animation.FuncAnimation(fig, run, interval=10, init_func=init)
root.mainloop()