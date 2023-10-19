#!/usr/bin/env python3 -B


import argparse
import os
import shutil
import numpy as np
from scipy import stats
from pylab import *

# ---------------------


def GetFiles():

    """ -------------------------------------------------------------------
    Handles input/output and excutable files

    YrandFile  : = myfile.dat   stores indices of shuffling, Pearson and R2
    ERRFile    : = myfile.yr2   File with ERR prediction quality score.
    ERRFile    : = myfile.yr2   File with Y2R prediction quality score.

    ------------------------------------------------------------------- """

  # get the input and output file names

#   parser = argparse.ArgumentParser()
#   parser.add_argument("-d", "--dat",  help = "Missing data file") 

#   args = parser.parse_args()


#   DATFile   = args.dat

    DATFile  = sys.argv[1]




    OUTFile   = DATFile.replace("boot_coef", "MAE_boot_coef_clean")
    COEF_File = DATFile.replace("boot_coef", "boot_coef_clean")

    print(DATFile)
    print(OUTFile)
    print(COEF_File)

    return DATFile, OUTFile, COEF_File
# --- End of GetFiles --------------------------------------

def main():
    
  # get input and output files

    DATFile, OUTFile, COEF_File = GetFiles()


    with open(DATFile, "r") as f:
         lines = f.readlines()

    Err_fit = []

    for line in lines:
        if ('MAE' not in line):
           Err_fit.append  (float(line.split()[-1]))
 
    Err_fit     = np.array(Err_fit)
    Err_fit_ave = np.mean(np.absolute(Err_fit))
    Err_fit_std = np.std(np.absolute(Err_fit), ddof=1)

 
# now remove outliers
    
    clean_Err_fit = []

    for e in range(len(Err_fit)):
        if np.absolute(Err_fit[e] - Err_fit_ave) < 4.0*Err_fit_std: 
           clean_Err_fit.append(Err_fit[e])

    clean_Err_fit     = np.array(clean_Err_fit)
    clean_Err_fit_ave = np.mean(np.absolute(clean_Err_fit))
    clean_Err_fit_std = np.std(np.absolute(clean_Err_fit), ddof=1)

#   with open(OUTFile, "w") as f:
#        f.write("{:8.3f}".format(clean_Err_fit_ave) + ' +/-'   
#               +"{:7.3f}".format(clean_Err_fit_std) + ' \n'  )


    with open("COEF_File", "w") as f:
         for e in range(len(clean_Err_fit)):
             f.write("{:8.3f}".format(clean_Err_fit[e]) + ' \n'  )

   
    return()
# --- End of main run_yrand.py -------------------------------

        
#==============================================================================
if __name__ == '__main__':
     main()
