#!/usr/bin/env python3 -B

""" ---------------------------------------------------------------------------

This script runs bootstrap test by running a series of MLR tests 
on the files generated by:
    1) the number of the systems put into the bag no_of_prediction = Nsys * percentage
    2) randomly choose NumChoose systems (Do not contain replica of the systems)
    3) generate a list contain Nsys - no_of_prediction systems, do np.random.choice(list, Nsys)

generate a new matrix, the first Nsys colomns contains randomly picked 

To be run as:
   python run_bootstrap.py -m/--matrix  sys08.matrix  -n/ncycles 10 -p/percentage 0.1

Input:
   MatrixFile : = myfile.matrix    Matrix with the dataset to be learned.
   ncycles    : = integer          Runtime parameter with number of 
                                   bootstrap cycles.
   percentage : = float            percentage of systems put into prediction list
   
Output:
   BOOT_File = myfile.boot_dat     File with ID of systems in boot dataset and those held out
   CFF_File  = myfile.boot_coef    File with coef full dataset coef boot and deviation
   R2_File   = myfile.boot_r2      R2 full dataset, bootstrap dataset, deviation
   MAE_File  = myfile.boot_mae     File with MAE from experiments, and full dataset fitted,   
                                   coefficients and R2
   PRED_File = myfile.boot_pred    File with experimental, fitted full dataset, prediction,
                                   deviation from experimental, deviation from fitted


@author: Zhen Cao, Luigi Cavallo
--------------------------------------------------------------------------- """

import argparse
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Utilities.set_variables import *
from Utilities.matrix_operation import *


# ---------------------

def GetFiles():

    """ -------------------------------------------------------------------
    Handles input/output and excutable files

    BOOT_File  : = myfile.boot            File with list of bootstrap data
    CFF_File   : = myfile.MAE_boot_cff    File with analysis of coeffcients from bootstrap.
    R2_File    : = myfile.MAE_boot_r2     File with analysis of R2 from bootstrap.
    PRED_File  : = myfile.MAE_boot_pred   File with analysis of predictions from bootstrap.

    ------------------------------------------------------------------- """

  # get the input and output file names

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--matrix",  help = "Missing Matrix file") 
    parser.add_argument("-n", "--ncycles", help = "Missing Number of Bootstrap cycles")
    parser.add_argument("-b", "--boot_percentage", help = "Missing Percentage")

    args            = parser.parse_args()

    if (not args.matrix)          \
    or (not args.ncycles)         \
    or (not args.boot_percentage) :
       print(' Usage:  run_bootstrap.py -m/--matrix file.matrix       \
                                        -n/--ncycles integer          \
                                        -b/--boot_percentage float'   )
       exit()




    MatrixFile      = args.matrix
    no_of_bootstrap = int(args.ncycles)
    percentage      = float(args.boot_percentage)
    
    TempFile  = MatrixFile.replace("matrix", "tmp")
    BOOT_File = MatrixFile.replace("matrix", "boot_dat")
    PRED_File = MatrixFile.replace("matrix", "boot_pred")
    CFF_File  = MatrixFile.replace("matrix", "boot_coef")
    R2_File   = MatrixFile.replace("matrix", "boot_r2")
    MAE_File  = MatrixFile.replace("matrix", "boot_mae")

    return (MatrixFile, TempFile, BOOT_File, PRED_File, CFF_File, R2_File, MAE_File,
            no_of_bootstrap, percentage)


# ---------------------

