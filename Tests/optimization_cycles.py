#!/usr/bin/env python3 -B

""" ---------------------------------------------------------------------------

This script simulates optimization cycles by running a series of MLR tests 
on randomly generated bags having one poor and one top performing system
    1) using Nsys * percentage the system is divided into prediction and training parts
    2) randomly choose 3 systems from preds and trains part. respectively, and put them into 3 bags
    3) training the model from the trains part - selected 3 systems
    4) one-by-one predict the data in bag 1, 2, 3:
         if data in bags are TP or FP, put them into training set, retrain the model,
         and predict the data in the next bag

To be run as:
   python run_bootstrap.py -m/--matrix  sys08.matrix  -o/--percentage_cycles 0.2 
                           -d/--direction up/dw -c/--cutoff 0.8 -n/--no_of_cycles


Input:
   MatrixFile        : = file     myfile.matrix    Matrix with the dataset to be learned.
   percentage_cycles : = float    Percentage of systems put into prediction list
   up or down        : = str      up/dw keyword to set if top/bottom split for training
   cutoff            : = float    How much scaling the top system in the training dataset
   no_of_cycles      : = float    How many random bags to be simulated at each optimization cycle
   

Output:
   PRED_File : = myfile.cycles_dat    File with history of each bag simulated, TP, FP, TN, FN etc.
   OUTFile   : = myfile.cycles_stat   Summary file per cycle, and summary of whole process

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

    PRED_File : = myfile.cycles_dat    File with history of each bag simulated, TP, FP, TN, FN etc.
    OUTFile   : = myfile.cycles_stat   Summary file per cycle, and summary of whole process

    ------------------------------------------------------------------- """

  # get the input and output file names

    parser = argparse.ArgumentParser()
    
    parser.add_argument("-m", "--matrix",  help = "Missing Matrix file") 
    parser.add_argument("-o", "--percentage", help = "Missing Percentage")
    parser.add_argument("-d", "--direction", help = "Missing if up or down reordering")
    parser.add_argument("-n", "--no_of_cycles", help = "Missing No of optimization cycles")   
    parser.add_argument("-c", "--cutoff", help = "Missing cutoff on top value in training dataset")

    args            = parser.parse_args()

    if (not args.matrix)     \
    or (not args.percentage) \
    or (not args.direction)  \
    or (not args.no_of_cycles)  \
    or (not args.cutoff)  :
       print(' Usage:  run_reorder.py -m/--matrix file.matrix    \
                                      -o/--precentage fraction of systems to predict  \
                                      -d/--direction up or down \
                                      -n/--no_of_cycles  No of 3 bags optimization cycles \
                                      -c/--cutoff cutoff to define TP/TN')
       exit()

    MatrixFile   = args.matrix
    percentage   = float(args.percentage)
    updown_flag  = str(args.direction)
    cutoff       = float(args.cutoff)
    no_of_cycles = int(args.no_of_cycles)

    if (updown_flag != 'up') and (updown_flag != 'down'):
       print(' Error:  -d/--direction flag must be up/down')
       exit()

    
    TempFile  = MatrixFile.replace("matrix", "tmp")
    PRED_File = MatrixFile.replace("matrix", "cycles_dat")
    OUTFile  = MatrixFile.replace("matrix",  "cycles_stat")
    
    return (MatrixFile, TempFile, PRED_File, OUTFile, percentage, updown_flag, no_of_cycles, cutoff)
# ---------------------


def calc_Acc_Pre_Rec(tp, fp, tn, fn):
    
  # Accuracy
    Acc = (tp+tn)/(tp+fp+tn+fn)
    Pre = (tp)/(tp+fp)
    Rec = (tp)/(tp+fn)
    
    return(Acc, Pre, Rec)
# ------------------------------------
    

