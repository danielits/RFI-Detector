# File with all the basic parameters for RFI mitigation scripts

# imports
import numpy as np
from calibrate_adcs import *

# communication parameters
roach_ip = '192.168.1.12'
boffile = 'spectrometerv2.bof.gz'
# boffile = 'spec4in_2048ch_600mhz.bof.gz 'usr/local/lib/python2.7/dist-packages/calandig
# ital-0.1-py2.7.egg/calandigital/adc5g_devel/SPI.py"
# hice abs para negativos pero aveces tira error por ser mayot a 65k

calibrate = 0 #Revisar

# model parameters
adc_bits = 8
bandwidth = 600  # MHz
acc_len_reg = 'acc_len'
cnt_rst_reg = 'cnt_rst'
detector_gain_reg = 'detector_gain'
adq_trigger_reg = 'brams_trigger'
spec_addr_width = 9  # bits
spec_word_width = 64  # bits
spec_data_type = '>u8'
score_addr_width = 9  # bits
score_word_width = 32  # bits
score_data_type = '>u4'

specbrams_list = [['dout_0a_0', 'dout_0a_1', 'dout_0a_2', 'dout_0a_3'],
                   #'dout0_4', 'dout0_5', 'dout0_6', 'dout0_7'],

                  ['dout_0c_0', 'dout_0c_1', 'dout_0c_2', 'dout_0c_3']]
                   #'dout1_4', 'dout1_5', 'dout1_6', 'dout1_7']]



specbrams_list = [['dout0_0', 'dout0_1', 'dout0_2', 'dout0_3'],
                   #'dout0_4', 'dout0_5', 'dout0_6', 'dout0_7'],

                  ['dout1_0', 'dout1_1', 'dout1_2', 'dout1_3']]
                   #'dout1_4', 'dout1_5', 'dout1_6', 'dout1_7']]

# experiment parameters
acc_len =       2 ** 12
detector_gain = 31 #  cuantos bits corro la ventana de 16 bits desde el MSB
pwr_sliced_bits = 46

# derivative parameters
nchannels = 2 ** spec_addr_width * len(specbrams_list[0])
freqs = np.linspace(0, bandwidth, nchannels, endpoint=False)  # MHz
freqs = np.delete(freqs, len(freqs) / 2)
dBFS = 6.02 * adc_bits + 1.76 + 10 * np.log10(nchannels)