def analysis_boot_cff(CFF_File, no_of_bootstrap, no_of_coef, reference_cff, boot_cff):

  # analyzes coefficients from bootstrap run and writes out MAE_boot_cff
  # MAE is calculated from reference_cff, which contains coefficients from
  # fitting the original dataset.

  # Input:
    # CFF_File         := file where to write results of the analysis.
    # no_of_bootstrap  := No of bootstrap cycles.
    # no_of_coef       := No of coefficients in the MLR training.
    # reference_cff    := Coefficients in the MLR training - array size no_of_coef.
    # boot_cff         := Coefficients from MLR training during the bootstrap cycles
    #                     - array size no_of_bootstrap*no_of_coef.

  # Output:            := results are written in file CFF_File
  # ---------------------


    MAE_boot_cff   = 0.0
    difference_cff = []

    with open(CFF_File, "w") as f:
         for b in range(no_of_bootstrap):
             for c in range(no_of_coef):

                 difference_cff.append(np.abs(boot_cff[b][c] - reference_cff[c]))
                 f.write("{:8.3f}".format(reference_cff[c]) + '  '
                       + "{:8.3f}".format(boot_cff[b][c])   + '  '
                       + "{:8.3f}".format(boot_cff[b][c] - reference_cff[c]) +  '\n')

         difference_cff = np.array(difference_cff)
         MAE_boot_cff = np.mean(difference_cff)
         MAE_boot_cff_std = np.std(difference_cff, ddof=1)
  

    return(MAE_boot_cff, MAE_boot_cff_std)


# ---------------------

def analysis_boot_r2(R2_File, no_of_bootstrap, reference_R2, boot_r2):

  # analyzes R2 from bootstrap run and writes out MAE_boot_r2
  # MAE is calculated from reference_r2, which contains R2 from
  # fitting the original dataset.

  # Input:
    # R2_File         := file where to write results of the analysis.
    # no_of_bootstrap := No of bootstrap cycles.
    # reference_r2    := R2 in the MLR training - float
    # boot_r2         := R2 from MLR training during the bootstrap cycles
    #                     - array size no_of_bootstrap*no_of_coef.

  # Output:           := results are written in file R2_File
  # ---------------------


  # analyzes R2 from bootstrap run

    MAE_boot_r2   = 0.0
    difference_r2 = []


    with open(R2_File, "w") as f:
         for b in range(no_of_bootstrap):

             difference_r2.append(np.abs(boot_r2[b] - reference_R2))

             f.write("{:8.3f}".format(reference_R2) + '  '
                    + "{:8.3f}".format(boot_r2[b])  + '  '
                    + "{:8.3f}".format(boot_r2[b] - reference_R2) + '\n')

         difference_r2 = np.array(difference_r2)
         MAE_boot_r2   = np.mean(difference_r2)
         MAE_boot_r2_std = np.std(difference_r2, ddof=1)
 
    return(MAE_boot_r2, MAE_boot_r2_std)


# ---------------------

