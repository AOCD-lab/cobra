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
import os
import shutil
import numpy as np

from set_variables import *
# -------------


def GetFiles():

    """ ----------------------------------------------------  
    Handles input/output and excutable files
   
    MatrixFile := matrix file name, i.e., sys08.matrix
    OutputFile := output file name, i.e., sys08.out
    R2File     := record the larget R^2 and the adjusted R^2
    ---------------------------------------------------- """
  
  
  # get input and output file names

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--matrix", help = "Missing Matrix file")

    args       = parser.parse_args()    

    if not args.matrix:
       print(' Usage: run_mlr.py -m/--matrix sys08.matrix')
       exit()
        
        
    MatrixFile = args.matrix
    OutputFile = MatrixFile.replace("matrix","mlr_out")
    R2File     = MatrixFile.replace("matrix","mlr_r2")
        

  # All done, return

    return MatrixFile, OutputFile, R2File

# --- End of GetFiles --------------------------------------


def GetR2(OutputFile):

    """ -------------------------------------------------------------
    get R2 and other parameters from output file 

    OutputFile         := output training file , e.g.  matrix.out
    R2File             := output file with R^2 and adjusted R^2
    no_of_systems      := number of systems in the matrix
    no_of_electronics  := number of electronic descriptors
    no_of_sterics      := number of steric descriptors
    R2                 := max R2 in the training
    ------------------------------------------------------------- """

    error_values = []
    
    with open(OutputFile,"r") as f:
         for line in f:

             if ("Number of systems" in line): 
                no_of_systems = float(line.split()[4])
           
             if ("Number of Electronic descriptors" in line): 
                no_of_electronics = float(line.split()[5])
           
             if ("Number of Steric descriptors" in line): 
                no_of_sterics = float(line.split()[5])
           
             if ("Max R2" in line) and ("pair" not in line): 
                R2 = float(line.split()[2])


             if ("Fit" in line) and ("Fitted" not in line):
                    error_values.append(float(line.split()[4]))
           
    error_values = np.array(error_values)
    MAE_fit = np.mean(np.abs(error_values))
 
    return (no_of_systems, no_of_electronics, no_of_sterics, R2, MAE_fit)
# ------------------------------------------------


def main():
    
  # get input and output files from GetFiles() and path to MLR.x from GetVariables()

    MatrixFile, OutputFile, R2File = GetFiles()
    MLRBinary = GetVariables()


  # run the code

    run = MLRBinary + " " + MatrixFile + " > " + OutputFile

    os.system(run)
    
    
  # get R^2 and other data from output file analysis

    no_of_systems, no_of_electronics, no_of_sterics, R2, MAE_fit = GetR2(OutputFile)
 
    
  # Calculate adjusted R2 and print out

    no_of_descriptors = no_of_electronics + no_of_sterics
    R2_adj = 1.0 - (1.0 - R2)*(no_of_systems - 1)/(no_of_systems - no_of_descriptors - 1)

    with open(R2File, "w") as f:
         f.write( "{:16s}".format("   R2      R2_adj   MAE_fit") + '\n' )
         f.write( "{:8.3f}".format(R2) + "{:8.3f}".format(R2_adj) )
         f.write( "{:8.3f}".format(MAE_fit) + '\n' )
  

    return()
#------------------------------------------------------------------------------

    
if __name__ == '__main__':
    main()
# --------
