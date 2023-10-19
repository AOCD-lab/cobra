#!/usr/bin/env python3 -B

""" ---------------------------------------------------------------------------

This script reorders a matrix file by increasing or decreasing experimental data

To be run as:
   python run_matrix_reorder.py -m/--matrix  sys08.matrix  -o/output reordered.matrix 
                                -d/direction up/down

Input:
   MatrixFile : = myfile.matrix    Matrix with the dataset to be learned.
   direction  : = string           Runtime parameter telling if experimental data 
                                   to be reordered by increasing or decreasing values
   
Output:
   Out_Matrix_File  : = reordered.matrix    File with reordered matrix

@author: Zhen Cao, Luigi Cavallo
--------------------------------------------------------------------------- """

import argparse
import numpy as np
from matrix_operation import *

# ---------------------

def GetFiles():

    """ -------------------------------------------------------------------
    Handles input/output and excutable files

    Input:

    MatrixFile : = myfile.matrix    Matrix with the dataset to be learned.
    direction  : = string           Runtime parameter telling if experimental data 
                                    to be reordered by increasing or decreasing values
    Output:
    Out_Matrix_File  : = reordered.matrix    File with reordered matrix

    ------------------------------------------------------------------- """

  # set the input and output file names

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--matrix",  help = "Missing Matrix file") 
    parser.add_argument("-d", "--direction", help = "Missing if up or down reordering")
    parser.add_argument("-o", "--output", help = "Missing output matrix file name")

    args            = parser.parse_args()

    if (not args.matrix)     \
    or (not args.output)     \
    or (not args.direction)  :
       print(' Usage:  run_reorder.py -m/--matrix file.matrix    \
                                      -o/--output output.matrix  \
                                      -d/--direction up or down' )
       exit()


    MatrixFile      = args.matrix
    Out_Matrix_File = args.output
    updown_flag     = str(args.direction)

    if (updown_flag != 'up') and (updown_flag != 'down'):
       print(' Error:  -d/--direction flag must be up/down')
       exit()


    return (MatrixFile, updown_flag, Out_Matrix_File)

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
            if no_of_sterics == 1:
               r1 = r
               r2 = out_indices[r]
               out_vbu[s][r1] = buried_volumes[s][r2]
            if no_of_sterics == 2:
               r1 = r*2
               r2 = out_indices[r]*2
               out_vbu[s][r1] = buried_volumes[s][r2]
               out_vbu[s][r1+1] = buried_volumes[s][r2+1]


  # all done, return the reordered data

    return(out_tag, out_exp, out_ele, out_vbu)

# ---------------------

def main():
    
  # parsing runtime arguments

    (MatrixFile, updown_flag, Out_Matrix_File) = GetFiles()


  # read matrix_file

    title             , print_flag             , normalization_flag   , \
    shift_flag        , skipped_systems        , no_of_systems        , \
    no_of_electronics , no_of_sterics          , no_of_buried_volumes , \
    system_tags       , experimental_tag       , experimental_data    , \
    electronic_tags   , electronic_descriptors , radius_proximal      , \
    radius_distal     , buried_volumes         = read_matrix(MatrixFile) 


  # initialize arrays

    out_tag = np.array(no_of_systems, dtype=str)
    out_exp = np.zeros(no_of_systems, dtype=float)
    out_ele = np.zeros((no_of_electronics, no_of_systems), dtype=float)
    out_vbu = np.zeros((no_of_buried_volumes, 2*no_of_systems), dtype=float)


  # reorder matrix

    out_tag, out_exp, out_ele, out_vbu = reorder_matrix(
    title             , print_flag             , normalization_flag   ,  
    shift_flag        , skipped_systems        , no_of_systems        ,  
    no_of_electronics , no_of_sterics          , no_of_buried_volumes ,  
    system_tags       , experimental_tag       , experimental_data    ,  
    electronic_tags   , electronic_descriptors , radius_proximal      ,  
    radius_distal     , buried_volumes         , updown_flag          )


  # write reordered matrix 

    write_matrix(Out_Matrix_File      , title             , print_flag           ,
                 normalization_flag   , shift_flag        , skipped_systems      ,
                 no_of_systems        , no_of_electronics , no_of_sterics        ,
                 no_of_buried_volumes , out_tag           , experimental_tag     ,
                 out_exp              , electronic_tags   , out_ele     ,
                 radius_proximal      , radius_distal     , out_vbu         ) 

    return()

# --- End of main run_matrix_reorder.py -------------------------------

        
#==============================================================================
if __name__ == '__main__':
     main()