def analysis_boot_pred(PRED_File, no_of_bootstrap, no_of_prediction, system_tags, 
                      experimental_data, reference_fit, boot_tag, boot_pred):

  # analyzes predicted experimental values from bootstrap run and writes out MAE_boot_exp
  # MAE_boot_fit.  MAEs are calculated from experimental_data and reference_fit, which 
  # contains experimental values and values from fitting the whole dataset.

  # Input:
    # PRE_File          := file where to write results of the analysis.
    # no_of_bootstrap   := No of bootstrap cycles.
    # no_of_prediction  := No of systems predicted in the bootstrap cycles
    # experimental_data := Fitted values from MLR training on the whoe dataset.
    # reference_fit     := Fitted values from MLR training on the whoe dataset.
    # boot_pred         := Predictions from MLR training during the bootstrap cycles
    #                     - array size no_of_bootstrap*no_of_prediction.

  # Output:            := results are written in file PRED_File
  # ---------------------


    MAE_boot_exp= 0.0
    MAE_boot_fit= 0.0
    difference_exp = []
    difference_fit = []


    with open(PRED_File, "w") as f:
         for b in range(no_of_bootstrap):
             for c in range(no_of_prediction):
 
               # find which system is predicted
                 id_predicted_system = system_tags.index(boot_tag[b*no_of_prediction+c])

                 difference_exp.append(np.abs(boot_pred[b*no_of_prediction+c] 
                                            - experimental_data[id_predicted_system]))
                 difference_fit.append(np.abs(boot_pred[b*no_of_prediction+c] 
                                            - reference_fit[id_predicted_system]))

                 f.write("{:8s}  ".format(system_tags[id_predicted_system]) 
                        +"{:8s}  ".format(boot_tag[b*no_of_prediction+c])  
                        +"{:8.3f}".format(experimental_data[id_predicted_system])  
                        +"{:8.3f}".format(reference_fit[id_predicted_system])  
                        +"{:8.3f}".format(boot_pred[b*no_of_prediction+c])  
                        +"{:8.3f}".format(boot_pred[b*no_of_prediction+c] 
                                        - experimental_data[id_predicted_system])
                        +"{:8.3f}".format(boot_pred[b*no_of_prediction+c] 
                                        - reference_fit[id_predicted_system]) + '\n')

         difference_exp = np.array(difference_exp)
         MAE_boot_exp   = np.mean(difference_exp)
         MAE_boot_exp_std = np.std(difference_exp, ddof=1)

         difference_fit = np.array(difference_fit)
         MAE_boot_fit   = np.mean(difference_fit)
         MAE_boot_fit_std = np.std(difference_fit, ddof=1)

 
    return(MAE_boot_exp, MAE_boot_exp_std, MAE_boot_fit, MAE_boot_fit_std)


# ---------------------
def prepare_bootstrap_indices(BOOT_File, no_of_bootstrap, no_of_systems, no_of_prediction, 
                              bootstrap_indices):

  # prepare bootstrap_indices defining which systems are in the training bag and which in the 
  # prediction bag.
  
  # Input:   
    #    BOOT_File        := File name where storing indices of training and prediction bags.
    #    no_of_bootstrap  := Number of bootstrap cycles to be considered.
    #    no_of_system     := Number of systems in the original dataset.
    #    no_of_prediction := Number of systems to be included in the prediction bag.
  
  # Output:   
    #    bootstrap_indices := matrix [no_of_bootstrap][no_of_systems+no_of_prediction]
    #                         each row of this matrix has training bag first followed
    #                         by prediciton bag. Maximum two replica per system allowed
    #                         in the training bag.
  # ---------------------


  # looping over the numer of bootstrap cycles 
  # start filling prediction bag, then training bag

    ntotal  = no_of_systems + no_of_prediction
    indices = np.arange(no_of_systems, dtype=int)

    np.random.seed(42)
    for b in range(no_of_bootstrap):
        prediction_bag = np.random.choice(indices, no_of_prediction, replace=False)

      # build a training pool from which extract the training set, including 
      # two times each system not in the prediction bag.

        training_pool = []
        for i in range(no_of_systems):
            if not (i in prediction_bag):
               training_pool.append(i)
               training_pool.append(i)

      # picking randomly no_of_systems from the doubled training pool, no replica, 
      # will allow each system to be present maximum two times in the training bag.

        training_pool = np.array(training_pool, dtype=int)
        training_bag  = np.random.choice(training_pool, no_of_systems, replace=False)
        
      # transferring training and prediciton bags to bootstrap_indices

        bootstrap_indices[b][:no_of_systems]       = training_bag[:]
        bootstrap_indices[b][no_of_systems:ntotal] = prediction_bag[:]

      
  # printing the BootFile to store indices of systems in training and prediction bags

    with open(BOOT_File, "w") as boot:
         boot.write( "{:48s}".format(" Cycle   ID of systems in bootstrap matrix: last   ") 
                   + "{:3d}".format(no_of_prediction) 
                   + "{:28s}".format("  are those to be predicted" 
                   + "\n"))

         for b in range(no_of_bootstrap):
             boot.write("{:4d}".format(b) + "   ")

             for i in range(ntotal):
                 boot.write( "{:4d}".format(bootstrap_indices[b][i]))
             boot.write('\n')


    return (bootstrap_indices)
