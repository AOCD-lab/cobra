#!/usr/bin/env python3 -B

""" ----------------------------------------------------------------------------

This script splits the dataset into bottom and top subsets. Then fits the MLR on
the bottom subset and predicts the systems in the top subset.

To be run as:
   python predictions.py -m/--matrix  myfile.matrix  -t/top_percentage 0.1 -d/direction up/down

Input:
   MatrixFile     : = myfile.matrix    Matrix with the dataset to be learned.
   top_percentage : = float            percentage of systems put into prediction list
   direction      : = up/down          whether to predict top or bottom subsets
   
Output:
    OutputFile  = myfile.pred_out  Output file with everything on the fitting
    PRED_File   = myfile.pred_mae  MAE of predictions from experimental and fitted full dataset
    DATFile     = myfile.pred_dat  Experimental, fitted full dataset, predicted, 
                                   deviations from experimental and fitted 
   
@author: Zhen Cao, Luigi Cavallo
--------------------------------------------------------------------------- """

import argparse
import sys
import os
import numpy as np

from matrix_operation import *

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Utilities.set_variables import *


# ---------------------

def GetFiles():

    """ -------------------------------------------------------------------
    Handles input/output and excutable files

    OutputFile  = myfile.pred_out  Output file with everything on the fitting
    PRED_File   = myfile.pred_mae  MAE of predictions from experimental and fitted full dataset
    DATFile     = myfile.pred_dat  Experimental, fitted full dataset, predicted, 
                                   deviations from experimental and fitted 

    ------------------------------------------------------------------- """

  # get the input and output file names

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--matrix",  help = "Missing Matrix file") 
    parser.add_argument("-t", "--top_percentage", help = "Missing Percentage between 0.0-1.0")
    parser.add_argument("-d", "--direction", help = "Missing if up or down reordering")

    args            = parser.parse_args()

    if (not args.matrix)         \
    or (not args.top_percentage) \
    or (not args.direction)      :
       print(' Usage:  run_reorder.py -m/--matrix file.matrix    \
                                      -t/--top_precentage fraction of systems to predict  \
                                      -d/--direction up or down' )
       exit()

    MatrixFile      = args.matrix
    percentage      = float(args.top_percentage)
    updown_flag     = str(args.direction)

    if (updown_flag != 'up') and (updown_flag != 'down'):
       print(' Error:  -d/--direction flag must be up/down')
       exit()

    
    OutputFile  = MatrixFile.replace("matrix", "pred_out")
    TempFile    = MatrixFile.replace("matrix", "tmp")
    PRED_File   = MatrixFile.replace("matrix", "pred_mae")
    DATFile     = MatrixFile.replace("matrix", "pred_dat")

    return (MatrixFile, OutputFile, TempFile, PRED_File, DATFile, percentage, updown_flag)


# ---------------------
def analysis_pred(PRED_File, DATFile, system_tags, out_skipped, 
                  experimental_data, reference_fit, reference_pre) :

  # analyzes predicted experimental values from bootstrap run and writes out MAE_boot_exp
  # MAE_boot_fit.  MAEs are calculated from experimental_data and reference_fit, which 
  # contains experimental values and values from fitting the whole dataset.

  # Input:
    # PRED_File         := file where to write results of the analysis.
    # no_of_prediction  := No of systems predicted 
    # system_tags       := Labels of experimental systems in the dataset
    # experimental_data := Experimental data in the dataset
    # reference_fit     := Fitted values from MLR training on the whoe dataset.
    # boot_pred         := Predictions from MLR training during the bootstrap cycles
    #                     - array size no_of_bootstrap*no_of_prediction.

  # Output:            := results are written in file PRED_File
  # ---------------------


    MAE_boot_exp= 0.0
    MAE_boot_fit= 0.0
    difference_exp = []
    difference_fit = []

    with open(DATFile, "w") as f:
         for p in range(out_skipped[1]-1, out_skipped[-1]):
 
               # find which system is predicted
                 difference_exp.append(np.abs(reference_pre[p] - experimental_data[p]))
                 difference_fit.append(np.abs(reference_pre[p] - reference_fit[p]))

                 f.write("{:8s}  ".format(system_tags[p]) 
                        +"{:8.3f}".format(experimental_data[p])  
                        +"{:8.3f}".format(reference_fit[p])  
                        +"{:8.3f}".format(reference_pre[p])  
                        +"{:8.3f}".format(reference_pre[p] 
                                        - experimental_data[p])
                        +"{:8.3f}".format(reference_pre[p] 
                                        - reference_fit[p]) + '\n')

    with open(PRED_File, "w") as f:
         difference_exp = np.array(difference_exp)
         MAE_boot_exp   = np.mean(difference_exp)
         stdv_exp = np.std(difference_exp, ddof=1)

         difference_fit = np.array(difference_fit)
         MAE_boot_fit   = np.mean(difference_fit)
         stdv_fit = np.std(difference_fit, ddof=1)

         f.write('MAE_boot_exp' + '  StDev    '    + 'MAE_boot_fit' + '  StDev'    + '\n')
         f.write( "{:8.3f}".format(MAE_boot_exp) 
                + "{:10.3f}".format(stdv_exp) + '     '
                + "{:8.3f}".format(MAE_boot_fit) 
                + "{:10.3f}".format(stdv_fit) + '\n')
    return()

# ---------------------

def reorder_matrix(title             , print_flag             , normalization_flag   ,  
                   shift_flag        , skipped_systems        , no_of_systems        ,  
                   no_of_electronics , no_of_sterics          , no_of_buried_volumes ,  
                   system_tags       , experimental_tag       , experimental_data    ,  
                   electronic_tags   , electronic_descriptors , radius_proximal      ,  
                   radius_distal     , buried_volumes         , updown_flag          ):

