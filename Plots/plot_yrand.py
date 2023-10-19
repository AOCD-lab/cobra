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

PNGFile  = sys.argv[1].replace("yrand_dat", "yrand_dat.png")
PSFile   = sys.argv[1].replace("yrand_dat", "yrand_dat.ps")

# read mysystem.yrand_dat file

with open(DATAFile, "r") as f:
     lines = f.readlines()

y_data = []
x_data = []

for line in lines[1:]:
#   line = line[:-1]
#   if line.endswith('Fit'):
       x_data.append(float(line.split()[-3]))
       y_data.append(float(line.split()[-1]))

x_data = np.array(x_data)
y_data = np.array(y_data)

print(x_data)
print(y_data)


# set plot space and scatter plot data

fig, ax = plt.subplots()
plt.scatter(x_data, y_data, s=6, c="r")


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

#ax.xaxis.set_major_locator(AutoLocator())
#ax.yaxis.set_major_locator(AutoLocator())

plt.xlim([-1.0, 1.0])
plt.ylim([ 0.0, 1.2])
ax.xaxis.set_major_locator(FixedLocator([-1.0, -0.5, 0.0, 0.5, 1.0]))
ax.yaxis.set_major_locator(FixedLocator([0.0, 0.5, 1.0]))
  
plt.axhline(y=1.0, color='b', linestyle='--', lw=1)

ax.tick_params(which='both', width=1.0, length=3)

plt.title("Y-randomization plot", fontsize = 12)
plt.xlabel("Pearson coefficient", fontsize = 12)
plt.ylabel("Scaled R2", fontsize = 12)

plt.tight_layout()


# filename, file_extension = os.path.splitext(sys.argv[1])
plt.savefig(PNGFile)
plt.savefig(PSFile)

print('Info:   ','Normal termination'                         )