def calc_Acc_Pre_Rec_3bags(tp, fp, tn, fn):
 
    Acc_3_bags = np.zeros(4, dtype=float)
    Pre_3_bags = np.zeros(4, dtype=float)
    Rec_3_bags = np.zeros(4, dtype=float)
    
    for b in range (4):
        Acc_3_bags[b], Pre_3_bags[b], Rec_3_bags[b] = calc_Acc_Pre_Rec(tp[b], fp[b], tn[b], fn[b])

    return (Acc_3_bags, Pre_3_bags, Rec_3_bags)
# ---------------------------------------------


def define_no_preds_bags(no_of_systems, percentage):
   
  # initialize arrays and set skipped_systems array to indicate systems to be predicted
  # if more than 12 systems and only 3 top systems selected, add one to give flexibility

    if no_of_systems < 10:
       print(' Number of systems too small.')
       exit()

    if no_of_systems == 10:
       no_of_preds = 2 
       no_of_bags  = 2

    if no_of_systems == 11:
       no_of_preds = 3 
       no_of_bags  = 2

    if no_of_systems == 12:
       no_of_preds = 3 
       no_of_bags  = 3

    if no_of_systems > 12:
       no_of_preds   = int(round(no_of_systems * percentage))
       if no_of_preds == 3:
          no_of_preds = 4 
       no_of_bags  = 3

    no_of_trains   = no_of_systems - no_of_preds

    return (no_of_preds, no_of_trains, no_of_bags)
# ----------------------------------


def set_lists_trains_preds(no_of_systems, no_of_preds, no_of_trains, updown_flag):
  
  # define which systems to be in the training and which in the prediction subsets
  
    list_of_preds = np.zeros(no_of_preds, dtype=int)
    list_of_trains = np.zeros(no_of_trains, dtype=int)
   
    if(updown_flag == "up"):
        for i in range(1, no_of_trains+1):
            list_of_trains[i-1] = i  

        for i in range(no_of_trains+1, no_of_systems+1):
            list_of_preds[i-no_of_trains-1] = i

    if(updown_flag == "down"):
       for i in range(1,no_of_trains+1):
           list_of_trains[i-1] = i + no_of_preds
      
       for i in range(1, no_of_preds+1):
           list_of_preds[i-1] = i

    return (list_of_trains, list_of_preds)
# ---------------------------------------



