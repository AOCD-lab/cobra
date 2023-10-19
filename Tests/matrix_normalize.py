#!/usr/bin/env python3 -B

""" ---------------------------------------------------------------------------

This script normalizes experimental_data and all descriptors in the matrix_file
centering by the mean and dividing by the standard deviation of input data.

To be run as:
   python run_normalize_matrix.py -m/--matrix  input.matrix  -o/output output.matrix

Input:
   MatrixFile   : = myfile.matrix       Matrix to be normalized.

Output:
   NMMatrixFile : = NM_myfile.matrix    Normalized matrix file.

@author: Zhen Cao, Luigi Cavallo
--------------------------------------------------------------------------- """

import argparse
import numpy as np
from matrix_operation import *

# ---------------------


def GetFiles():

    """ -------------------------------------------------------------------
    Handles input/output and excutable files


    ------------------------------------------------------------------- """

  # get the input and output file names

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--matrix",  help = "Missing input Matrix file") 
    parser.add_argument("-o", "--output",  help = "Missing output Matrix file") 

    args = parser.parse_args()

    if (not args.matrix) or (not args.output) :
       print(' Usage:  run_normalize_matrix.py -m/--matrix input.matrix  -o/output output.matrix')
       exit()


    MatrixFile      = args.matrix
    NormMatrixFile  = args.output


    return MatrixFile, NormMatrixFile
# --- End of GetFiles --------------------------------------

def main():
    
  # get input and output files

    MatrixFile, NormMatrixFile = GetFiles()


  # call read_matrix to read matrix_file

    title             , print_flag             , normalization_flag   , \
    shift_flag        , skipped_systems        , no_of_systems        , \
    no_of_electronics , no_of_sterics          , no_of_buried_volumes , \
    system_tags       , experimental_tag       , experimental_data    , \
    electronic_tags   , electronic_descriptors , radius_proximal      , \
    radius_distal     , buried_volumes         = read_matrix(MatrixFile) 


  # start normalizing experimental_data and electronic_descriptors

    NM_experimental_data      = np.zeros (no_of_systems)  
    NM_electronic_descriptors = np.zeros((no_of_electronics, no_of_systems))

    mean = np.mean(experimental_data)
    stdv = np.std(experimental_data, ddof=1)
    NM_experimental_data = np.divide(np.subtract(experimental_data, mean), stdv)

    for e in range(no_of_electronics):
        mean = np.mean(electronic_descriptors[e])
        stdv = np.std(electronic_descriptors[e], ddof=1)
        NM_electronic_descriptors[e] = np.divide(np.subtract(electronic_descriptors[e], mean), stdv)


  # unpack proximal and distal volumes to vp and vd, and normalize them

    if no_of_sterics == 1:
       indices = np.arange(0, no_of_systems,   1, dtype=int)

    if no_of_sterics == 2:
       even_indices = np.arange(0, 2*no_of_systems,   2, dtype=int)
       odd_indices  = np.arange(1, 2*no_of_systems+1, 2, dtype=int)

    NM_buried_volumes = np.zeros((no_of_buried_volumes, no_of_sterics*no_of_systems))

    for v in range(no_of_buried_volumes):
        NM_buried_volumes[v] = np.zeros(no_of_sterics*no_of_systems)

        if no_of_sterics == 1:
           vp = np.take(buried_volumes[v], indices)
           mean = np.mean(vp)
           stdv = np.std(vp, ddof=1)
           NM_vp = np.divide(np.subtract(vp, mean), stdv)

           np.put(NM_buried_volumes[v], indices, NM_vp)

        if no_of_sterics == 2:
           vp = np.take(buried_volumes[v], even_indices)
           mean = np.mean(vp)
           stdv = np.std(vp, ddof=1)
           NM_vp = np.divide(np.subtract(vp, mean), stdv)
           np.put(NM_buried_volumes[v], even_indices, NM_vp)
    
           vd = np.take(buried_volumes[v], odd_indices)
           mean = np.mean(vd)
           stdv = np.std(vd, ddof=1)
           NM_vd = np.divide(np.subtract(vd, mean), stdv)

           np.put(NM_buried_volumes[v], odd_indices,  NM_vd)
        

  # all done, call write_matrix to write normalized matrix_file 

    write_matrix(NormMatrixFile            , title             , print_flag                ,
                     normalization_flag    , shift_flag        , skipped_systems           ,
                     no_of_systems         , no_of_electronics , no_of_sterics             ,
                     no_of_buried_volumes  , system_tags       , experimental_tag          ,
                     NM_experimental_data  , electronic_tags   , NM_electronic_descriptors ,
                     radius_proximal       , radius_distal     , NM_buried_volumes         )


    return()
# --- End of main run_normalize_matrix.py -------------------------------

        
#==============================================================================
if __name__ == '__main__':
     main()