# Reorders systems by increasing experimental performance if updown_flag is UP
# Reorders systems by decreasing experimental performance if updown_flag is DOWN
# Returns the ordered system_tags, experimental_data, electronic_descriptors and buried_volumes


  # defyning arrays to store reordered data

    out_tag = []
    out_exp = np.zeros(no_of_systems, dtype=float)
    out_ele = np.zeros((no_of_electronics, no_of_systems), dtype=float)
    out_vbu = np.zeros((no_of_buried_volumes, 2*no_of_systems), dtype=float)


  # get indices of experimental_data according to updown_flag

    out_indices = np.zeros(no_of_systems, dtype=int)
 
    if updown_flag == "up"   : out_indices = np.argsort(+experimental_data)
    if updown_flag == "down" : out_indices = np.argsort(-experimental_data)

  # store data in temporary arrays according to order in out_indices array

    for r in range(no_of_systems):
        out_tag.append(system_tags[out_indices[r]])
        out_exp[r] = experimental_data[out_indices[r]]

        for e in range(no_of_electronics):
            out_ele[e][r] = electronic_descriptors[e][out_indices[r]]

        for s in range(no_of_buried_volumes):
            r1 = no_of_sterics*r
            r2 = no_of_sterics*out_indices[r]
            out_vbu[s][r1] = buried_volumes[s][r2]
          
            if no_of_sterics == 2:
               out_vbu[s][r1+1] = buried_volumes[s][r2+1]


  # all done, return the reordered data

    return(out_tag, out_exp, out_ele, out_vbu)

# ---------------------

def main():
    
  # get input and output files

    MatrixFile, OutputFile, TempFile, PRED_File, DATFile, percentage, updown_flag = GetFiles()
    MLRBinary, PYTHONHOME = GetVariables()

  # call read_matrix to read matrix_file

    title             , print_flag             , normalization_flag   , \
    shift_flag        , skipped_systems        , no_of_systems        , \
    no_of_electronics , no_of_sterics          , no_of_buried_volumes , \
    system_tags       , experimental_tag       , experimental_data    , \
    electronic_tags   , electronic_descriptors , radius_proximal      , \
    radius_distal     , buried_volumes         = read_matrix(MatrixFile) 


  # initialize arrays and set skipped_systems array to indicate systems to be predicted

    no_of_prediction   = round(no_of_systems * percentage)

    out_skipped    = np.zeros((no_of_prediction+1), dtype=int)

    out_skipped[0] = no_of_prediction
    for p in range(no_of_prediction):
        out_skipped[p+1] = no_of_systems - no_of_prediction + p + 1
        
    out_tag = np.array(no_of_systems, dtype=str)
    out_exp = np.zeros(no_of_systems, dtype=float)
    out_ele = np.zeros((no_of_electronics, no_of_systems), dtype=float)
    out_vbu = np.zeros((no_of_buried_volumes, 2*no_of_systems), dtype=float)


 #  reorder matrix

    out_tag, out_exp, out_ele, out_vbu = reorder_matrix(
    title             , print_flag             , normalization_flag   ,  
    shift_flag        , out_skipped            , no_of_systems        ,  
    no_of_electronics , no_of_sterics          , no_of_buried_volumes ,  
    system_tags       , experimental_tag       , experimental_data    ,  
    electronic_tags   , electronic_descriptors , radius_proximal      ,  
    radius_distal     , buried_volumes         , updown_flag          )


  # write matrix for training the MLR model on the whole dataset

    write_matrix(TempFile             , title             , print_flag           ,
                 normalization_flag   , shift_flag        , skipped_systems      ,
                 no_of_systems        , no_of_electronics , no_of_sterics        ,
                 no_of_buried_volumes , out_tag           , experimental_tag     ,
                 out_exp              , electronic_tags   , out_ele     ,
                 radius_proximal      , radius_distal     , out_vbu         ) 


  # running MLR on the input matrix 

    run = MLRBinary + " " + TempFile + " > " + OutputFile
    os.system(run)

 # parse temp.out to get reference fitted values 

    reference_fit = []

    with open(OutputFile, "r") as f:
         lines = f.readlines()
         for line in lines:
             if (line[-4:-1] == "Fit"):
                reference_fit.append(float(line.split()[6]))


  # End of reference MLR run - start the prediction run by 
  # writing matrix with out_skipped defining the predicted systems

    write_matrix(TempFile             , title             , print_flag           ,
                 normalization_flag   , shift_flag        , out_skipped          ,
                 no_of_systems        , no_of_electronics , no_of_sterics        ,
                 no_of_buried_volumes , out_tag           , experimental_tag     ,
                 out_exp              , electronic_tags   , out_ele     ,
                 radius_proximal      , radius_distal     , out_vbu         ) 


  # running MLR on the prediction matrix 

    run = MLRBinary + " " + TempFile + " > " + OutputFile
    os.system(run)


  # from temp.out get reference fitted values and coefficients

    reference_pre = []

    with open(OutputFile, "r") as f:
         lines = f.readlines()
         for line in lines:
             if (line[-4:-1] == "Fit"):
                reference_pre.append(float(line.split()[6]))
             if (line[-4:-1] == "Pre"):
                reference_pre.append(float(line.split()[6]))

    os.system("rm " + TempFile )


  # prediction run done - start analysis writing files

    MAE_boot_fit = 0.0
    MAE_boot_exp = 0.0


  # analyze and print bootstrap data

    analysis_pred(PRED_File, DATFile, out_tag, out_skipped,
                  out_exp, reference_fit, reference_pre) 


#   print('all done')


# --- End of main run_yrand.py -------------------------------

        
#==============================================================================
if __name__ == '__main__':
     main()