def one_loop_3bags():

  # get input and output files

    MatrixFile, TempFile, PRED_File, OUTFile, percentage, updown_flag, no_of_cycles, cutoff = GetFiles()
    MLRBinary, PYTHONHOME = GetVariables()


  # call read_matrix to read matrix_file

    title             , print_flag             , normalization_flag   , \
    shift_flag        , skipped_systems        , no_of_systems        , \
    no_of_electronics , no_of_sterics          , no_of_buried_volumes , \
    system_tags       , experimental_tag       , experimental_data    , \
    electronic_tags   , electronic_descriptors , radius_proximal      , \
    radius_distal     , buried_volumes         = read_matrix(MatrixFile) 


  # reorder matrix and put the reordered content to the out_* lists

    out_tag = np.array(no_of_systems, dtype=str)
    out_exp = np.zeros(no_of_systems, dtype=float)
    out_ele = np.zeros((no_of_electronics, no_of_systems), dtype=float)
    out_vbu = np.zeros((no_of_buried_volumes, 2*no_of_systems), dtype=float)

    out_tag, out_exp, out_ele, out_vbu = reorder_matrix(
    title             , print_flag             , normalization_flag   ,  
    shift_flag        , skipped_systems        , no_of_systems        ,  
    no_of_electronics , no_of_sterics          , no_of_buried_volumes ,  
    system_tags       , experimental_tag       , experimental_data    ,  
    electronic_tags   , electronic_descriptors , radius_proximal      ,  
    radius_distal     , buried_volumes         , 'up'          )


  # define how many preds, trainings and bags, and define which systems 

    no_of_preds, no_of_trains, no_of_bags = define_no_preds_bags(no_of_systems, percentage)
    list_of_trains, list_of_preds = set_lists_trains_preds(no_of_systems, no_of_preds, no_of_trains, updown_flag)
  

    np.random.seed(223)
    os.system("rm " + PRED_File)
    os.system("rm " + OUTFile)
 
    no_of_TP = np.zeros(4, dtype=int)
    no_of_FP = np.zeros(4, dtype=int)
    no_of_TN = np.zeros(4, dtype=int)
    no_of_FN = np.zeros(4, dtype=int)
    
    
  # start optimization cycles - generate 3 bags
   
    for c in range(no_of_cycles):
        print(' cycle ', c)
        list_outside = np.random.choice(list_of_preds, no_of_bags, replace=False)
        list_inside  = np.random.choice(list_of_trains, no_of_bags, replace=False)
        
        if(updown_flag == "up"):
            list_outside = np.sort(list_outside)
            
        if(updown_flag == "down"):
            list_outside = np.sort(list_outside)
            list_outside = list_outside[::-1]
 

      # set tags of systems to be skipped - add 3 bags to out_skipped  
      
        out_skipped = []
        out_skipped.append(no_of_preds+no_of_bags)
        
        for i in range(no_of_bags):
            out_skipped.append(list_inside[i])
            out_skipped.append(list_outside[i])
            
            
      # add remaining top systems to out_skipped 
      
        for i in range(len(list_of_preds)):
            key_skip = 0
            if list_of_preds[i] in out_skipped: 
                key_skip = 1
            if(key_skip == 0): 
                out_skipped.append(list_of_preds[i])
 
    
      # generate list_training exp_training    
      
        list_training = []
        exp_training  = []
        
        for i in range(no_of_systems):
            key_skip= 0
            if i+1 in out_skipped[1:]:
                key_skip = 1
            if(key_skip == 0):
                list_training.append(i+1)
