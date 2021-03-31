# File with all the basic parameters for RFI mitigation scripts

# imports
import numpy as np

# communication parameters
roach_ip   = '192.168.1.12'
#roach_ip   = None
#boffile    = 'detv2_v2.bof.gz'

# model parameters
adc_bits        = 8
bandwidth       = 128 # MHz
acc_len_reg     = 'acc_len'
cnt_rst_reg     = 'cnt_rst'
filter_gain_reg = 'filter_gain'
spec_addr_width = 9  # bits
spec_word_width = 64 # bits
spec_data_type  = '>u8'
conv_addr_width = 10 # bits
conv_word_width = 64 # bits
conv_data_type  = '>u8'
                  # primary signal
specbrams_list = [['dout0_0', 'dout0_1', 'dout0_2', 'dout0_3', 
                   'dout0_4', 'dout0_5', 'dout0_6', 'dout0_7'],
                  # reference signal
                  ['dout1_0', 'dout1_1', 'dout1_2', 'dout1_3', 
                   'dout1_4', 'dout1_5', 'dout1_6', 'dout1_7'],
                  # filter output
                  ['dout2_0', 'dout2_1', 'dout2_2', 'dout2_3', 
                   'dout2_4', 'dout2_5', 'dout2_6', 'dout2_7']]
bram_mean0  = 'dout_mean0'
bram_mean1 = 'dout_mean1'
bram_mean1 = 'dout_mean2'

# experiment parameters
acc_len     = 2**7
filter_gain = 2**31

# derivative parameters
nchannels = 2**spec_addr_width * len(specbrams_list[0])
freqs     = np.linspace(0, bandwidth, nchannels, endpoint=False) # MHz
dBFS      = 6.02*adc_bits + 1.76 + 10*np.log10(nchannels)
