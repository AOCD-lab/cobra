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


    OUTFile   = DATFile.replace("", "mae-pred-boh")
    PRED_File = DATFile.replace("", "mae-pred-boh")

    return DATFile, OUTFile
# --- End of GetFiles --------------------------------------

def main():
    
  # get input and output files

    DATFile, OUTFile = GetFiles()


    with open(DATFile, "r") as f:
         lines = f.readlines()

    Err_exp = []
    Err_fit = []

    for line in lines:
        if ('MAE' not in line):
           Err_exp.append  (float(line.split()[-2]))
           Err_fit.append  (float(line.split()[-1]))
 
    Err_exp     = np.array(Err_exp)
    Err_exp_ave = np.mean(np.absolute(Err_exp))
    Err_exp_std = np.std(np.absolute(Err_exp), ddof=1)

    Err_fit     = np.array(Err_fit)
    Err_fit_ave = np.mean(np.absolute(Err_fit))
    Err_fit_std = np.std(np.absolute(Err_fit), ddof=1)


# now remove outliers
    
    clean_Err_exp = []
    clean_Err_fit = []

    for e in range(len(Err_fit)):
        if np.absolute(Err_fit[e] - Err_fit_ave) < 4.0*Err_fit_std: 
           clean_Err_fit.append(Err_fit[e])
           
        if np.absolute(Err_exp[e] - Err_exp_ave) < 4.0*Err_exp_std:
           clean_Err_exp.append(Err_exp[e])

    clean_Err_exp     = np.array(clean_Err_exp)
    clean_Err_exp_ave = np.mean(np.absolute(clean_Err_exp))
    clean_Err_exp_std = np.std(np.absolute(clean_Err_exp), ddof=1)

    clean_Err_fit     = np.array(clean_Err_fit)
    clean_Err_fit_ave = np.mean(np.absolute(clean_Err_fit))
    clean_Err_fit_std = np.std(np.absolute(clean_Err_fit), ddof=1)
    

#   with open(OUTFile, "w") as f:
#        f.write("{:8.3f}".format(Err_exp_ave) + ' +/-'   
#               +"{:7.3f}".format(Err_exp_std)
#               +"{:9.3f}".format(Err_fit_ave) + ' +/-'   
#               +"{:7.3f}".format(Err_fit_std) 
#               +"{:12.3f}".format(clean_Err_exp_ave) + ' +/-'   
#               +"{:7.3f}".format(clean_Err_exp_std)
#               +"{:9.3f}".format(clean_Err_fit_ave) + ' +/-'   
#               +"{:7.3f}".format(clean_Err_fit_std) + ' \n'  )




    with open("EXPY_FILE", "w") as f:
         for e in range(len(clean_Err_exp)):
             f.write("{:8.3f}".format(clean_Err_exp[e]) + ' \n'  )



    with open("FITT_FILE", "w") as f:
         for e in range(len(clean_Err_fit)):
             f.write("{:8.3f}".format(clean_Err_fit[e]) + ' \n'  )




    return()
# --- End of main run_yrand.py -------------------------------

        
#==============================================================================
if __name__ == '__main__':
     main()
