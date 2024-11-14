#!/usr/bin/env python3 -B

""" ---------------------------------------------------------------------------

This script assembles results from all tests and write a file for the radar plot

To be run as:
   python pcs.py -m myfile.matrix

Input:
   MatrixFile : = myfile.matrix       Matrix describing the dataset to be learned

Output:
   OUTFile  : = myfile.pcs          Output file with summary of all data

@author: Zhen Cao, Luigi Cavallo
--------------------------------------------------------------------------- """

import argparse
import os
import sys
import shutil
import numpy as np

# ---------------------


def GetFiles():

    """ ----------------------------------------------------
    Handles input/output and excutable files

    MatrixFile  := matrix file name, i.e., myfile.matrix

    ---------------------------------------------------- """

  # get the input and output file names

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--matrix", help = "Missing Matrix file")

    args       = parser.parse_args()

    if (not args.matrix) :
       print(' Usage:  pcs.py -m/--matrix file.matrix')
       exit()


    MatrixFile = args.matrix
    Basename = os.path.splitext(MatrixFile)[0]

    MLRFile    = "NM-"    + Basename + ".mlr_r2"
    LOOFile    = "Rm-NM-" + Basename + ".loo_q2"
    YRANDFile  = "Rm-NM-" + Basename + ".yrand_yr2"
    BOOTFile   = "Rm-NM-" + Basename + ".boot_mae"
    PREDFile   = "NM-"    + Basename + ".pred_mae"
    CYCLEFile  =            Basename + ".cycles_stat"
 
    OUTFile   = MatrixFile.replace("matrix", "pcs")
    
    return Basename, MLRFile, LOOFile, YRANDFile, BOOTFile, PREDFile, CYCLEFile, OUTFile
# --- End of GetFiles -----------------------------

def main():
    
  # get input and output files

    
    Basename, MLRFile, LOOFile, YRANDFile, BOOTFile, PREDFile, CYCLEFile, OUTFile = GetFiles()


# read MLR

    file = open(MLRFile, "r")
    file_lines = ( file.readlines() )
    file.close()
    words = []
    words = file_lines[1].split()
    words = np.array(words).astype(np.float)
    mlr_r2 = words[0]
    mlr_ar2 = words[1]
    mlr_mae = words[2]


# read LOO

    file = open(LOOFile, "r")
    file_lines = ( file.readlines() )
    file.close()
    words = []
    words = file_lines[1].split()
    words = np.array(words).astype(np.float)
    loo_q2 = words[0]
    loo_mae = words[1]


# read YRAND

    file = open(YRANDFile, "r")
    file_lines = ( file.readlines() )
    file.close()
    words = []
    words = file_lines[1].split()
    words.pop(6)
    words.pop(3)
    words = np.array(words).astype(np.float)
    yrand_syr2_max = words[1]
    yrand_syr2_ave = words[4]


# read BOOT
   
    file = open(BOOTFile, "r")
    file_lines = ( file.readlines() )
    file.close()
    words = []
    words = file_lines[1].split()   
    words.pop(2)
    words.pop(0)
    words = np.array(words).astype(np.float)
    boot_mae_fit = words[0]
    words = file_lines[2].split()   
    words.pop(2)
    words.pop(0)
    words = np.array(words).astype(np.float)
    boot_mae_cff = words[0]


# read PRED
       
    file = open(PREDFile, "r")
    file_lines = ( file.readlines() )
    file.close()
    words = [] 
    words = file_lines[1].split()   
    words = np.array(words).astype(np.float)
    pred_mae = words[2]


# read CYCLES
       
    file = open(CYCLEFile, "r")
    file_lines = ( file.readlines() )
    file.close()
    words = []
    words = file_lines[4].split()[5:8]
    words = np.array(words).astype(np.float)
    cycle_pre = words[0]
    cycle_acc = words[1]
    cycle_rec = words[2]


