import matplotlib
import numexpr
import math
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


def add_reg_entry(roach, root, reg):
    frame = tk.Frame(master=root, bg="white")
    frame.pack(side=tk.TOP, anchor="w")
    label = tk.Label(frame, text=reg + ":", bg="white")
    label.pack(side=tk.LEFT)
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
        ax.set_xlim(0, bandwidth)
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
    numdata = [math.sqrt(numdata[i]) for i in range(0, len(numdata))]
    numdata = np.asarray(numdata)
    numdata = np.delete(numdata, len(specdata1) / 2)
    denomdata = [math.sqrt(denomdata[i]) for i in range(0, len(denomdata))]
    denomdata = np.asarray(denomdata)
    denomdata = np.delete(denomdata, len(specdata2) / 2)

    # Get score data
    scoredata = cd.read_interleave_data(roach, score_names[2], score_addr_width, score_word_width,
                                        score_data_type) * 2 ** -30
    scoredata = np.delete(scoredata, len(specdata1) / 2)

    # Score derivative
    global score_der_last
    score_der = scoredata - score_der_last
    score_der_last = scoredata

    # Save data
    # config = 'data/cfg1_'
    # filenames = ['specdata1.txt', 'specdata2.txt', 'specdata_sl1.txt', 'specdata_sl2.txt', 'numdata.txt',
    #              'denomdata.txt', 'scoredata.txt', 'timedata.txt']
    # data_array = [specdata1, specdata2, specdata_sl1, specdata_sl2, numdata, denomdata, scoredata, time.time()]
    # for filename, data in zip(filenames, data_array):
    #     f = open(config + filename, 'ab')
    #     np.savetxt(f, [data])
    #     f.close()

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

    # Acquisition trigger of brams
    roach.write_int(adq_trigger_reg, 1)
    roach.write_int(adq_trigger_reg, 0)

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