#                exp_training.append(experimental_data[i])
                exp_training.append(out_exp[i])

    
      # scan the bags
      
        for bag in range(no_of_bags):
            
      # generate temporary file
      
            write_matrix(TempFile             , title             , print_flag           ,
                         normalization_flag   , shift_flag        , out_skipped          ,
                         no_of_systems        , no_of_electronics , no_of_sterics        ,
                         no_of_buried_volumes , out_tag           , experimental_tag     ,
                         out_exp              , electronic_tags   , out_ele              ,
                         radius_proximal      , radius_distal     , out_vbu         )
        
            
      # run the fortran code
      
            run =  MLRBinary  + " " + TempFile + " > temp.out"
            os.system(run)

            os.system("cp " + TempFile + "  " + TempFile + "." + str(bag))
    
            
      # do the analysis
      
            if(updown_flag == "up"):
                threshold = np.max(exp_training) * cutoff
    
            if(updown_flag == "down"):
                threshold = np.min(exp_training) * cutoff
      
            sys = []
            exp = []
            pre = []
            TOF = []
            
            with open('temp.out', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if (line[0:3] == "LOO"):
                      sys.append(int(line.split()[1]))
                      exp.append(float(line.split()[2]))
                      pre.append(float(line.split()[3]))
                      max_exp = np.max(exp_training)
                      min_exp = np.min(exp_training)
                      
                      if sys[-1] == list_outside[bag] or sys[-1] == list_inside[bag]:

                          if updown_flag == "up":
                              
                            if pre[-1] >= threshold:
                                if exp[-1] >= max_exp:
                                   TOF.append("TP")
                                   no_of_TP[bag] = no_of_TP[bag] + 1
                                else:
                                   TOF.append("FP")
                                   no_of_FP[bag] = no_of_FP[bag] + 1
    
                            if pre[-1] < threshold:
                                if exp[-1] > max_exp:
                                   TOF.append("FN")
                                   no_of_FN[bag] = no_of_FN[bag] + 1
                                else:
                                   TOF.append("TN")
                                   no_of_TN[bag] = no_of_TN[bag] + 1
                                
                                
                          if updown_flag == "down":
                              
                            if pre[-1] > threshold and exp[-1] > min_exp:
                                TOF.append("TN")
                                no_of_TN[bag] = no_of_TN[bag] + 1
    
                            if pre[-1] > threshold and exp[-1] < min_exp:
                                TOF.append("FN")
                                no_of_FN[bag] = no_of_FN[bag] + 1
    
                            if pre[-1] < threshold and exp[-1] > min_exp:
                                TOF.append("FP")
                                no_of_FP[bag] = no_of_FP[bag] + 1
    
                            if pre[-1] < threshold and exp[-1] < min_exp:
                                TOF.append("TP")
                                no_of_TP[bag] = no_of_TP[bag] + 1
                                                  
                
            with open(PRED_File, "a") as f:
                 f.write("{:5d} ".format(c)
                        +"{:3d}".format(bag+1)
                        +"{:8.3f}".format(threshold/cutoff)
                        +"{:8.3f}".format(threshold)
                        +"{:4d}".format(sys[0])
                        +"{:8.3f}".format(exp[0])
                        +"{:8.3f}".format(pre[0])
                        +"{:>3s}".format(TOF[0])
                        +"{:4d}".format(sys[1])
                        +"{:8.3f}".format(exp[1])
                        +"{:8.3f}".format(pre[1])
                        +"{:>3s}".format(TOF[1]))
              
                 for ii in range(len(list_training)):
                     f.write("{:6d}".format(list_training[ii]))
                 f.write("\n")
      
                
          # bag completed - add TP and FP systems to the matrix
      
            num_move  = 0
            temp_pred = []
            temp_pred.append(out_skipped[1])
            temp_pred.append(out_skipped[2])
            
    
            if TOF[1] == "TP" or TOF[1] == "FP":
                list_training.append(out_skipped[2])
                temp_pred.pop(1)
                num_move += 1
                exp_training.append(out_exp[out_skipped[2]-1])


            if TOF[0] == "TP" or TOF[0] == "FP":
                list_training.append(out_skipped[1])
                temp_pred.pop(0)
                num_move += 1
                exp_training.append(out_exp[out_skipped[1]-1])

            
            out_skipped[0] -= num_move
            out_skipped.pop(1)
            out_skipped.pop(1)
            
            for ii in range(len(temp_pred)):
                out_skipped.append(temp_pred[ii])
                
            if updown_flag == "up":
                threshold = np.max(exp_training) * cutoff
                
            if updown_flag == "down":
                threshold = np.min(exp_training) * cutoff
    
    no_of_TP[3] = np.sum(no_of_TP)
    no_of_FP[3] = np.sum(no_of_FP)
    no_of_TN[3] = np.sum(no_of_TN)
    no_of_FN[3] = np.sum(no_of_FN)
    
    Acc_3_bags = np.zeros(4, dtype=float)
    Pre_3_bags = np.zeros(4, dtype=float)
    Rec_3_bags = np.zeros(4, dtype=float)
 
    Acc_3_bags, Pre_3_bags, Rec_3_bags = calc_Acc_Pre_Rec_3bags(no_of_TP, no_of_FP, no_of_TN, no_of_FN)
    
    with open(OUTFile, "a") as f:
        for c in range(4):
            f.write("{:5d} ".format(no_of_TP[c])
                   +"{:5d} ".format(no_of_FP[c])
                   +"{:5d} ".format(no_of_TN[c])
                   +"{:5d} ".format(no_of_FN[c]) 
                   +"{:6.3f} ".format(Acc_3_bags[c]) 
                   +"{:6.3f} ".format(Pre_3_bags[c]) 
                   +"{:6.3f} ".format(Rec_3_bags[c]) + '\n')
   
  
    os.system('rm temp.out')
    os.system('rm ' + TempFile)
    print('all done')


#==============================================================================
if __name__ == '__main__':
     one_loop_3bags()
