import numpy as np

def read_matrix(matrix_file):

  # read the file and save it as a list of lines in variable "file_lines" 

    file_      = open(matrix_file, "r")  
    file_lines = ( file_.readlines() )  
    file_.close()


  # store variables

    title                = str(file_lines[0].strip())
    print_flag           = int(file_lines[1].strip())
    normalization_flag   = int(file_lines[2].strip())
    shift_flag           = int(file_lines[3].strip())
    skipped_systems      = [int(i)   for i in file_lines[4].split()]
    no_of_systems        = int(file_lines[5].strip())
    no_of_electronics    = int(file_lines[6].strip())
    no_of_sterics        = int(file_lines[7].strip())
    no_of_buried_volumes = int(file_lines[8].strip())
    system_tags          = [str(s)   for s in file_lines[9].split()]
    experimental_tag     = str(file_lines[10].split()[0])
    experimental_data    = [float(e) for e in file_lines[10].split()[1:]]


  # define and store arrays 

    electronic_tags        = []
    electronic_descriptors = []
    buried_volumes         = []
    radius_proximal        = []
    radius_distal          = []

    for line in file_lines[11 : 11 + no_of_electronics]:
        electronic_tags.append(line.split()[0])

        for x in line.split()[1:]:
            electronic_descriptors.append(float(x))


    for line in file_lines[ 11 + no_of_electronics : 
                            11 + no_of_electronics + no_of_buried_volumes]:
        radius_proximal.append(float(line.split()[0]))
        radius_distal.append(float(line.split()[1]))

        for x in line.split()[2:]:
            buried_volumes.append(float(x))


  # convert to numpy arrays

    skipped_systems         = np.array(skipped_systems)       
    experimental_data       = np.array(experimental_data)       
    electronic_descriptors  = np.array(electronic_descriptors)  
    radius_proximal         = np.array(radius_proximal)         
    radius_distal           = np.array(radius_distal)           
    buried_volumes          = np.array(buried_volumes)           

    
  # reshape 1D arrays to 2D
    
    electronic_descriptors = electronic_descriptors.reshape((no_of_electronics, no_of_systems))
    if no_of_sterics == 1:
       buried_volumes = buried_volumes.reshape((no_of_buried_volumes, 1*no_of_systems))
    else:
       buried_volumes = buried_volumes.reshape((no_of_buried_volumes, 2*no_of_systems))


  # all done - return values

    return (title             , print_flag             , normalization_flag   ,
            shift_flag        , skipped_systems        , no_of_systems        ,
            no_of_electronics , no_of_sterics          , no_of_buried_volumes ,
            system_tags       , experimental_tag       , experimental_data    , 
            electronic_tags   , electronic_descriptors , radius_proximal      , 
            radius_distal     , buried_volumes         )

# --- End of function read_matrix ---------------------------------------------


def write_matrix(matrix_file          , title             , print_flag             , 
                 normalization_flag   , shift_flag        , skipped_systems        , 
                 no_of_systems        , no_of_electronics , no_of_sterics          , 
                 no_of_buried_volumes , system_tags       , experimental_tag       , 
                 experimental_data    , electronic_tags   , electronic_descriptors , 
                 radius_proximal      , radius_distal     , buried_volumes         ):


  # write the matrix. Start opening the output file

    with open(matrix_file, "w") as f: 
         f.write( title                              + '\n'
                + "{:8d}".format(print_flag)         + '\n'
                + "{:8d}".format(normalization_flag) + '\n'
                + "{:8d}".format(shift_flag)         + '\n')

         for i in range(len(skipped_systems)) : 
               f.write( "{:8d}".format(skipped_systems[i]) )
         f.write( '\n')
     
         f.write( "{:8d}".format(no_of_systems)        + '\n' 
                + "{:8d}".format(no_of_electronics)    + '\n' 
                + "{:8d}".format(no_of_sterics)        + '\n' 
                + "{:8d}".format(no_of_buried_volumes) + '\n')
         
         f.write('            ')
         for i in range(no_of_systems) : 
               f.write( "{:>14s}".format(system_tags[i]) )
         f.write( '\n')
     
         f.write( "{:12s}".format(experimental_tag) )
         for i in range(no_of_systems) : 
               f.write( "{:14.5e}".format(experimental_data[i]) )
         f.write( '\n')
     
         for r in range(no_of_electronics):
               f.write( "{:12s}".format(electronic_tags[r]) )

               for i in range(no_of_systems) : 
                   f.write( "{:14.5e}".format(electronic_descriptors[r][i]) )
               f.write( '\n')
         
         for r in range(no_of_buried_volumes):
               f.write( "{:6.2f}".format(radius_proximal[r])  
                      + "{:6.2f}".format(radius_distal[r]) )

               if no_of_sterics == 1:
                  for i in range(no_of_systems) : 
                      f.write( "{:9.3f}".format(buried_volumes[r][i]) )
               else:
                  for i in range(no_of_systems) : 
                      f.write( "{:9.3f}".format(buried_volumes[r][2*i])  
                             + "{:7.3f}".format(buried_volumes[r][2*i+1]) )

               f.write( '\n')


    return()

# --- End of function read_matrix ---------------------------------------------

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

        if no_of_sterics == 1:
            for s in range(no_of_buried_volumes):
                out_vbu[s][r] = buried_volumes[s][r]
         
        if no_of_sterics == 2:
            for s in range(no_of_buried_volumes):
                r1 = r*2
                r2 = out_indices[r]*2
                out_vbu[s][r1] = buried_volumes[s][r2]
                out_vbu[s][r1+1] = buried_volumes[s][r2+1]


  # all done, return the reordered data

    return(out_tag, out_exp, out_ele, out_vbu)

# --- End of function reorder_matrix ---------------------------------------------