# ---------------------
def assemble_bootstrap_matrix(b                   , ntotal                , no_of_electronics, 
                              no_of_sterics       , no_of_buried_volumes  , bootstrap_indices, 
                              system_tags         , experimental_data     , electronic_descriptors, 
                              buried_volumes      , boot_system_tag       , boot_experimental, 
                              boot_electronics    , boot_volumes):
  # assemble bootstrap matrix

    for n in range(ntotal):
        boot_system_tag[n]   = system_tags[bootstrap_indices[b][n]]
        boot_experimental[n] = experimental_data[bootstrap_indices[b][n]]
    
    for e in range(no_of_electronics):
        for n in range(ntotal):
            boot_electronics[e][n] = electronic_descriptors[e][bootstrap_indices[b][n]]

    for v in range(no_of_buried_volumes):
        for n in range(ntotal):
            n1 = no_of_sterics*n
            b1 = no_of_sterics*bootstrap_indices[b][n]
            boot_volumes[v][n1]   = buried_volumes[v][b1]
          
            if no_of_sterics == 2:
               boot_volumes[v][n1+1] = buried_volumes[v][b1+1]


    return()
# ---------------------

def main():
    
  # get input and output files

    (MatrixFile, TempFile, BOOT_File, PRED_File, CFF_File, R2_File, MAE_File,
                no_of_bootstrap, percentage) = GetFiles()
    MLRBinary, PYTHONHOME = GetVariables()


  # call read_matrix to read matrix_file

    title             , print_flag             , normalization_flag   , \
    shift_flag        , skipped_systems        , no_of_systems        , \
    no_of_electronics , no_of_sterics          , no_of_buried_volumes , \
    system_tags       , experimental_tag       , experimental_data    , \
    electronic_tags   , electronic_descriptors , radius_proximal      , \
    radius_distal     , buried_volumes         = read_matrix(MatrixFile) 


  # initialize arrays

    no_of_prediction     = round(no_of_systems * percentage)
    ntotal               = no_of_prediction + no_of_systems
    
