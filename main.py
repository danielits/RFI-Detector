import itertools
import Tkinter as tk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib import style, animation
from detector_parameters import *
import calandigital as cd

# roach = cd.initialize_roach(roach_ip, boffile=boffile, upload=True)
roach = cd.initialize_roach('192.168.1.12')
roach.write_int(acc_len_reg, acc_len)
roach.write_int(cnt_rst_reg, 1)
roach.write_int(cnt_rst_reg, 0)

fig = Figure(figsize=(10, 5), dpi=120)
fig.set_tight_layout(True)
ax1 = fig.add_subplot(321)
ax2 = fig.add_subplot(322)
ax3 = fig.add_subplot(323)
ax4 = fig.add_subplot(324)
ax5 = fig.add_subplot(325)
axes = [ax1, ax2, ax3, ax4]
titles = ["Main signal", "Referece signal", "Cross-correlation magnitude", "Power multiplied"]

line, = ax5.plot([], [], "C", lw=1.3)

for ax, title in zip(axes, titles):
    ax.plot([], [])
    ax.set_xlim(0, 20)
    ax.set_ylim(-80 - 2, 0)
    ax.set_xlabel('Frequency [MHz]')
    ax.set_ylabel('Power [dBFS]')
    ax.set_title(title)
ax5.set_ylim(-dBFS - 2, 0)
ax5.set_xlim(0, bandwidth)

def data_gen():

    specdata1 = cd.read_interleave_data(roach, specbrams_list[0], spec_addr_width, spec_word_width, spec_data_type)
    specdata2 = cd.read_interleave_data(roach, specbrams_list[1], spec_addr_width, spec_word_width, spec_data_type)
    specdata1 = cd.scale_and_dBFS_specdata(specdata1, acc_len, dBFS)
    specdata2 = cd.scale_and_dBFS_specdata(specdata2, acc_len, dBFS)

    yield specdata1, specdata2


def init():
    return line

def run(data):
    # update the data
    t, y = data
    line.set_data(freqs, t)

    return line

class CrossCor(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}

        for F in (MainPage, PageOne):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(MainPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Main Page")
        label.pack(pady=10, padx=10)

app = CrossCor()
ani = animation.FuncAnimation(fig, run, data_gen, interval=10, init_func=init)
app.mainloop()
