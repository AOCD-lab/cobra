#!/usr/bin/python3 -B
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pylab import *
from matplotlib import font_manager
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)


# --- Main program below

# set filenames to be read

DATAFile  = sys.argv[1]

PNGFile  = sys.argv[1].replace("loo_dat", "loo_dat.png")
PSFile   = sys.argv[1].replace("loo_dat", "loo_dat.ps")

# read mysystem.mlr_out file

with open(DATAFile, "r") as f:
     lines = f.readlines()

y_data = []
x_data = []

for line in lines[1:]:
    x_data.append(float(line.split()[1]))
    y_data.append(float(line.split()[2]))

x_data = np.array(x_data)
y_data = np.array(y_data)


# set plot space and scatter plot data

fig, ax = plt.subplots()
plt.scatter(x_data, y_data, s=6, c="r")


# Make linear fitting using numpy and plot fitted line

z = np.polyfit(x_data, y_data, 1)
p = np.poly1d(z)
plt.plot(x_data, p(x_data), linewidth=1.0 )


# set plot layout and fig size

fig.set_figwidth(3.0)
fig.set_figheight(3.0)
plt.rcParams.update({ 'font.sans-serif': 'Myriad Pro',
                      'font.family': 'sans-serif'        })


# set axes ticks and format

for axis in ['top','bottom','left','right']:
    ax.spines[axis].set_linewidth(1.0)

ax.tick_params(axis='x', labelsize=11)
ax.tick_params(axis='y', labelsize=11)

ax.xaxis.set_major_formatter('{x:3.1f}')
ax.yaxis.set_major_formatter('{x:3.1f}')

max_ticks_spacer = (max(x_data) - min(x_data)) / 3.0
max_ticks_spacer = round(max_ticks_spacer, 1)

ax.xaxis.set_major_locator(MultipleLocator(max_ticks_spacer))
ax.yaxis.set_major_locator(MultipleLocator(max_ticks_spacer))

ax.xaxis.set_minor_locator(MultipleLocator(max_ticks_spacer/2.0))
ax.yaxis.set_minor_locator(MultipleLocator(max_ticks_spacer/2.0))

ax.tick_params(which='both', width=1.0, length=3)

plt.title("LOO plot: Original data", fontsize = 12)
plt.xlabel("Experimental data", fontsize = 12)
plt.ylabel("LOO data", fontsize = 12)

plt.tight_layout()


# filename, file_extension = os.path.splitext(sys.argv[1])
plt.savefig(PNGFile)
plt.savefig(PSFile)

print('Info:   ','Normal termination'                         )