# Summarize all data in .pcs file

    PCS = np.zeros(13)

    PCS[0]  =  mlr_ar2
    PCS[1]  =  mlr_mae
    PCS[2]  =  loo_q2
    PCS[3]  =  loo_mae
    PCS[4]  =  yrand_syr2_max
    PCS[5]  =  yrand_syr2_ave
    PCS[6]  =  boot_mae_fit
    PCS[7]  =  boot_mae_cff
    PCS[8]  =  pred_mae
    PCS[9]  =  cycle_pre
    PCS[10] =  cycle_acc
    PCS[11] =  cycle_rec

    with open(OUTFile, "w") as f:
         f.write("{:10s}".format('             ') + "{:10s}".format(Basename) + '\n' )
         f.write("{:10s}".format('$R^2$        ') + "{:8.3f}".format(PCS[0])  + '\n' )
         f.write("{:10s}".format('$MAE_{Fit}$  ') + "{:8.3f}".format(PCS[1])  + '\n' )
         f.write("{:10s}".format('$Q^2$        ') + "{:8.3f}".format(PCS[2])  + '\n' )
         f.write("{:10s}".format('$MAE_{LOO}$  ') + "{:8.3f}".format(PCS[3])  + '\n' )
         f.write("{:10s}".format('$SR^2_{Max}}$') + "{:8.3f}".format(PCS[4])  + '\n' )
         f.write("{:10s}".format('$SR^2_{Av}$  ') + "{:8.3f}".format(PCS[5])  + '\n' )
         f.write("{:10s}".format('$MAD_{BP}$   ') + "{:8.3f}".format(PCS[6])  + '\n' )
         f.write("{:10s}".format('$MAD_{BC}$   ') + "{:8.3f}".format(PCS[7])  + '\n' )
         f.write("{:10s}".format('$MAE_{T20}$  ') + "{:8.3f}".format(PCS[8])  + '\n' )
         f.write("{:10s}".format('$Acc_{80}$   ') + "{:8.3f}".format(PCS[9])  + '\n' )
         f.write("{:10s}".format('$Pre_{80}$   ') + "{:8.3f}".format(PCS[10]) + '\n' )
         f.write("{:10s}".format('$Rec_{80}$   ') + "{:8.3f}".format(PCS[11]) + '\n' )


# write data for radar plot. Manipulate some metrics to have 1.0 as ideal behavior

    PCS[0]  =       mlr_ar2        
    PCS[1]  =  1.0 -mlr_mae        
    PCS[2]  =       loo_q2         
    PCS[3]  =  1.0 -loo_mae        
    PCS[4]  =  1.0 -yrand_syr2_max 
    PCS[5]  =  1.0 -yrand_syr2_ave 
    PCS[6]  =  1.0 -boot_mae_fit   
    PCS[7]  =  1.0 -boot_mae_cff   
    PCS[8]  =  1.0 -pred_mae       
    PCS[9]  =       cycle_pre      
    PCS[10] =       cycle_acc      
    PCS[11] =       cycle_rec      

    WEB_PCS_TABLE = OUTFile.replace(".pcs", ".radar_pcs")

    with open(WEB_PCS_TABLE, "w") as f:
         f.write("{:20s}".format('               ') + "{:10s}".format(Basename) + '\n' )
         f.write("{:20s}".format('$R^2$          ') + "{:8.3f}".format(PCS[0])  + '\n' )
         f.write("{:20s}".format('$1-MAE_{Fit}$  ') + "{:8.3f}".format(PCS[1])  + '\n' )
         f.write("{:20s}".format('$Q^2$          ') + "{:8.3f}".format(PCS[2])  + '\n' )
         f.write("{:20s}".format('$1-MAE_{LOO}$  ') + "{:8.3f}".format(PCS[3])  + '\n' )
         f.write("{:20s}".format('$1-SR^2_{Max}}$') + "{:8.3f}".format(PCS[4])  + '\n' )
         f.write("{:20s}".format('$1-SR^2_{Av}$  ') + "{:8.3f}".format(PCS[5])  + '\n' )
         f.write("{:20s}".format('$1-MAD_{BP}$   ') + "{:8.3f}".format(PCS[6])  + '\n' )
         f.write("{:20s}".format('$1-MAD_{BC}$   ') + "{:8.3f}".format(PCS[7])  + '\n' )
         f.write("{:20s}".format('$1-MAE_{T20}$  ') + "{:8.3f}".format(PCS[8])  + '\n' )
         f.write("{:20s}".format('$Acc_{80}$     ') + "{:8.3f}".format(PCS[9])  + '\n' )
         f.write("{:20s}".format('$Pre_{80}$     ') + "{:8.3f}".format(PCS[10]) + '\n' )
         f.write("{:20s}".format('$Rec_{80}$     ') + "{:8.3f}".format(PCS[11]) + '\n' )


#==============================================================================
if __name__ == '__main__':
     main()

