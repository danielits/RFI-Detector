import matplotlib
import math
from sklearn.decomposition import PCA
from sklearn import preprocessing
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from mpldatacursor import HighlightingDataCursor, DataCursor
import calandigital as cd
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
filenames = ['specdata_sl1.txt', 'specdata_sl2.txt', 'numdata.txt', 'scoredata.txt']
cdict = {0: 'red', 1: 'blue', 2: 'green', 3: 'cyan', 4: 'black'}
ldict = {0: 'No detection', 1: 'Detection narrowband', 2: 'Detection broadband'}
xlabels = ['Principal Component 1', 'Principal Component 1', 'Main Feature 1', 'Main Feature 1']
ylabels = ['Principal Component 2', 'Principal Component 2', 'Main Feature 1', 'Main Feature 1']
titles = ['PCA with K-Means', 'PCA with score, NB & WB decision', 't-SNE with K-Means', 't-SNE with score, NB & WB decision']
colors = []
files = []
score = []
mean = []
var = []
skew = []
kurt = []

scoredata = pd.read_csv(config+'scoredata.txt', delimiter=' ', header=None)
specdata = pd.read_csv(config+'specdata_sl1.txt', delimiter=' ', header=None) / 2**10

for i in scoredata.T:
    row = scoredata.T[i][1:]
    score.append(row.max())

temp = np.mean(scoredata.T[0][1:])
for i in range(0, len(scoredata)):
    if score[i] > 0.5:
        colors.append(1)
        # if np.mean(scoredata.T[i][1:]) >= temp * 1.3:
        #     colors.append(2)
        # else:
        #     colors.append(1)
    else:
        colors.append(0)
    temp = np.mean(scoredata.T[i][1:])

# ind = 2764
# specdata = np.loadtxt(config+filenames[3], skiprows=ind, max_rows=1)
# freqs = np.linspace(0, bandwidth, nchannels, endpoint=False)  # MHz
# freqs = np.delete(freqs, len(freqs) / 2)
# freqs = [x + 1200 for x in freqs]
# # specdata = cd.scale_and_dBFS_specdata(specdata, acc_len, dBFS)
#
# plt.plot(freqs, specdata, c=cdict[colors[ind]])
# plt.ylim([0,1])
# plt.show()


stats = stats.describe(specdata, axis=1)
stats = np.stack([stats[1][0], stats[1][1], stats[2], stats[3], stats[4], stats[5]], axis=1)
scaled_stats = preprocessing.scale(stats, axis=0)

#PCA
pca = PCA()
pca.fit(scaled_stats)
pca_stats = pca.transform(scaled_stats)

# # #t-SNE
tsne = TSNE(learning_rate=50)
tsne_stats = tsne.fit_transform(scaled_stats)

#K-Means
km = KMeans(n_clusters=3, max_iter=3000)
km.fit(scaled_stats)
km_stats = km.predict(scaled_stats)

fig,  ((ax1, ax2), (ax3, ax4))= plt.subplots(2,2)
fig.set_size_inches(18.5, 10.5, forward=True)
fig.set_tight_layout('True')
axes = [ax1, ax2, ax3, ax4]

for ax, xlabel, ylabel, title in zip(axes,xlabels,ylabels,titles):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

for i in np.unique(km.labels_):
    ix = np.where(km.labels_ == i)
    ax1.scatter(pca_stats[ix,0], pca_stats[ix,1], c=cdict[i], s=20, picker=True)
    ax3.scatter(tsne_stats[ix, 0], tsne_stats[ix, 1], c=cdict[i], s=20, picker=True)

classindex_color = []
for i in np.unique(colors):
    ix = np.where(colors == i)
    classindex_color.append(ix)
    ax2.scatter(pca_stats[ix,0], pca_stats[ix,1], c=cdict[i], label=ldict[i], s=20, picker=True)
    ax4.scatter(tsne_stats[ix, 0], tsne_stats[ix, 1], c=cdict[i], label=ldict[i], s=20, picker=True)


def onpick1(event):
    ind = event.ind
    xdata = event.artist.get_label()
    print(ind, xdata)
    for i in range(len(ldict)):
        if xdata == ldict[i]:
            ind = classindex_color[i][0][ind]
    if len(ind) == 1:
        specdata = np.loadtxt(config+filenames[0], skiprows=ind, max_rows=1)
        specdata2 = np.loadtxt(config + filenames[1], skiprows=ind, max_rows=1)
        scoredata2 = np.loadtxt(config + filenames[3], skiprows=ind, max_rows=1)
        freqs = np.linspace(0, bandwidth, nchannels, endpoint=False)  # MHz
        freqs = np.delete(freqs, len(freqs) / 2)
        freqs = [x + 1200 for x in freqs]
        specdata = cd.scale_and_dBFS_specdata(specdata, acc_len, dBFS)
        specdata2 = cd.scale_and_dBFS_specdata(specdata2, acc_len, dBFS)
        fig2, axs = plt.subplots(3,1)
        fig2.set_tight_layout('True')
        axs[0].plot(freqs, specdata)
        axs[1].plot(freqs, specdata2)
        axs[2].plot(freqs, scoredata2)
        titles = ['Main PSD', 'Reference PSD', 'Channel score']
        for ax, title in zip(axs, titles):
            ax.set_xlim(1200, 1800)
            ax.set_ylim(-dBFS - 2, 0)
            ax.set_xlabel('Frequency (MHz)')
            ax.set_ylabel('Power (dBFS)')
            ax.set_title(title)
            ax.grid()
        axs[2].set_ylim(0,1)
        ax.set_ylabel('Score')
        plt.show()
fig.canvas.mpl_connect('pick_event', onpick1)
plt.grid()
plt.legend()
plt.show()