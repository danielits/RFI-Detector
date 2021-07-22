# File with all the basic parameters for RFI detection scripts

# imports
import numpy as np

# communication parameters
roach_ip = '192.168.1.12'
boffile = 'rfidet_div.bof.gz'

# model parameters
adc_bits = 8
bandwidth = 600  # MHz
acc_len_reg = 'acc_len'
cnt_rst_reg = 'cnt_rst'
detector_gain_reg = 'detector_gain'
adq_trigger_reg = 'trigger'
spec_addr_width = 9  # bits
spec_word_width = 64  # bits
spec_data_type = '>u8'
score_addr_width = 9  # bits
score_word_width = 32  # bits
score_data_type = '>u4'

specs_names = [['dout0_0', 'dout0_1', 'dout0_2', 'dout0_3'],                        # Primary signal
               ['dout1_0', 'dout1_1', 'dout1_2', 'dout1_3']]                        # Reference signal

specs_sl_names = [['doutsl0_0', 'doutsl0_1', 'doutsl0_2', 'doutsl0_3'],             # Primary signal sliced
                  ['doutsl1_0', 'doutsl1_1', 'doutsl1_2', 'doutsl1_3']]             # Reference signal sliced

score_names = [['dout_num_0', 'dout_num_1', 'dout_num_2', 'dout_num_3'],            # Power Spectral Density multiplied
               ['dout_denom_0', 'dout_denom_1', 'dout_denom_2', 'dout_denom_3'],    # Cross-Power Spectral Density
                ['dout_score_0', 'dout_score_1', 'dout_score_2', 'dout_score_3']]   # Score

# experiment parameters
acc_len = 2 ** 12
detector_gain = 37
pwr_sliced_bits = 45

# derivative parameters
nchannels = 2 ** spec_addr_width * len(specs_names[0])
freqs = np.linspace(0, bandwidth, nchannels, endpoint=False)  # MHz
freqs = np.delete(freqs, len(freqs) / 2)
freqs = [x+1200 for x in freqs]
dBFS = 6.02 * adc_bits + 1.76 + 10 * np.log10(nchannels)
