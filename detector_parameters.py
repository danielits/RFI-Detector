# File with all the basic parameters for RFI mitigation scripts

# imports
import numpy as np

# communication parameters
roach_ip = '192.168.1.12'
boffile = 'detector_sinscore_2021_Jun_13_2247.bof.gz'

# model parameters
adc_bits = 8
bandwidth = 540  # MHz
acc_len_reg = 'acc_len'
cnt_rst_reg = 'cnt_rst'
detector_gain_reg = 'detector_gain'
adq_trigger_reg = 'trigger'
spec_addr_width = 7  # bits
spec_word_width = 64  # bits
spec_data_type = '>u8'
speccross_addr_width = 7  # bits
speccross_word_width = 128  # bits
score_addr_width = 9  # bits
score_word_width = 128  # bits
score_name_bram = 'dout_score'

# Primary signal
specbrams_list = [['dout0_0', 'dout0_1', 'dout0_2', 'dout0_3',
                   'dout0_4', 'dout0_5', 'dout0_6', 'dout0_7'],
                  # reference signal
                  ['dout1_0', 'dout1_1', 'dout1_2', 'dout1_3',
                   'dout1_4', 'dout1_5', 'dout1_6', 'dout1_7']]

# Cross-correlated signal
crossbrams_list = ['dout2_0', 'dout2_1', 'dout2_2', 'dout2_3',
                   'dout2_4', 'dout2_5', 'dout2_6', 'dout2_7']

pows_list = ['dout3_0', 'dout3_1', 'dout3_2', 'dout3_3',
             'dout3_4', 'dout3_5', 'dout3_6', 'dout3_7']

score_list = ['score_0', 'score_1', 'score_2', 'score_3',
              'score_4', 'score_5', 'score_6', 'score_7']


# experiment parameters
acc_len = 2 ** 12
detector_gain = 2 ** 15

# derivative parameters
nchannels = 2 ** spec_addr_width * len(specbrams_list[0])
freqs = np.linspace(0, bandwidth, nchannels, endpoint=False)  # MHz
freqs = np.delete(freqs, len(freqs) / 2)
dBFS = 6.02 * adc_bits + 1.76 + 10 * np.log10(nchannels)