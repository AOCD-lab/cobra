#!/usr/bin/python
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import subprocess                 # For issuing commands to the OS.
import os
import sys                        # For determining the Python version.
import seaborn as sns
from pylab import *
from matplotlib import font_manager
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)


# --- Main program below


# checking 5 arguments are passed from command line

#if (len(sys.argv)<1) :
#   print(' ')
#   sys.exit( ' Usage: mappa.py surface-file.dat spacing')
#
#
## set filenames to be read

#CFFFile   = sys.argv[1].replace("matrix", "MAE_boot_coef-cut")
#PREFile   = sys.argv[1].replace("matrix", "MAE_boot_pred-cut")

CFFFile = "COEF_FILE"
PREFile = "FITT_FILE"

# read coefficient file

with open(CFFFile, "r") as f:
     lines = f.readlines()

cff_data = []
for line in lines:
    cff_data.append(float(line.split()[-1]))

cff_data = np.array(cff_data)


# read prediction file

with open(PREFile, "r") as f:
     lines = f.readlines()

pre_data = []
for line in lines:
    pre_data.append(float(line.split()[-1]))

pre_data = np.array(pre_data)


# set plot space and plot distribution

fig, ax = plt.subplots()

sns.distplot(cff_data, color="b", hist=False, ax=ax, kde_kws=dict(linewidth=1))
sns.distplot(pre_data, color="r", hist=False, ax=ax, kde_kws=dict(linewidth=1))

plt.rcParams.update({ 'font.sans-serif': 'Myriad Pro',
                      'font.family': 'sans-serif'        })

# set axes ticks and format

fig.set_figwidth(2.0)
fig.set_figheight(2.0)

ax.set_xlim(-1.0, 1.0)
for axis in ['top','bottom','left','right']:
    ax.spines[axis].set_linewidth(1.0)

#xticks_font = font_manager.FontProperties(family='sans-serif')
#plt.xticks(fontname = 'Helvetica')

ax.tick_params(axis='x', labelsize=9)
ax.tick_params(axis='y', labelsize=9)

ax.xaxis.set_major_formatter('{x:3.1f}')
ax.yaxis.set_major_formatter('{x:3.1f}')


ax.xaxis.set_major_locator(MultipleLocator(1))
ax.xaxis.set_minor_locator(AutoMinorLocator(2))


ax.tick_params(which='both', width=1.0, length=3)


# ax.set_xticks([-2, -1.0, 0.0, 1, 2], minor=True)
ax.set_yticks([0.0, 1.0, 2.0, 3.0])


# Set coloumn with reference colors


filename, file_extension = os.path.splitext(sys.argv[1])
plt.savefig(filename+".ps")
plt.savefig(filename+".png")

print('Info:   ','Normal termination'                         )







