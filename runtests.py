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

REORDER_MATRIX   = PYTHONHOME + "Utilities/matrix_reorder.py"
NORMALIZE_MATRIX = PYTHONHOME + "Utilities/matrix_normalize.py"

RUN_MLR   = PYTHONHOME + "Tests/mlr.py"
RUN_LOO   = PYTHONHOME + "Tests/loo.py"
RUN_YRAND = PYTHONHOME + "Tests/y_randomization.py"
RUN_BOOT  = PYTHONHOME + "Tests/bootstrap.py"
RUN_PRED  = PYTHONHOME + "Tests/prediction.py"
RUN_BAGS  = PYTHONHOME + "Tests/optimization_cycles.py"
RUN_PCS   = PYTHONHOME + "Tests/pcs.py"


# get command line parameters

parser = argparse.ArgumentParser()

parser.add_argument("-m", "--matrix",               help = "Missing Matrix file")
parser.add_argument("-n", "--no_of_cycles",         help = "Missing No of optimization cycles")
parser.add_argument("-t", "--percentage_top_preds", help = "Missing Percentage of predicted systems: 0.1 = 10% predicted")
parser.add_argument("-b", "--percentage_bootstrap", help = "Missing Percentage of predicted systems: 0.2 = 20% predicted")
parser.add_argument("-o", "--percentage_cycles",    help = "Missing Percentage of top systems in the optimizatino cycles: 0.3 = 30% predicted")
parser.add_argument("-d", "--direction",            help = "Missing if up or down reordering:  keywords up/dw")
parser.add_argument("-c", "--cutoff",               help = "Missing cutoff on top value in training dataset: 0.8 = Max experimental performance * 0.8")

args = parser.parse_args()

if (not args.matrix)        \
or (not args.no_of_cycles)  \
or (not args.percentage_top_preds) \
or (not args.percentage_bootstrap) \
or (not args.percentage_cycles) \
or (not args.direction)  \
or (not args.cutoff)  :
   print(' Usage:  run_reorder.py -m/--matrix file.matrix')
   print('                        -n/--no_of_cycles  No of randomization/bootstrap/optimization cycles ')
   print('                        -t/--precentage_top_preds fraction of top/bottom systems to predict: 0.1 = 10% predicted')
   print('                        -b/--precentage_bootstrap fraction of systems out of the bags:  0.2 = 20% held out')
   print('                        -o/--precentage_cycles fraction of systems out in the optimization cycles:  0.3 = 30% held out')
   print('                        -d/--direction up or down: keywords up/dw')
   print('                        -c/--cutoff cutoff to define TP/TN: 0.8 = Max experimental performance * 0.8')
   exit()


# set system dependent variables

MATRIX            =  args.matrix
BACKUP_MATRIX     = "backup.matrix"
NORMALIZED_MATRIX = "NM-" + args.matrix
REORDERED_MATRIX  = "NM-" + args.matrix
R2MIN_MATRIX      = "Rm-" + args.matrix
R2MIN_NM_MATRIX   = "Rm-NM-" + args.matrix
TMP_MATRIX        = "tmp.matrix"


# save original matrix

subprocess.run(["cp", args.matrix, BACKUP_MATRIX])


# Set in matrix that 2nd line = 1 for writing best matrix

file = open(BACKUP_MATRIX, "r")
file_lines = ( file.readlines() )
file.close()

file_lines[1] = "1  \n"

file = open(args.matrix, "w") 
file.write("".join(file_lines)) 
file.close()


# Print input data into basename.info

BASE_INFO = MATRIX.replace(".matrix", "")

file = open(BASE_INFO+".inf", "w")
file.write("CSV file                                            : " + BASE_INFO + "\n")
file.write("No of randomizaiton/bootstrap/optimization cycles   : " + args.no_of_cycles + "\n")  
file.write("% of top/bottom systems to predict                  : " + args.percentage_top_preds + "\n")
file.write("% of systems out of the bag in the bootstrap cycles : " + args.percentage_bootstrap + "\n")
file.write("% of systems out in the optimization cycles         : " + args.percentage_cycles + "\n")
file.write("Ranking systems upward or downward                  : " + args.direction + "\n")
file.write("cutoff to define TP/TN                              : " + args.cutoff + "\n")
file.close()  

# normalize and reorder matrix

print(' Reordering and normalizing matrix...')
subprocess.run(["python", REORDER_MATRIX, "-m", args.matrix, "-d", "up", "-o", TMP_MATRIX])
subprocess.run(["cp", TMP_MATRIX, args.matrix])
subprocess.run(["python", NORMALIZE_MATRIX, "-m", TMP_MATRIX,"-o", NORMALIZED_MATRIX])


print(' Running MLR...')
subprocess.run(["python", RUN_MLR,   "-m", args.matrix])
subprocess.run(["python", RUN_MLR,   "-m", NORMALIZED_MATRIX])


print(' Running LOO...')
subprocess.run(["python", RUN_LOO,   "-m", R2MIN_MATRIX])
subprocess.run(["python", RUN_LOO,   "-m", R2MIN_NM_MATRIX])


print(' Running Y-randomization...')
subprocess.run(["python", RUN_YRAND, "-m", R2MIN_NM_MATRIX, "-n", args.no_of_cycles])

print(' Running bootstrap...')
subprocess.run(["python", RUN_BOOT,  "-m", R2MIN_NM_MATRIX, "-n", args.no_of_cycles, "-b", args.percentage_bootstrap])

print(' Running top systems predictions...')
subprocess.run(["python", RUN_PRED,  "-m", NORMALIZED_MATRIX, "-t", args.percentage_top_preds, "-d", args.direction])

print(' Running optimization cycles...')
subprocess.run(["python", RUN_BAGS,  "-m",            MATRIX, "-o", args.percentage_cycles, "-d", args.direction, "-c", args.cutoff, "-n", args.no_of_cycles])


subprocess.run(["python", RUN_PCS,   "-m", args.matrix])
