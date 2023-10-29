import sys
import math
import argparse
import numpy as np
import pandas as pd

def GetFiles():

    """ ----------------------------------------------------
    Handles input/output and excutable files

    MatrixFile := matrix file name, i.e., sys08.matrix
    OutputFile := output file name, i.e., sys08.out
    R2File     := record the larget R^2 and the adjusted R^2
    ---------------------------------------------------- """
 
 
  # get input and output file names

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--csv", help = "Missing CSV file")

    args = parser.parse_args()

    if not args.csv:
       print(' Usage: csv_to_matrix.py -c/--csv file.csv')
       exit()
    
    
    CSVFile = args.csv
    MatrixFile = CSVFile.replace("csv","matrix")
    

    return CSVFile, MatrixFile



def main():

    CSVFile, MatrixFile = GetFiles()


    dataset = pd.read_csv(CSVFile)
    dataset.columns = [col.strip() for col in list(dataset.columns)]
    
    N_Systems, N_Columns = dataset.shape
    N_Descriptors = N_Columns - 2
    column_names = list(dataset.columns.values)
    

    # print matrix

    with open(MatrixFile, "w") as f:
       f.write(CSVFile + "\n")
       f.write ("1  \n")
       f.write ("3  \n")
       f.write ("1  \n")
       f.write ("0  \n")
       f.write("{:8d}".format(N_Systems) + "\n")
       f.write("{:8d}".format(N_Descriptors-1) + "\n")
       f.write("1  \n")
       f.write("1  \n")
   
       d0 = dataset[column_names[0]].to_numpy()
       for system in range(N_Systems):
           f.write( "{:12s}".format(d0[system]) )
       f.write( "\n")
   
       for col in range(len(column_names)-2):
           d0 = dataset[column_names[col+1]].to_numpy()
           f.write( "desc        " )
           for system in range(N_Systems):
               f.write( "{:10.4f}".format(d0[system]) )
           f.write( "\n")
   
       d0 = dataset[column_names[N_Descriptors+1]].to_numpy()
       f.write( "3.0   0.1   " )
       for system in range(N_Systems):
           f.write( "{:10.4f}".format(d0[system]) )
       f.write( "\n")


# ------------------------
if __name__ == '__main__':
    main()
