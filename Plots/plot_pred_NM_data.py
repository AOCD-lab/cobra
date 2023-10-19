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

PNGFile  = sys.argv[1].replace("pred_out", "pred_out.png")
PSFile   = sys.argv[1].replace("pred_out", "pred_out.ps")

# read mysystem.mlr_out file

with open(DATAFile, "r") as f:
     lines = f.readlines()

fy_data = []
fx_data = []
py_data = []
px_data = []

for line in lines:
    line = line[:-1]
    if line.endswith('Fit'):
       fx_data.append(float(line.split()[2]))
       fy_data.append(float(line.split()[3]))

    if line.endswith('Pre'):
       fx_data.append(float(line.split()[2]))
       fy_data.append(float(line.split()[3]))
       px_data.append(float(line.split()[2]))
       py_data.append(float(line.split()[3]))

fx_data = np.array(fx_data)
fy_data = np.array(fy_data)
px_data = np.array(px_data)
py_data = np.array(py_data)


# set plot space and scatter plot data

fig, ax = plt.subplots()
plt.scatter(fx_data, fy_data, s=6, c="r")
plt.scatter(px_data, py_data, s=6, c="g")


# Make linear fitting using numpy and plot fitted line

z = np.polyfit(fx_data, fy_data, 1)
p = np.poly1d(z)
plt.plot(fx_data, p(fx_data), linewidth=1.0 )


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

#max_ticks_spacer = (max(x_data) - min(x_data)) / 4.0
#max_ticks_spacer = round(max_ticks_spacer, 1)
#
#ax.xaxis.set_major_locator(MultipleLocator(max_ticks_spacer))
#ax.yaxis.set_major_locator(MultipleLocator(max_ticks_spacer))
#
#ax.xaxis.set_minor_locator(MultipleLocator(max_ticks_spacer/2.0))
#ax.yaxis.set_minor_locator(MultipleLocator(max_ticks_spacer/2.0))
#

ax.xaxis.set_major_locator(AutoLocator())
ax.yaxis.set_major_locator(AutoLocator())
ax.tick_params(which='both', width=1.0, length=3)

plt.title("Fitting: Original data", fontsize = 12)
plt.xlabel("Experimental data", fontsize = 12)
plt.ylabel("Fitted data", fontsize = 12)

plt.tight_layout()


# filename, file_extension = os.path.splitext(sys.argv[1])
plt.savefig(PNGFile)
plt.savefig(PSFile)

print('Info:   ','Normal termination'                         )
