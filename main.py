import matplotlib
import struct

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
# roach = cd.initialize_roach('192.168.1.12')
roach.write_int(acc_len_reg, acc_len)
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
ax6 = fig.add_subplot(325)
axes = [ax1, ax2, ax3, ax4, ax6]
titles = ["Primary signal",
          "Reference signal",
          "Cross-correlation magnitude after integration",
          "CPSD magnitude before integration (same as multiplied density power)",
          "Score bin"
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


toggle_button.config(command=adquisition_toggle)
toggle_button.pack(side=tk.LEFT)
score_label = tk.Label(button_frame, text="Hola", bg="white")
score_label.pack(side=tk.LEFT)

for ax in axes:
    line, = ax.plot([], [], 'c', lw=1.3)
    lines.append(line)
# lineDet = ax5.vlines([], 0, tempMax, 'r', lw=1.3)
lines[4], = ax6.plot([], [], 'r', lw=1.3)
lineScore, = ax6.plot([], [], 'c', lw=1.3)

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
    # ax5.set_xlabel('Time')
    # ax5.set_ylabel('Score')
    # ax5.set_ylim(0, tempMax)
    # ax5.set_xlim(0, 600)
    ax6.set_ylabel('Score')
    ax6.set_ylim(-0.2, 1.2)
    return lines


def run(i):
    # Get spectrometers data
    specdata1 = cd.read_interleave_data(roach, specbrams_list[0], spec_addr_width, spec_word_width, spec_data_type)
    specdata2 = cd.read_interleave_data(roach, specbrams_list[1], spec_addr_width, spec_word_width, spec_data_type)
    specdata1 = np.delete(specdata1, len(specdata1) / 2)
    specdata2 = np.delete(specdata2, len(specdata2) / 2)

    crossdata = cd.read_interleave_data(roach, crossbrams_list, spec_addr_width, spec_word_width, spec_data_type)
    crossdata = crossdata / 2 #  Creo que agrego un bit mas en la parte decimal de cmult del modelo, revisar
    powsdata = cd.read_interleave_data(roach, pows_list, spec_addr_width, spec_word_width, spec_data_type)
    crossdata = np.delete(crossdata, len(crossdata) / 2)
    powsdata = np.delete(powsdata, len(powsdata) / 2)

    vartemp = 30
    crossdata = np.trunc(crossdata / 2 ** vartemp ) * 2 ** vartemp
    powsdata = np.trunc(powsdata / 2 ** vartemp) * 2 ** vartemp

    crossdata = crossdata * (2 ** 10)
    powsdata = powsdata * (2 ** 10)

    scoretemp = cd.read_interleave_data(roach, score_list, spec_addr_width, spec_word_width, spec_data_type)
    scoretemp = (np.delete(scoretemp, len(scoretemp) / 2)) / 2 ** 29

    # # Get cross-correlation and **power multiplied data**
    # crossdata = []
    # for bram in crossbrams_list:
    #     bramdata = struct.unpack('>256Q', roach.read(bram, 2 ** speccross_addr_width * speccross_word_width / 8))
    #     for j in np.arange(0, 256, 2):
    #         aux = (bramdata[j] << 64) + bramdata[j + 1]
    #         crossdata.append(aux)
    # crossdata = np.resize(crossdata, (len(crossbrams_list), len(crossdata) / len(crossbrams_list)))
    # crossdata = np.vstack(crossdata).reshape((-1,), order='F')
    # crossdata = [crossdata[j]/2 for j in range(len(crossdata))] #Revisar el divido 2, por que es necesario
    # crossdata = np.delete(crossdata, len(crossdata) / 2)
    #
    # # Get principal and reference power spectral density multiplication
    # powsdata = []
    # for bram in pows_list:
    #     bramdata = struct.unpack('>256Q', roach.read(bram, 2 ** speccross_addr_width * speccross_word_width / 8))
    #     for j in np.arange(0, 256, 2):
    #         aux = (bramdata[j] << 64) + bramdata[j + 1]
    #         powsdata.append(aux)
    # powsdata = np.resize(powsdata, (len(crossbrams_list), len(powsdata) / len(crossbrams_list)))
    # powsdata = np.vstack(powsdata).reshape((-1,), order='F')
    # powsdata = np.delete(powsdata, len(powsdata) / 2)

    scoredata = 1.0 * crossdata / powsdata
    score_label.configure(text="Score: " + str(np.max(scoredata))) # Update score label text value

    specdata1db = cd.scale_and_dBFS_specdata(specdata1, acc_len, dBFS)
    specdata2db = cd.scale_and_dBFS_specdata(specdata2, acc_len, dBFS)
    multdatadb = [(specdata1db[j] + specdata2db[j]) / 2 for j in range(len(specdata1db))]
    crossdatadb = cd.scale_and_dBFS_specdata(np.sqrt(np.asarray(crossdata, dtype=float)), acc_len, dBFS)
    powsdatadb = cd.scale_and_dBFS_specdata(np.sqrt(np.asarray(powsdata, dtype=float)), acc_len, dBFS)

    roach.write_int(adq_trigger_reg, 1)
    roach.write_int(adq_trigger_reg, 0)

    # Update fig lines
    lines[0].set_data(freqs, specdata1db)
    lines[1].set_data(freqs, specdata2db)
    lines[2].set_data(freqs, crossdatadb)
    lines[3].set_data(freqs, powsdatadb)
    # lines[4].set_data(t, scoredata)
    lineScore.set_data(freqs, scoretemp)
    lines[4].set_data(freqs, scoredata)

    k = 0
    for i in scoretemp:

        if i >0.1:
            k+=1

    print k

    # lineDet.set_segments(detdata)

    return lines


ani = animation.FuncAnimation(fig, run, interval=10, init_func=init)
root.mainloop()
