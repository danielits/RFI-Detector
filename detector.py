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
import numpy as np

varData = np.zeros(varAcc)
varIndex = 0

graphIndex = 0
graphSize = 300
graphData = np.zeros(graphSize)

LARGE_FONT = ("verdana", 12)
style.use("bmh")

roach = cd.initialize_roach(roach_ip, boffile=boffile, upload=True)
#roach = cd.initialize_roach('192.168.1.12')
roach.write_int(acc_len_reg, acc_len)
roach.write_int(cnt_rst_reg, 1)
roach.write_int(cnt_rst_reg, 0)

fig = Figure(figsize=(10, 5), dpi=100)
fig.set_tight_layout(True)
ax1 = fig.add_subplot(321)
ax2 = fig.add_subplot(322)
ax3 = fig.add_subplot(323)
ax4 = fig.add_subplot(324)
ax5 = fig.add_subplot(325)
axes = [ax1, ax2, ax3, ax4]
titles = ["Main signal", "Referece signal", "Cross-correlation magnitude", "Power multiplied"]

for ax, title in zip(axes, titles):
    ax.plot([], [])
    ax.set_xlim(0, bandwidth)
    ax.set_ylim(-dBFS - 2, 0)
    ax.set_xlabel('Frequency [MHz]')
    ax.set_ylabel('Power [dBFS]')
    ax.set_title(title)

def animate(i):
    
	specdata1 = cd.read_interleave_data(roach, specbrams_list[0], spec_addr_width, spec_word_width, spec_data_type)
	specdata2 = cd.read_interleave_data(roach, specbrams_list[1], spec_addr_width, spec_word_width, spec_data_type)
	
	specdata1 = cd.scale_and_dBFS_specdata(specdata1, acc_len, dBFS)
	specdata2 = cd.scale_and_dBFS_specdata(specdata2, acc_len, dBFS)
	multdata = [specdata1[j] + specdata2[j] + (2 *31.683) for j in range(len(specdata2))]
	
	data = []
	for bram in speccross_list:
		bramdata = struct.unpack('>256Q',roach.read(bram,2**speccross_addr_width*speccross_word_width/8))
		for j in np.arange(0,256,2):
			aux = bramdata[j+1] + (bramdata[j] << 64)
			data.append(aux)
	interleaved_data = np.resize(data, (len(speccross_list), len(data)/len(speccross_list)))
	interleaved_data = np.vstack(interleaved_data).reshape((-1,), order='F')
	interleaved_data = cd.scale_and_dBFS_specdata(interleaved_data, acc_len, dBFS)
	
	#Score data
	score_data = []
	bramscore = struct.unpack('>1024Q',roach.read(score_name_bram,2**score_addr_width*score_word_width/8))
	for j in np.arange(0,1024,2):
		aux = bramscore[j+1] + (bramscore[j] << 64)
		score_data.append(aux)
	#print('Score FPGA: ' + str(max(score_data)) +', Score Python: ' + str(np.sum(data)
	
	global varIndex
	scorePy = np.sum(data)
	varData[varIndex] = 10 * np.log10(scorePy)
	variance = np.std(varData)
	
	global graphIndex
	graphData[graphIndex] = 10 * np.log10(scorePy)
	
	
	if graphIndex != graphSize-1:
		graphIndex += 1
	else:
		graphIndex = 0
	
	
	if varIndex != varAcc-1:
		varIndex += 1
	else:
		varIndex = 0
	
	for ax in axes:
		if len(ax.lines) > 0:
			del ax.lines[-1]
	ax1.plot(freqs, specdata1, "C", linewidth=1.3)
	ax2.plot(freqs, specdata2, "C", linewidth=1.3)
	ax3.plot(freqs, interleaved_data, "C", linewidth=1.3)
	ax4.plot(freqs, multdata, "C", linewidth=1.3)
	ax5.plot(graphData, "C", linewidth=1.3)

	
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

        label1 = tk.Label(self, text="Accumulation Size: ")
        label1.pack(side=tk.LEFT, fill=tk.NONE, expand=False, pady=10, padx=5)

        v = tk.StringVar(value=acc_len)
        entry1 = tk.Entry(self, textvariable=v)
        entry1.pack(side=tk.LEFT, fill=tk.NONE, expand=False, pady=10, padx=5)

        button1 = tk.Button(self, text="Update",
                            command=lambda: self.updateAcc(entry1.get()))
        button1.pack(side=tk.LEFT, fill=tk.NONE, expand=False, pady=10, padx=5)

    def updateAcc(self, value):
        print('Updating register', acc_len_reg)
        roach.write_int(acc_len_reg, value)
        acc_len = roach.read_int(acc_len_reg)
        roach.write_int(cnt_rst_reg, 1)
        roach.write_int(cnt_rst_reg, 0)
        print('acc_len:', str(acc_len))

class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Main Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

app = CrossCor()
ani = animation.FuncAnimation(fig, animate, interval=10)
app.mainloop()
