#!/usr/bin/env python3 -B

""" ---------------------------------------------------------------------------

This script runs Leave one out cross validation and calculate Q^2

To be run as:
   python runloo.py -m myfile.matrix

Input:
   MatrixFile : = myfile.matrix       Matrix describing the dataset to be learned

Output:
   LOOFile  : = myfile.loo_dat      Output file with experimental and LOOCV values
   Q2File   : = myfile.loo_q2       Output file having inside Q2 and MAE

@author: Zhen Cao, Luigi Cavallo
--------------------------------------------------------------------------- """

import argparse
import shutil
import numpy as np
import sys
import os

from matrix_operation import *

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Utilities.set_variables import *


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
    TempFile   = "tmp.matrix"
    LOOFile    = MatrixFile.replace("matrix", "loo_dat")
    Q2File     = MatrixFile.replace("matrix", "loo_q2")
    MAEFile    = MatrixFile.replace("matrix", "loo_mae")
    
    return MatrixFile, TempFile, LOOFile, Q2File, MAEFile     
# --- End of GetFiles -----------------------------

def main():
    
  # get input and output files

    MatrixFile, TempFile, LOOFile, Q2File, MAEFile = GetFiles()
    MLRBinary, PYTHONHOME = GetVariables()


  # call read_matrix to read matrix_file

    title             , print_flag             , normalization_flag   , \
    shift_flag        , skipped_systems        , no_of_systems        , \
    no_of_electronics , no_of_sterics          , no_of_buried_volumes , \
    system_tags       , experimental_tag       , experimental_data    , \
    electronic_tags   , electronic_descriptors , radius_proximal      , \
    radius_distal     , buried_volumes         = read_matrix(MatrixFile) 


  # loop over systems excluding them one by one

    loo_system = [1, 0]
    loo_values = []
    for l in range(no_of_systems):
        loo_system[1] = l+1

    
      # call write_matrix to write matrix_file for loo calculation

        write_matrix(TempFile             , title             , print_flag             ,
                     normalization_flag   , shift_flag        , loo_system             ,
                     no_of_systems        , no_of_electronics , no_of_sterics          ,
                     no_of_buried_volumes , system_tags       , experimental_tag       ,
                     experimental_data    , electronic_tags   , electronic_descriptors ,
                     radius_proximal      , radius_distal     , buried_volumes         )


      # run MLR on the temporary matrix file skipping one system

        run = MLRBinary + " " + TempFile + " > temp.out"
        os.system(run)


      # get predicted value for this matrix

        with open('temp.out', "r") as f:
             lines = f.readlines()
             for line in lines:
                 if ("LOO   " in line) :
                    loo_values.append(float(line.split()[3]))
        os.system('rm temp.out')
    os.system('rm  tmp.matrix')

    
  # loo cycles completed, calculate Q2, MAE_loo and print out

    loo_values = np.array(loo_values)
    corr_matrix = np.corrcoef(experimental_data, loo_values)
    corr = corr_matrix[0,1]
    Q2 = corr**2

    no_of_descriptors = no_of_electronics + no_of_sterics

    with open(LOOFile, "w") as f:
         f.write( "{:32s}".format(' System      Experiment     LOO \n' ) )
         for i in range(no_of_systems) :
               f.write( "{:12s}  ".format(system_tags[i])  
                      + "{:10.3f}".format(experimental_data[i])  
                      + "{:10.3f}".format(loo_values[i]) + '\n')
      
      
    MAE_loo = np.mean(np.abs(experimental_data - loo_values))

    with open(Q2File, "w") as f:
         f.write( "{:36s}".format("     Q2        MAE_LOO") + '\n' )
         f.write( "{:10.3f}".format(Q2) )
         f.write( "{:10.3f}".format(MAE_loo) + '\n' )

    return()
# --- End of main run_loo.py -------------------------------

        
#==============================================================================
if __name__ == '__main__':
     main()
