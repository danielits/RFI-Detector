import matplotlib
import numexpr
import math
from sklearn.decomposition import PCA
from sklearn import preprocessing

import scipy.stats
from scipy import stats
import numpy as np
import pandas as pd
import time
from matplotlib import patches as pat
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import Tkinter as tk
from matplotlib import animation
from detector_parameters import *
import calandigital as cd
import matplotlib.pyplot as plt

matplotlib.use("TkAgg")
# score_der_last = np.zeros(nchannels - 1)

config = 'data/cfg3_'
filenames = ['specdata_sl1.txt', 'specdata_sl2.txt', 'numdata.txt']
files = []
score = []
mean = []
var = []
skew = []
kurt = []

data = pd.read_csv(config+'scoredata.txt', delimiter=' ', header=None)

for i in data.T:
    row = data.T[i][1:]
    score.append(row.max())

stats = stats.describe(data, axis=1)
stats = np.stack([stats[1][0], stats[1][1], stats[2], stats[3], stats[4], stats[5]], axis=1)
scaled_stats = stats
# scaled_stats = preprocessing.scale(stats, axis=0)
pca = PCA(n_components=2)
pca.fit(scaled_stats)
pca_data = pca.transform(scaled_stats)
scaled_stats = pca_data


# per_var = np.round(pca.explained_variance_ratio_* 100, decimals=1)
# labels = ['PC'+str(x) for x in range(1, len(per_var)+1)]
# plt.bar(x=range(1, len(per_var)+1), height=per_var, tick_label=labels)
# plt.ylabel('Percentage of Explained Variance')
# plt.xlabel('Principal Component')
# plt.title('Scre Plot')
# plt.show()

x1=[]
x2=[]
y1=[]
y2=[]
for i in range(0, len(pca_data)):
    if score[i] > 0.4:
        x1.append(scaled_stats[i][0])
        y1.append(scaled_stats[i][1])
    else:
        x2.append(scaled_stats[i][0])
        y2.append(scaled_stats[i][1])

plt.scatter(x1, y1 ,s = 10, c='r', alpha=0.5, label='Detection')
plt.scatter(x2, y2 ,s = 10, c='b', alpha=0.5, label='No detection')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.legend()
plt.show()
# for filename in filenames[0:1]:
#     data = pd.read_csv(config+filename, delimiter=' ', header=None)
#
#     #  Moments calculations
#     nchannels = nchannels - 1
#     for i in data.T:
#         row = data.T[i] / acc_len
#         mean.append(np.sum(row) / nchannels)
#         var.append(np.sum((row - mean[-1]) ** 2) / (nchannels - 1 ))
#         skew.append(np.sum((row - mean[-1]) ** 3) / var[-1]**(3/2))
#         kurt.append(np.sum((row - mean[-1]) ** 4) / (var[-1] ** 2)*nchannels*(nchannels+1)/((nchannels-1)*(nchannels-2)*(nchannels-3)) - 3*((nchannels-1)**2)/((nchannels-2)*(nchannels-3)))
#
#     features = np.stack([mean, skew, var, kurt], axis = 1)
#     print features
