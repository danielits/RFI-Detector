# File with all the basic parameters for RFI mitigation scripts

# imports
import numpy as np

# communication parameters
roach_ip = '192.168.1.12'
boffile = 'spectrometer.bof.gz'

# model parameters
adc_bits = 8
bandwidth = 540  # MHz
acc_len_reg = 'acc_len'
cnt_rst_reg = 'cnt_rst'
detector_gain_reg = 'detector_gain'
adq_trigger_reg = 'brams_trigger'
spec_addr_width = 7  # bits
spec_word_width = 64  # bits
spec_data_type = '>u8'

specbrams_list = [['dout0_0', 'dout0_1', 'dout0_2', 'dout0_3',
                   'dout0_4', 'dout0_5', 'dout0_6', 'dout0_7'],

                  ['dout1_0', 'dout1_1', 'dout1_2', 'dout1_3',
                   'dout1_4', 'dout1_5', 'dout1_6', 'dout1_7']]

# experiment parameters
acc_len =       2 ** 12
detector_gain = 2 ** 15 #  cuantos bits corro la ventana de 16 bits desde el MSB

# derivative parameters
nchannels = 2 ** spec_addr_width * len(specbrams_list[0])
freqs = np.linspace(0, bandwidth, nchannels, endpoint=False)  # MHz
freqs = np.delete(freqs, len(freqs) / 2)
dBFS = 6.02 * adc_bits + 1.76 + 10 * np.log10(nchannels)
