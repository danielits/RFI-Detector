import itertools
import tkinter as tk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib import style, animation
from detector_parameters import *

roach = cd.initialize_roach(roach_ip, boffile=boffile, upload=True)
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

line, = ax5.plot([], [], lw=2)
xdata, ydata = [], []
x = np.arange()


def data_gen():
    for cnt in itertools.count():
        t = cnt / 10
        yield t, np.sin(2*np.pi*t) * np.exp(-t/10.)


def init():
    for ax, title in zip(axes, titles):
        ax.plot([], [])
        ax.set_xlim(0, 20)
        ax.set_ylim(-80 - 2, 0)
        ax.set_xlabel('Frequency [MHz]')
        ax.set_ylabel('Power [dBFS]')
        ax.set_title(title)

    ax5.set_ylim(-1.1, 1.1)
    ax5.set_xlim(0, 30)
    del xdata[:]
    del ydata[:]
    line.set_data(xdata, ydata)
    return line,

def run(data):
    # update the data
    t, y = data
    xdata.append(t)
    ydata.append(y)
    xmin, xmax = ax5.get_xlim()

    if t >= xmax:
        xmax+=1/10
        xmin+=1/10
        ax5.set_xlim(xmin, xmax)
        ax5.figure.canvas.draw()
    line.set_data(xdata, ydata)

    for ax in axes:
        if len(ax.lines) > 0:
            del ax.lines[-1]
    ax1.plot(freqs, specdata1, "C", linewidth=1.3)
    ax2.plot(freqs, specdata2, "C", linewidth=1.3)
    ax3.plot(freqs, interleaved_data, "C", linewidth=1.3)
    ax4.plot(freqs, multdata, "C", linewidth=1.3)

    return line,

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
