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

import argparse
import subprocess
import sys
import os

# set variables

sys.path.append(os.path.join(os.path.dirname(__file__), 'Utilities'))
from set_variables import *

MLRBinary, PYTHONHOME = GetVariables()



RUN_R2_RAW  = PYTHONHOME + "Plots/plot_r2_raw_data.py"              
RUN_R2_NM   = PYTHONHOME + "Plots/plot_r2_NM_data.py"               
RUN_LOO_RAW = PYTHONHOME + "Plots/plot_loo_raw_data.py"         
RUN_LOO_NM  = PYTHONHOME + "Plots/plot_loo_NM_data.py"         
RUN_YRAND   = PYTHONHOME + "Plots/plot_yrand.py"         
RUN_BOOT    = PYTHONHOME + "Plots/plot_boot.py"         
RUN_PRED    = PYTHONHOME + "Plots/plot_pred_NM_data.py"         
RUN_CYCLES  = PYTHONHOME + "Plots/plot_cycles.py"         
RUN_RADAR   = PYTHONHOME + "Plots/plot_radar.py"             

# get command line parameters

parser = argparse.ArgumentParser()

parser.add_argument("-m", "--matrix",               help = "Missing Matrix file")

args = parser.parse_args()

if (not args.matrix):
   print(' Usage:  run_reorder.py -m/--matrix file.matrix')


# set system dependent variables

INPUT_HEAD = args.matrix.replace(".matrix", "")


INP_R2_RAW =              INPUT_HEAD + ".mlr_out"
INP_R2_NM  =      "NM-" + INPUT_HEAD + ".mlr_out"
INP_LOO_RAW=   "Rm-NM-" + INPUT_HEAD + ".loo_dat"
INP_LOO_NM =      "Rm-" + INPUT_HEAD + ".loo_dat"
INP_YRAND  =   "Rm-NM-" + INPUT_HEAD + ".yrand_dat"
INP_BOOT   =   "Rm-NM-" + INPUT_HEAD + ".matrix"
INP_PRED   =      "NM-" + INPUT_HEAD + ".pred_out"
INP_CYCLES =              INPUT_HEAD + ".cycles_stat"
INP_RADAR  =              INPUT_HEAD + ".pcs"


print(' Running MLR...')
subprocess.run(["python", RUN_R2_RAW , INP_R2_RAW  ])
subprocess.run(["python", RUN_R2_NM  , INP_R2_NM   ])
subprocess.run(["python", RUN_LOO_RAW, INP_LOO_RAW ])
subprocess.run(["python", RUN_LOO_NM , INP_LOO_NM  ])
subprocess.run(["python", RUN_YRAND  , INP_YRAND   ])
subprocess.run(["python", RUN_BOOT   , INP_BOOT    ])
subprocess.run(["python", RUN_PRED   , INP_PRED    ])
subprocess.run(["python", RUN_CYCLES , INP_CYCLES  ])
subprocess.run(["python", RUN_RADAR  , INP_RADAR   ])


