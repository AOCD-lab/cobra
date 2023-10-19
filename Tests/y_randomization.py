#!/usr/bin/env python3 -B

""" ---------------------------------------------------------------------------

This script runs Y-randomization test by running a series of MLR tests 
by shuffling the experimental data in the input matrix file. It returns 
the Pearson correlation coefficient between the unshuffled and shuffled 
experimental data, plus the R2 value from MLR on the shuffled data.

To be run as:
   python run_yrand.py -m/--matrix  myfile.matrix  -n/ncycles 100

Input:
   MatrixFile : = myfile.matrix      Matrix with the dataset to be learned.
   ncycles    : = integer            Runtime parameter with number of 
                                     y-randomization cycles.
Output:
   YrandFile : = myfile.yrand_dat    File with indices of shuffling, Pearson
                                     coefficient and R2 for all cycles. Both
                                     scaled and unscaled R2 values are reported.
   YR2File   : = myfile.yrand_yr2    File with Y2R prediction quality score.

@author: Zhen Cao, Luigi Cavallo
--------------------------------------------------------------------------- """

import argparse
import shutil
import sys
import os
import numpy as np
from scipy import stats

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Utilities.set_variables import *
from Utilities.matrix_operation import *


# ---------------------


def GetFiles():

    """ -------------------------------------------------------------------
    Handles input/output and excutable files

    YrandFile  : = myfile.dat   stores indices of shuffling, Pearson and R2
    YR2File    : = myfile.yr2   File with Y2R prediction quality score.

    ------------------------------------------------------------------- """

  # get the input and output file names

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--matrix",  help = "Missing Matrix file") 
    parser.add_argument("-n", "--ncycles", help = "Missing number of shuffle cycles")

    args = parser.parse_args()

    if (not args.matrix) or (not args.ncycles) :   
       print('Usage:  run_yrand.py -m/--matrix  input.matrix  -n/ncycles No. of cycles (integer)')
       exit()


    MatrixFile     = args.matrix
    no_of_shuffles = int(args.ncycles)

    TempFile  = "tmp.matrix"
    YrandFile = MatrixFile.replace("matrix", "yrand_dat")
    YR2File   = MatrixFile.replace("matrix", "yrand_yr2")

    return MatrixFile, TempFile, YrandFile, YR2File, no_of_shuffles
# --- End of GetFiles --------------------------------------

def main():
    
  # get input and output files

    MatrixFile, TempFile, YrandFile, YR2File, no_of_shuffles = GetFiles()
    MLRBinary, PYTHONHOME = GetVariables()


  # call read_matrix to read matrix_file

    title             , print_flag             , normalization_flag   , \
    shift_flag        , skipped_systems        , no_of_systems        , \
    no_of_electronics , no_of_sterics          , no_of_buried_volumes , \
    system_tags       , experimental_tag       , experimental_data    , \
    electronic_tags   , electronic_descriptors , radius_proximal      , \
    radius_distal     , buried_volumes         = read_matrix(MatrixFile) 


  # initialize arrays

    indices               = np.arange(no_of_systems, dtype=int)
    shuffled_indices      = np.zeros ( (no_of_shuffles+1, no_of_systems), dtype=int)
    shuffled_experimental = np.zeros (no_of_systems)
    r2_values             = np.zeros (no_of_shuffles + 1)
    pearson_values        = np.zeros (no_of_shuffles + 1)


  # set indices to shuffle experimental data - start with unshuffled

    shuffled_indices[0][:] = indices

    np.random.seed(42)
    for s in range(1, no_of_shuffles+1):
        np.random.shuffle(indices)
        shuffled_indices[s][:] = indices
      
      
  # indices of all shuffles generated, run MLR on each of them.
  # first reorder experimental data according to shuffled_indices in cycle.
  # then calculate pearson between shuffled and unshuffled experimental data.

    for s in range (0, no_of_shuffles+1):
        for i in range (0,no_of_systems):
            shuffled_experimental[i] = experimental_data[shuffled_indices[s][i]] 
        pearson_values[s] = stats.pearsonr(experimental_data, shuffled_experimental)[0]


      # call write_matrix to write matrix_file for shuffle cycle 
      # run MLR code and extract data


      # call write_matrix to write matrix_file for loo calculation

        write_matrix(TempFile              , title             , print_flag             ,
                     normalization_flag    , shift_flag        , skipped_systems        ,
                     no_of_systems         , no_of_electronics , no_of_sterics          ,
                     no_of_buried_volumes  , system_tags       , experimental_tag       ,
                     shuffled_experimental , electronic_tags   , electronic_descriptors ,
                     radius_proximal       , radius_distal     , buried_volumes         )

        
        run = MLRBinary + " " + TempFile + " > temp.out"
        os.system(run)


      # get R2 value for this shuffle 

        with open('temp.out', "r") as f:
             lines = f.readlines()
             for line in lines:
                 if ("Max R2" in line) :
                    r2_values[s] = float(line.split()[2])
        os.system('rm temp.out')
        os.system('rm tmp.matrix')


  # all shuffle cycles completed, start analysis
    
    with open(YrandFile, "w") as f:
         f.write("{}".format("1. Indeces of shuffled systems.  ")
                +"{}".format("2. Pearson correlation coefficient.  ")
                +"{}".format("3. R2.  ") 
                +"{}".format("4. Scaled R2.") + '\n')

         for s in range(no_of_shuffles+1):
             for i in range(no_of_systems):
                 f.write("{:5d}".format(shuffled_indices[s][i]) )

             f.write("{:8.3f}".format(pearson_values[s]) 
                    +"{:8.3f}".format(r2_values[s]) 
                    +"{:8.3f}".format(r2_values[s]/r2_values[0]) + '\n')

    r2_max = np.amax(r2_values[1:])
    r2_ave = np.mean(r2_values[1:])
    r2_std = np.std(r2_values[1:], ddof=1)
    with open(YR2File, "w") as f:
         f.write("{}".format("Max R2   Scaled Max R2   Average and STD values ") + '\n')
         f.write("{:8.3f}".format(r2_max) 
                +"{:8.3f}".format(r2_max/r2_values[0]) 
                +"{:8.3f}".format(r2_ave) +' +/-' 
                +"{:6.3f}".format(r2_std) 
                +"{:8.3f}".format(r2_ave/r2_values[0]) +' +/-' 
                +"{:6.3f}".format(r2_std/r2_values[0]) + '\n')


    return()
# --- End of main run_yrand.py -------------------------------

        
#==============================================================================
if __name__ == '__main__':
     main()
