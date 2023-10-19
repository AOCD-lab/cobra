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

    for line in lines:
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

ax.plot(label_loc, data1+data3, lw=2, label='reference')
ax.plot(label_loc, data1, lw=3, label=sys.argv[1])

ax.set_theta_direction(-1)
ax.set_theta_offset(np.pi / 2.0)

ax.spines['polar'].set_linewidth(3)
    
ax.grid(color='black', alpha=1.0)
    
ax.set_ylim(0, 1.2)

ax.tick_params(axis='both', which='major', pad=20, labelsize=12)

#ax.yaxis.set_major_locator(MultipleLocator(1))
#ax.yaxis.set_minor_locator(AutoMinorLocator(5))
    
ax.legend(loc="lower right", bbox_to_anchor=(.1, 1.0))

ax.yaxis.grid(True)

ax.grid(which='minor', color='#EEEEEE', linestyle=':', linewidth=0.5)

ax.minorticks_on()

ax.yaxis.set_major_locator(ticker.FixedLocator([0.2, 0.4, 0.6, 0.8, 1.0, 1.2]))
ax.yaxis.set_minor_locator(ticker.FixedLocator([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.9, 1.1]))

#ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.2))

ax.set_rlabel_position(180/1 + 180/12)

#ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])

lines, labels = plt.thetagrids(np.degrees(label_loc), labels=label)

plt.tight_layout()

#plt.show()

filename, file_extension = os.path.splitext(sys.argv[1])
plt.savefig(filename+"-pcs.ps")
plt.savefig(filename+"-pcs.png")


