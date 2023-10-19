#!/usr/bin/python -B
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


# set filenames to be read

GODFile  = sys.argv[1]

PNGFile  = sys.argv[1].replace("dat", "png")
PSFile   = sys.argv[1].replace("dat", "ps")

# read good.dat file

with open(GODFile, "r") as f:
     lines = f.readlines()

god_data = []
god_pear = []

for line in lines:
    god_pear.append(float(line.split()[-3]))
    god_data.append(float(line.split()[-1]))

god_pear = np.array(god_pear)
god_data = np.array(god_data)



# set plot space and plot distribution

fig, ax = plt.subplots()

plt.scatter(god_pear, god_data, s=1, c="r")

#  z = np.polyfit(god_pear, god_data, 1)
#  p = np.poly1d(z)
#  plt.plot(god_pear, p(god_pear), linewidth=0.5 )

# set plot layout

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
ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])



# Set coloumn with reference colors

# filename, file_extension = os.path.splitext(sys.argv[1])
plt.savefig(PNGFile)
plt.savefig(PSFile)

print('Info:   ','Normal termination'                         )







