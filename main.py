import matplotlib
import numexpr
import time
from matplotlib import patches as pat
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import Tkinter as tk
from matplotlib import animation
from detector_parameters import *
import calandigital as cd
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
ax1 = fig.add_subplot(421)
ax2 = fig.add_subplot(422)
ax3 = fig.add_subplot(423)
ax4 = fig.add_subplot(424)
ax5 = fig.add_subplot(425)
ax6 = fig.add_subplot(426)
ax7 = fig.add_subplot(427)
ax8 = fig.add_subplot(428)
axes = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8]
titles = ["Primary signal full bits",
          "Reference signal full bits",
          "Primary signal 18 bits",
          "Reference signal 18 bits",
          "Cross-Power Spectral Density",
          "Power Spectral Density Multiplied",
          "Channel scores",
          "Channel scores sum"
          ]
lines = []
t = []
scoresum = []


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
add_reg_entry(roach, root, detector_gain_reg)

# Define plots lines
linePSDM, = ax6.plot([], [], 'r', lw=1.3, label='full bits')

for ax in axes:
    line, = ax.plot([], [], 'c', lw=1.3)
    lines.append(line)
lines[5].set_label('18 bits')
axes[5].legend()

# Define plots patches
patches = []
for i in range(0,6):
    patches.append(pat.Rectangle((0, 0), 1200, 0, alpha=0.1, facecolor='red'))
    axes[i].add_patch(patches[i])

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
        ax.set_xlim(0, bandwidth)
        ax.set_ylim(-dBFS - 2, 0)
        ax.set_xlabel('Frequency (MHz)')
        ax.set_ylabel('Power (dBFS)')
        ax.set_title(title)
        ax.grid()
    ax7.set_ylim(0, nchannels)
    ax7.set_xlim(0, 60)
    ax7.set_ylabel('Score')
    ax7.set_xlabel('Time (s)')
    ax8.set_ylabel('Sum score')
    ax8.set_ylim(-0.2, 1.2)
    return lines


def run(i):
    # Update registers
    acc_len = roach.read_uint(acc_len_reg)
    detector_gain = roach.read_uint(detector_gain_reg)

    # Get spectrometers data
    specdata1 = cd.read_interleave_data(roach, specs_names[0], spec_addr_width, spec_word_width, spec_data_type)
    specdata2 = cd.read_interleave_data(roach, specs_names[1], spec_addr_width, spec_word_width, spec_data_type)
    specdata1 = np.delete(specdata1, len(specdata1) / 2)
    specdata2 = np.delete(specdata2, len(specdata2) / 2)

    # Get spectrometer sliced data
    pow_factor = pwr_sliced_bits - detector_gain
    specdata_sl1 = cd.read_interleave_data(roach, specs_sl_names[0], score_addr_width, score_word_width,
                                           score_data_type) * (2 ** (pow_factor))
    specdata_sl2 = cd.read_interleave_data(roach, specs_sl_names[1], score_addr_width, score_word_width,
                                           score_data_type) * (2 ** (pow_factor))
    specdata_sl1 = np.delete(specdata_sl1, len(specdata1) / 2)
    specdata_sl2 = np.delete(specdata_sl2, len(specdata2) / 2)

    # Get numerator and denominator of RFI score
    numdata = cd.read_interleave_data(roach, score_names[0], score_addr_width, score_word_width,
                                        score_data_type) * (2 ** (pow_factor * 2 + 4))
    denomdata = cd.read_interleave_data(roach, score_names[1], score_addr_width, score_word_width,
                                        score_data_type) * (2 ** (pow_factor * 2 + 4))
    numdata = np.delete(numdata, len(specdata1) / 2)
    denomdata = np.delete(denomdata, len(specdata2) / 2)

    # Get score data
    # scoredata = cd.read_interleave_data(roach, score_names[2], score_addr_width, score_word_width, score_data_type)
    # scoredata = np.delete(scoredata, len(specdata1) / 2)

    # Normalize data by acc_len and convert to dBFS
    specdata1db = cd.scale_and_dBFS_specdata(specdata1, acc_len, dBFS)
    specdata2db = cd.scale_and_dBFS_specdata(specdata2, acc_len, dBFS)
    specdata_sl1db = cd.scale_and_dBFS_specdata(specdata_sl1, acc_len, dBFS)
    specdata_sl2db = cd.scale_and_dBFS_specdata(specdata_sl2, acc_len, dBFS)
    numdatadb = cd.scale_and_dBFS_specdata(np.sqrt(numdata), acc_len, dBFS)
    denomdatadb = cd.scale_and_dBFS_specdata(np.sqrt(denomdata), acc_len, dBFS)

    # Power Spectral Density full bits, the product and squared root are calculated in python
    multdatadb = [(specdata1db[j] + specdata2db[j]) / 2 for j in range(len(specdata1db))]

    # Add last score sum and time data
    # t.append(time.time() - time_start)
    # scoresum.append(np.sum(scoredata))

    # Trigger adquisition control of brams
    roach.write_int(adq_trigger_reg, 1)
    roach.write_int(adq_trigger_reg, 0)

    # Update fig lines
    lines[0].set_data(freqs, specdata1db)
    lines[1].set_data(freqs, specdata2db)
    lines[2].set_data(freqs, specdata_sl1db)
    lines[3].set_data(freqs, specdata_sl2db)
    lines[4].set_data(freqs, numdatadb)
    lines[5].set_data(freqs, denomdatadb)
    linePSDM.set_data(freqs, multdatadb)
    # lines[6].set_data(freqs, scoredata)
    lines[7].set_data(t, scoresum)

    # Update x-limits of plots  with time to see the last 60 seconds
    # if t[-1] > 60:
    #     ax8.set_xlim(t[-1] - 60, t[-1])

    # Update rectangle patch
    y0 = 10 * np.log10(2 ** (pow_factor - np.log2(acc_len))) - dBFS
    height = 10 * np.log10(2 ** 18)
    for patch in patches:
        patch.set_y(y0)
        patch.set_height(height)
    return lines


time_start = time.time()
ani = animation.FuncAnimation(fig, run, interval=10, init_func=init)
root.mainloop()
