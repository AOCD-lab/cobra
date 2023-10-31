#!/usr/bin/env python3 -B

""" ---------------------------------------------------------------------------
This script runs the MLR code and exctracts Max R2 and adjusted R2
cavolo

To be run as:
   python RunMLR.py -m sys08.matrix

Input:   
   MatrixFile : = myfile.matrix       Matrix describing the dataset to be learned

Output:
   OutputFile : = myfile.out          Output file with all training informations
   R2File     : = myfile.r2           Outputfile having inside R2 and R2-adj 

@author: Zhen Cao, Luigi Cavallo  - September 2022
--------------------------------------------------------------------------- """

from pylab import *
import argparse
import subprocess
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from set_variables import *


# set variables
MLRBinary, PYTHONHOME = GetVariables()

DATAFile  = sys.argv[1]

COEF_File  = sys.argv[1].replace("matrix", "boot_coef")
PRED_File  = sys.argv[1].replace("matrix", "boot_pred")


#PNGFile  = sys.argv[1].replace("loo_dat", "loo_dat.png")
#PSFile   = sys.argv[1].replace("loo_dat", "loo_dat.ps")



RUN_CHECK_COEF = PYTHONHOME + "Plots/check_boot_coef.py"
RUN_CHECK_PRED = PYTHONHOME + "Plots/check_boot_pred.py"
RUN_PLOTS      = PYTHONHOME + "Plots/plot_boot_coef.py"

subprocess.run(["python", RUN_CHECK_COEF, COEF_File])
subprocess.run(["python", RUN_CHECK_PRED, PRED_File])

subprocess.run(["python", RUN_PLOTS, sys.argv[1] ])

