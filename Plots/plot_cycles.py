import matplotlib.pyplot as plt
import matplotlib
from pylab import *

import os
import numpy as np

DATAFile = sys.argv[1]

#input=open(DATAFile,"r")


with open(DATAFile, "r") as f:
     lines = f.readlines()





a=[1, 2, 3, 4]
x=[]
y=[]
z=[]

for line in lines[1:]:
      line = line[:-1]
      word = line.split()
#     a.append(eval(word[0]))
      x.append(eval(word[5]))
      y.append(eval(word[6]))
      z.append(eval(word[7]))

a = np.array(a)
x = np.array(x)
y = np.array(y)
z = np.array(z)


plt.rcParams.update({ 'font.sans-serif': 'Myriad Pro', 'font.family': 'sans-serif'} )

fig = plt.figure()
fig.set_figwidth(3.0)
fig.set_figheight(3.0)
gs = fig.add_gridspec(1,3, hspace=0, wspace=0)

#plt.title("Optimization cycles", fontsize = 12)

axs = gs.subplots(sharex=False, sharey=True)

axs[0].set_ylim(bottom=0.0, top=1.2)
axs[0].set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
axs[0].set_ylabel('Score')

axs[1].set_xlabel('Optimization cycle')

axs[0].set_title('Accuracy',  y=1.0, pad=-15, fontsize=10)
axs[1].set_title('Precision', y=1.0, pad=-15, fontsize=10)
axs[2].set_title('Recall',    y=1.0, pad=-15, fontsize=10)


for ax in axs:
    ax.set_xticks([1, 2, 3, 9 ])
    ax.tick_params(axis='x', labelsize=9)
    ax.tick_params(axis='y', labelsize=9)

axs[1].tick_params(axis='y', which='both', left=False) 
axs[2].tick_params(axis='y', which='both', left=False) 

axs[0].bar(a, x, width=1.0, color="green", edgecolor="black")
axs[1].bar(a, y, width=1.0, color="red",   edgecolor="black")
axs[2].bar(a, z, width=1.0, color="blue",  edgecolor="black")


# Hide x labels and tick labels for all but bottom plot.
for ax in axs:
    ax.label_outer()

    for axis in ['top','bottom','left','right']:
        ax.spines[axis].set_linewidth(1.0)

plt.tight_layout()

#filename, file_extension = os.path.splitext(DATAFile)
#plt.savefig(filename+".ps")
#plt.savefig(filename+".png")

PNGFile  = sys.argv[1].replace("cycles_stat", "cycles_stat.png")
PSFile   = sys.argv[1].replace("cycles_stat", "cycles_stat.ps")
plt.savefig(PNGFile)
plt.savefig(PSFile)



#plt.show()
