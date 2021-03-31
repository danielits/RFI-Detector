# Script to filter RFI with the kesteven filter model. Plots
# the spectrum of the primary signal, reference signal and
# the filter output. Also add some user interface to control 
# the filter and show additional plots.
import time
import numexpr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import Tkinter as Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import calandigital as cd
from detector_parameters import *

def main():
    # initialization
    roach = cd.initialize_roach(roach_ip)

    print("Setting model registers...")
    roach.write_int(acc_len_reg, acc_len)
    roach.write_int(filter_gain_reg, filter_gain)
    print("done")
    print("Resseting counter registers...")
    roach.write_int(cnt_rst_reg, 1)
    roach.write_int(cnt_rst_reg, 0)
    print("done")

    print("Setting GUI elements...")
    fig, lines = create_window(roach)
    print("done.")

    # animation function
    def animate(_):
        for line, specbrams in zip(lines, specbrams_list):
            # update acc_len
            acc_len = roach.read_uint(acc_len_reg)
            # get spectral data
            specdata = cd.read_interleave_data(roach, 
                specbrams, spec_addr_width, spec_word_width, 
                spec_data_type)
            specdata = cd.scale_and_dBFS_specdata(specdata,
                acc_len, dBFS)
            line.set_data(freqs, specdata)
        return lines

    anim = animation.FuncAnimation(fig, animate, blit=True)
    Tk.mainloop()

def create_window(roach):
    """
    Create wondow for the RFI Filter
    """
    # create window
    root = Tk.Tk()

    # add matplotlib figure and toolbar
    fig, lines = create_figure(root)

    # create button frame and buttons
    button_frame = Tk.Frame(master=root)
    button_frame.pack(side=Tk.TOP, anchor="w")
    add_save_button(roach, button_frame)
    add_reset_button(roach, button_frame)

    # add regiter entries
    add_reg_entry(roach, root, acc_len_reg)
    add_reg_entry(roach, root, filter_gain_reg)

    return fig, lines

def create_figure(root):
    """
    Create the figure that contains the plots of the filter.
    """
    fig = plt.Figure()
    fig.set_tight_layout(True)
    canvas = FigureCanvasTkAgg(fig, master=root)
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)        

    # add axes to figure
    ax1 = fig.add_subplot(2,2,1)
    ax2 = fig.add_subplot(2,2,2)
    ax3 = fig.add_subplot(2,2,3)
    axes = [ax1, ax2, ax3]
    titles = ["Primary Signal", "Reference Signal", "Filter Output"]

    # define axes and create plot lines
    lines = []
    for ax, title in zip(axes, titles):
        ax.set_xlim(0, bandwidth)
        ax.set_ylim(-dBFS-2, 0)
        ax.set_xlabel('Frequency [MHz]')
        ax.set_ylabel('Power [dBFS]')
        ax.set_title(title)
        ax.grid()

        line, = ax.plot([], [], animated=True)
        lines.append(line)

    return fig, lines

def add_save_button(roach, button_frame):
    """
    Add save button to the button panel of the GUI.
    Save the plotted data into a file.
    """
    save_button = Tk.Button(button_frame, text="Save data")
    def save():
        specdata_list = []
        for specbrams in specbrams_list:
            specdata = cd.read_interleave_data(roach, 
                specbrams, spec_addr_width, spec_word_width, 
                spec_data_type)
            specdata_list.append(specdata)
        np.savez("filter_data", prim=specdata_list[0],
            ref=specdata_list[1],
            output=specdata_list[2])
        print("Data saved")
    save_button.config(command=save)
    save_button.pack(side=Tk.LEFT)

def add_reset_button(roach, button_frame):
    """
    Add reset button to the button panel of the GUI.
    It reset the cnt_rst register of the model.
    """
    reset_button = Tk.Button(button_frame, text="Reset")
    def reset():
        roach.write_int(cnt_rst_reg, 1)
        roach.write_int(cnt_rst_reg, 0)
        print("reset ROACH")
    reset_button.config(command=reset)
    reset_button.pack(side=Tk.LEFT)

def add_reg_entry(roach, root, reg):
    """
    Add a text entry to the GUI to modify a register in FPGA.
    The desired value must be written in the entry textbox,
    and the value is assigned by pressing <Return> with the
    textbox focused.
    """
    # add frame
    frame = Tk.Frame(master=root)
    frame.pack(side = Tk.TOP, anchor="w")
    # add label
    label = Tk.Label(frame, text=reg+":")
    label.pack(side=Tk.LEFT)
    # add entry
    entry = Tk.Entry(frame)
    entry.insert(Tk.END, roach.read_uint(reg))
    entry.pack(side=Tk.LEFT)
    def set_reg_from_entry():
        string_val = entry.get()
        try:
            val = int(numexpr.evaluate(string_val))
        except:
            raise Exception('Unable to parse value in textbox: ' 
                + string_val)
        print("Set reg " + reg + " to value " + str(val))
        roach.write_int(reg, val)
    entry.bind('<Return>', lambda x: set_reg_from_entry())


if __name__ == "__main__":
    main()
