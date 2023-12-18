#!/usr/bin/env python3 -B

""" ---------------------------------------------------------------------------

This script runs Leave one out cross validation and calculate Q^2

To be run as:
   python runloo.py -m sys08.matrix

Input:
   MatrixFile : = myfile.matrix       Matrix describing the dataset to be learned

Output:
   LOOFile  : = myfile.loo          Output file with experimental and LOOCV values
   Q2File   : = myfile.q2           Output file having inside R2 
   MAEFile  : = myfile.mae_loo      Output file having inside MAE from LOOCV

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

    MatrixFile  := matrix file name, i.e., sys08.matrix
    LOOFile     := stores experimental and LOO values
    Q2File      := stores Q2 

    ---------------------------------------------------- """

  # get the input and output file names

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--matrix", help = "Missing Matrix file")

    args       = parser.parse_args()

    if (not args.matrix) :
       print(' Usage:  run_loo.py -m/--matrix file.matrix')
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


# calculate PCS

    PCS = np.zeros(13)


  # last reference values

    aR2      =  0.903
    MAE_Fit  =  0.198
    Q2       =  0.852
    MAE_LOO  =  0.289
    aYR2_Max =  0.817
    aYR2_Ave =  0.279
    MAE_PR   =  0.179
    MAE_CF   =  0.170
    MAE_T20  =  0.403
    Acc_80   =  0.743
    Pre_80   =  0.762
    Rec_80   =  0.776


    PCS[1]  =   (mlr_ar2        - aR2      )
    PCS[2]  =  -(mlr_mae        - MAE_Fit  )
    PCS[3]  =   (loo_q2         - Q2       )
    PCS[4]  =  -(loo_mae        - MAE_LOO  )
    PCS[5]  =  -(yrand_syr2_max - aYR2_Max )
    PCS[6]  =  -(yrand_syr2_ave - aYR2_Ave )
    PCS[7]  =  -(boot_mae_fit   - MAE_PR   )
    PCS[8]  =  -(boot_mae_cff   - MAE_CF   )
    PCS[9]  =  -(pred_mae       - MAE_T20  )
    PCS[10] =   (cycle_pre      - Acc_80   )
    PCS[11] =   (cycle_acc      - Pre_80   )
    PCS[12] =   (cycle_rec      - Rec_80   )

    PCS[0] = np.sum(PCS[1:13])
    PCS[0] = PCS[0]/12.0

    with open(OUTFile, "w") as f:
         f.write("{:10s}".format('             ') + "{:10s}".format('Reference') + "{:10s}".format(Basename       ) + "{:10s}".format('Delta ') + '\n' )
         f.write("{:10s}".format('$R^2$        ') + "{:8.3f}".format(aR2     )   + "{:8.3f}".format(mlr_ar2       ) + "{:8.3f}".format(PCS[1])  + '\n' )
         f.write("{:10s}".format('$MAE_{Fit}$  ') + "{:8.3f}".format(MAE_Fit )   + "{:8.3f}".format(mlr_mae       ) + "{:8.3f}".format(PCS[2])  + '\n' )
         f.write("{:10s}".format('$Q^2$        ') + "{:8.3f}".format(Q2      )   + "{:8.3f}".format(loo_q2        ) + "{:8.3f}".format(PCS[3])  + '\n' )
         f.write("{:10s}".format('$MAE_{LOO}$  ') + "{:8.3f}".format(MAE_LOO )   + "{:8.3f}".format(loo_mae       ) + "{:8.3f}".format(PCS[4])  + '\n' )
         f.write("{:10s}".format('$SR^2_{Max}}$') + "{:8.3f}".format(aYR2_Max)   + "{:8.3f}".format(yrand_syr2_max) + "{:8.3f}".format(PCS[5])  + '\n' )
         f.write("{:10s}".format('$SR^2_{Av}$  ') + "{:8.3f}".format(aYR2_Ave)   + "{:8.3f}".format(yrand_syr2_ave) + "{:8.3f}".format(PCS[6])  + '\n' )
         f.write("{:10s}".format('$MAD_{PR}$   ') + "{:8.3f}".format(MAE_PR  )   + "{:8.3f}".format(boot_mae_fit  ) + "{:8.3f}".format(PCS[7])  + '\n' )
         f.write("{:10s}".format('$MAD_{CF}$   ') + "{:8.3f}".format(MAE_CF  )   + "{:8.3f}".format(boot_mae_cff  ) + "{:8.3f}".format(PCS[8])  + '\n' )
         f.write("{:10s}".format('$MAE_{T20}$  ') + "{:8.3f}".format(MAE_T20 )   + "{:8.3f}".format(pred_mae      ) + "{:8.3f}".format(PCS[9])  + '\n' )
         f.write("{:10s}".format('$Acc_{80}$   ') + "{:8.3f}".format(Acc_80  )   + "{:8.3f}".format(cycle_pre     ) + "{:8.3f}".format(PCS[10]) + '\n' )
         f.write("{:10s}".format('$Pre_{80}$   ') + "{:8.3f}".format(Pre_80  )   + "{:8.3f}".format(cycle_acc     ) + "{:8.3f}".format(PCS[11]) + '\n' )
         f.write("{:10s}".format('$Rec_{80}$   ') + "{:8.3f}".format(Rec_80  )   + "{:8.3f}".format(cycle_rec     ) + "{:8.3f}".format(PCS[12]) + '\n' )
         f.write("{:10s}".format('PCS     ')      + "{:8.3f}".format(PCS[0])     + '\n' )


#==============================================================================
if __name__ == '__main__':
     main()
