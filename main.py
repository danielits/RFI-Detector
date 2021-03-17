import calandigital as cd
import struct
import numpy as np
import time

def data_max(roach, brams, awidth, dwidth):
	maxd=0
	for bram in brams:
		bramdata = struct.unpack('>256Q',roach.read(bram,2**awidth*dwidth/8))
		print(len(bramdata))
		time.sleep(2)
		for i in np.arange(0,256,2):
			aux = ( bramdata[i] << dwidth/2 ) + bramdata[i+1]
			if aux > maxd:
				maxd =aux
	return maxd
	
bramnames = ['dout0_0', 'dout0_1', 'dout0_2', 'dout0_3', 'dout0_4', 'dout0_5', 'dout0_6', 'dout0_7']
ip = '192.168.1.12'
addrwidth = 7
datawidth = 128
bandwidth = 540
acclen = 2**5
nbits = 8
acc_len_reg = 'acc_len'
filter_gain = 2**16 #Puse esto pq el filter gain esta en complemento de 2 y con
					#1 dividia, el maximo valor es 820.000 al utilizar 2**16 de gain
	
roach = cd.initialize_roach('192.168.1.12', boffile='det2v2.bof.gz'	, upload=True)
#roach = cd.initialize_roach('192.168.1.12')
roach.write_int('acc_len',0)
roach.write_int('acc_len',acclen)
roach.write_int('filter_gain',filter_gain)
roach.write_int('cnt_rst',1)
roach.write_int('cnt_rst',0)

while True:
	c = data_max(roach, bramnames, addrwidth, datawidth)
	print(c, roach.read_int('filter_gain'))
