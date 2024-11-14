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
    
    label, data1 = [], []

    for line in lines[1:]:
        words = line.split()
        if len(words) == 2:
           label.append(line.split()[0])
           data1.append(float(line.split()[1]))

    label = [*label, label[0]]
    data1 = [*data1, data1[0]]

    data1 = np.array(data1)
   
    return (label, data1)
# ------------------------------------------------------



# --- Main program below

 
# checking 5 arguments are passed from command line
 
if (len(sys.argv)<2) :
   print(' ')
   sys.exit( ' Usage: mappa.py surface-file.dat spacing')


# read x_data files

label, data1 = read_data(sys.argv[1])

# set figure and plot distribution


label_loc = np.linspace(start=0, stop=2 * np.pi, num=len(label))

fig, ax = plt.subplots(figsize=(5,5), subplot_kw=dict(polar=True))


basename = os.path.splitext(sys.argv[1])[0]

ax.plot(label_loc, data1, lw=3, label=basename, color='black', zorder=5)

ax.set_theta_direction(-1)
ax.set_theta_offset(np.pi / 2.0)

ax.spines['polar'].set_linewidth(3)

# Set the grid line color to 50% gray
ax.grid(color='0.5', alpha=1.0)  # This is for major grid lines
ax.yaxis.grid(True, color='0.5', alpha=1.0)  # Explicitly specifying for y-axis major grid

# For minor grid lines (dashed), also set the color to 50% gray
ax.grid(which='minor', color='0.5', linestyle=':', linewidth=0.5)

# find plot limits

ymin = np.min(data1)
ymax = np.max(data1)
ymax = 1.0

test = np.arange(-5.0,+5.0,0.2)

for it in range(len(test)):
    if test[it] > ymin:
       ymin = test[it-1]
       break

if ymin > 0:
   ymin = 0

ax.set_ylim(ymin,ymax)

ax.tick_params(axis='both', which='major', pad=20, labelsize=12)
ax.legend(loc="lower right", bbox_to_anchor=(.1, 1.0))

ax.yaxis.grid(True)
ax.grid(which='minor', color='#EEEEEE', linestyle=':', linewidth=0.5)


tikki=np.arange(ymin+0.2,ymax,0.2)

if ymin < -0.5:
   tikki=np.arange(ymin+0.3,ymax,0.3)

if ymin < -1.0:
   tikki=np.arange(ymin+0.4,ymax,0.4)

ax.yaxis.set_major_locator(ticker.FixedLocator(tikki))


ax.yaxis.set_minor_locator(ticker.FixedLocator([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.9, 1.1]))
ax.minorticks_off()


# plot positive area cyan 

thetas = np.linspace(0,2*np.pi,500)
ax.fill(thetas, [ymax for i in thetas], color = "cyan", alpha = 0.2, zorder= 1)

# if ymin < 0 plot zero axis in red color and negative area red

if ymin < 0:
   circle = plt.Circle((0, 0), -ymin, transform=ax.transData._b, fill=False, edgecolor='red', linewidth=2, zorder=3)
   plt.gca().add_artist(circle)

   thetas = np.linspace(0,2*np.pi,500)
   ax.fill(thetas, [0 for i in thetas], color = "red", alpha = 0.3, zorder= 2)


# draw labels

ax.set_rlabel_position(180/1 + 180/12)
lines, labels = plt.thetagrids(np.degrees(label_loc), labels=label)


# save images to files

plt.tight_layout()

filename, file_extension = os.path.splitext(sys.argv[1])
plt.savefig(filename+"-pcs.ps")
plt.savefig(filename+"-pcs.png")


