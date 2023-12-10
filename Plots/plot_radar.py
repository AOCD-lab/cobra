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
import matplotlib.ticker as ticker



# --- read prediction file -----------------------------

def read_data(DATFile):
  
    with open(DATFile, "r") as f:
         lines = f.readlines()
    
    label = []
    data1 = []
    data2 = []
    data3 = []

    for line in lines[1:]:
        words = line.split()
        if len(words) == 4:
           label.append(line.split()[0])
           data1.append(float(line.split()[1]))
           data2.append(float(line.split()[2]))
           data3.append(float(line.split()[3]))

    label = [*label, label[0]]
    data1 = [*data1, data1[0]]
    data2 = [*data2, data2[0]]
    data3 = [*data3, data3[0]]

    data1 = np.array(data1)
    data2 = np.array(data2)
    data3 = np.array(data3)
   
    return (label, data1, data2, data3)
# ------------------------------------------------------



# --- Main program below

 
# checking 5 arguments are passed from command line
 
if (len(sys.argv)<2) :
   print(' ')
   sys.exit( ' Usage: mappa.py surface-file.dat spacing')


# read x_data files

label, data1, data2, data3 = read_data(sys.argv[1])

# set figure and plot distribution


label_loc = np.linspace(start=0, stop=2 * np.pi, num=len(label))

fig, ax = plt.subplots(figsize=(5,5), subplot_kw=dict(polar=True))


basename = os.path.splitext(sys.argv[1])[0]

ax.plot(label_loc, data3, lw=3, label=basename, zorder=2)

ax.set_theta_direction(-1)
ax.set_theta_offset(np.pi / 2.0)

ax.spines['polar'].set_linewidth(3)
ax.grid(color='black', alpha=1.0)


# find plot limits

ymin = np.min(data3)
ymax = np.max(data3)

test = np.arange(-2.0,+2.0,0.2)

for it in range(len(test)):
    if test[it] > ymax:
       ymax = test[it]
       break
    if test[it] > ymin:
       ymin = test[it-1]
       break

ax.set_ylim(ymin,ymax)

ax.tick_params(axis='both', which='major', pad=20, labelsize=12)
ax.legend(loc="lower right", bbox_to_anchor=(.1, 1.0))

ax.yaxis.grid(True)
ax.grid(which='minor', color='#EEEEEE', linestyle=':', linewidth=0.5)

#ax.yaxis.set_major_locator(ticker.FixedLocator([-1.2,-1.0,-0.8,-0.6,-0.4,-0.2,0.0,0.2,0.4,0.6,0.8,1.0,1.2]))

tikki=np.arange(ymin+0.2,ymax,0.2)
ax.yaxis.set_major_locator(ticker.FixedLocator(tikki))



ax.yaxis.set_minor_locator(ticker.FixedLocator([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.9, 1.1]))
ax.minorticks_on()


# plot zero axis in red color

circle = plt.Circle((0, 0), 0.6, transform=ax.transData._b, fill=False, edgecolor='red', linewidth=2, zorder=1)
plt.gca().add_artist(circle)


ax.set_rlabel_position(180/1 + 180/12)

lines, labels = plt.thetagrids(np.degrees(label_loc), labels=label)

plt.tight_layout()

filename, file_extension = os.path.splitext(sys.argv[1])
plt.savefig(filename+"-pcs.ps")
plt.savefig(filename+"-pcs.png")