#   indices              = np.arange(no_of_systems, dtype=int)
    bootstrap_indices    = np.zeros ((no_of_bootstrap, ntotal), dtype=int)

    boot_system_tag      = [' ']*ntotal
    boot_experimental    = np.zeros (ntotal)
    boot_electronics     = np.zeros ((no_of_electronics, ntotal))
    boot_volumes         = np.zeros ((no_of_buried_volumes, 2*ntotal))
    boot_skipped_systems = np.zeros(no_of_prediction+1, dtype=int)


  # running MLR on the input matrix to get reference values and coefficients

    run = MLRBinary  + " " + MatrixFile + " > tempo-fit.out"
    os.system(run)

  # from temp.out get reference fitted values and coefficients

    reference_fit = []
    reference_cff = []

    with open('tempo-fit.out', "r") as f:
         lines = f.readlines()
         for line in lines:
             if (line[-4:-1] == "Fit"):
                reference_fit.append(float(line.split()[6]))

             if (line[0:6] == "Max R2"):
                words = line.split()[:-1]
                no_of_coef = len(words) - 4
                reference_cff = np.array(line.split()[5:]).astype(np.float)
                reference_R2 = float(words[2])


  # End of reference MLR run - start the bootstrap procedure
  # set skipped_systems indices by incrementing the total no of systems in the dataset

    boot_skipped_systems[0] = no_of_prediction
    for i in range(no_of_prediction):
        boot_skipped_systems[i+1] = no_of_systems + i + 1
    

  # fill training and prediction bags, store them into bootstrap_indices

    np.random.seed(42)
    prepare_bootstrap_indices(BOOT_File, no_of_bootstrap, no_of_systems, no_of_prediction, 
                              bootstrap_indices ) 


  # run MLR on all the training and prediciton bags.
  # start initializing arrays to store results.

    boot_cff = np.zeros((no_of_bootstrap,no_of_coef))
    boot_r2  = np.zeros(no_of_bootstrap)
    boot_tag = []
    boot_pre = []

    for b in range (no_of_bootstrap):

      # assemble bootstrap matrix
        assemble_bootstrap_matrix(b                   , ntotal                , no_of_electronics, 
                                  no_of_sterics       , no_of_buried_volumes  , bootstrap_indices, 
                                  system_tags         , experimental_data     , electronic_descriptors, 
                                  buried_volumes      , boot_system_tag       , boot_experimental, 
                                  boot_electronics    , boot_volumes)


      # call write_matrix to write matrix_file for loo calculation

        write_matrix(TempFile             , title             , print_flag           ,
                     normalization_flag   , shift_flag        , boot_skipped_systems ,
                     ntotal               , no_of_electronics , no_of_sterics        ,
                     no_of_buried_volumes , boot_system_tag   , experimental_tag     ,
                     boot_experimental    , electronic_tags   , boot_electronics     ,
                     radius_proximal      , radius_distal     , boot_volumes         ) 

        run = MLRBinary + " " + TempFile + " > temp.out"
        os.system(run)

      # from temp.out get predicted value for this bootstrap 

        with open('temp.out', "r") as f:
             lines = f.readlines()
             for line in lines:
                 if (line[-4:-1] == "Pre"):
                    boot_tag.append(line.split()[1])
                    boot_pre.append(line.split()[6])

                 if (line[0:6] == "Max R2"):
                    boot_r2[b]     = line.split()[2]
                    boot_cff[b][:] = line.split()[5:]
 

        #os.system('rm temp.out')

  # bootstrap cycles done - start analysis writing files

    boot_r2  = np.array(boot_r2).astype(np.float)
    boot_pre = np.array(boot_pre).astype(np.float)
    boot_cff = np.array(boot_cff).astype(np.float)


    MAE_boot_fit = 0.0
    MAE_boot_exp = 0.0


  # analyze and print bootstrap data

    (MAE_boot_exp, MAE_boot_exp_std, MAE_boot_fit, MAE_boot_fit_std) = analysis_boot_pred(PRED_File, no_of_bootstrap, no_of_prediction, system_tags, 
                       experimental_data, reference_fit, boot_tag, boot_pre) 

    (MAE_boot_r2, MAE_boot_r2_std) = analysis_boot_r2(R2_File, no_of_bootstrap, reference_R2, boot_r2)

    (MAE_boot_cff, MAE_boot_cff_std) = analysis_boot_cff(CFF_File, no_of_bootstrap, no_of_coef, reference_cff, boot_cff) 


    with open(MAE_File, "w") as f:
        f.write('MAE_boot_exp  ' + "{:8.3f}".format(MAE_boot_exp) 
               +'   StDev   '    + "{:8.3f}".format(MAE_boot_exp_std) + '\n')
        f.write('MAE_boot_fit  ' + "{:8.3f}".format(MAE_boot_fit) 
               +'   StDev   '    + "{:8.3f}".format(MAE_boot_fit_std) + '\n')
        
        f.write('MAE_boot_cff  ' + "{:8.3f}".format(MAE_boot_cff) 
                +'   StDev   '   + "{:8.3f}".format(MAE_boot_cff_std) + '\n')
        
        f.write('MAE_boot_r2   ' + "{:8.3f}".format(MAE_boot_r2) 
                +'   StDev   '   + "{:8.3f}".format(MAE_boot_r2_std) + '\n')
          

    os.system('rm temp.out')
    os.system('rm tempo-fit.out')
    os.system('rm ' + TempFile)
    
#   print('all done')


# --- End of main run_yrand.py -------------------------------

        
#==============================================================================
if __name__ == '__main__':
     main()
