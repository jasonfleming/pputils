#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import numpy             as np             # numpy
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Functions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def readAdcirc(adcirc_file):
  #{{{
  # define lists
  x = list()
  y = list()
  z = list()
  e1 = list()
  e2 = list()
  e3 = list()
  
  # each line in the file is a list object
  line = list()
  with open(adcirc_file, "r") as f1:
    for i in f1:
      line.append(i)
    
  # to write to a temp file nodes and 2d elements only
  #temp_nodes_file ="temp_nodes.csv"
  #temp_elements_file ="temp_elements.csv"
  
  #fout_nodes = open(temp_nodes_file,"w")
  #fout_elements = open(temp_elements_file,"w")
  
  # read how elements and nodes from second line of adcirc file (line(2)
  ele_nod_str = line[1]
  ele_nod_list = ele_nod_str.split() 
  e = ele_nod_list[0]
  e = int(e)
  n = ele_nod_list[1]
  n = int(n)
  
  node_str = str("")
  # write the temp nodes file
  for i in range(2,n+2):
    #fout_nodes.write(line[i])
    node_str = line[i]
    node_str_list = node_str.split()
    x.append(node_str_list[1])
    y.append(node_str_list[2])
    z.append(node_str_list[3])
    
  
  # write the temp elements file
  for i in range(n+2,n+2+e):
    #fout_elements.write(line[i])
    ele_str = line[i]
    ele_str_list = ele_str.split()
    e1.append(ele_str_list[2])
    e2.append(ele_str_list[3])
    e3.append(ele_str_list[4])
    
  # turn these into numpy arrays
  xx = np.zeros(n)
  yy = np.zeros(n)
  zz = np.zeros(n)
  e11 = np.zeros(e)
  e22 = np.zeros(e)
  e33 = np.zeros(e)
  
  for i in range(0,n):
    xx[i] = x[i]
    yy[i] = y[i]
    zz[i] = z[i]
  
  # round the coordinates and the elevation values
  xx = np.around(xx,decimals=3)
  yy = np.around(yy,decimals=3)
  zz = np.around(zz,decimals=3)

  # -1 to change index of elements; min node number now starts at zero
  
  # matplotlib triangulation requires node numbering to start at zero,
  # whereas my adcirc node numbering start at 1
  for i in range(0,e):
    e11[i] = int(e1[i])-1
    e22[i] = int(e2[i])-1
    e33[i] = int(e3[i])-1
    
  # stack the elements
  ikle = np.column_stack((e11,e22,e33))  
  
  ikle = ikle.astype(np.int32)
  
  #print ikle.shape
  #print ikle.dtype
  
  #print xx.shape
  #print xx.dtype
  #}}}
  return n,e,xx,yy,zz,ikle

def readPly(ply_file):
  #{{{
  # define lists
  x = list()
  y = list()
  z = list()
  e1 = list()
  e2 = list()
  e3 = list()
  
  # each line in the file is a list object
  line = list()
  with open(ply_file, 'r') as f1:
    for i in f1:
      line.append(i)
  
  # reads the nodes from    
  n = line[3].split()[2]
  n = int(n)
  e = line[7].split()[2]
  e = int(e)
  
  node_str = str("")
  # read nodes from file
  for i in range(10,n+10):
    node_str = line[i]
    node_str_list = node_str.split()
    x.append(node_str_list[0])
    y.append(node_str_list[1])
    z.append(node_str_list[2])
    
  
  # write the temp elements file
  for i in range(n+10,n+10+e):
    ele_str = line[i]
    ele_str_list = ele_str.split()
    e1.append(ele_str_list[1])
    e2.append(ele_str_list[2])
    e3.append(ele_str_list[3])
    
  # turn these into numpy arrays
  xx = np.zeros(n)
  yy = np.zeros(n)
  zz = np.zeros(n)
  e11 = np.zeros(e)
  e22 = np.zeros(e)
  e33 = np.zeros(e)
  
  for i in range(0,n):
    xx[i] = x[i]
    yy[i] = y[i]
    zz[i] = z[i]
    
  # +1 to change index of elements to match
  for i in range(0,e):
    e11[i] = int(e1[i])+1
    e22[i] = int(e2[i])+1
    e33[i] = int(e3[i])+1
    
  # stack the elements
  ikle = np.column_stack((e11,e22,e33))  
  ikle = ikle.astype(np.int32)
  
  return n,e,xx,yy,zz,ikle

# reads a *.dat mesh file format; stores the ikle indexes as zero based
def readDat(dat_file):

  # open the file
  fin = open(dat_file, 'r')

  # read the first line of the *.dat file (and get nodes and elements)
  line = fin.readline()

  # these are strings
  n = int( line.split()[0] )
  e = int( line.split()[1] ) # this includes the 1d elements too

  # now we can define numpy arrays to store the mesh data
  x = np.zeros(n, dtype=np.float32)
  y = np.zeros(n, dtype=np.float32)
  z = np.zeros(n, dtype=np.float32)

  # this is the ikle array, but it has the shape that includes all
  # elements (1d+2d)
  ikle = np.zeros( (e,3), dtype=np.int32)

  # element type flag in the *.dat mesh (103 = 1d mesh; 203 = 2d mesh)
  mesh_flag = np.zeros(e, dtype=np.int32)
  
  # now we can read the *.dat file line by line, and store into arrays
  # read the nodes
  for i in range(n):
    # reads the file from the file stream as a string
    line = fin.readline()

    # converts the line as a list of strings
    lst = line.split()

    # do not have to read the node number (at lst[0])
    x[i] = float( lst[1])
    y[i] = float( lst[2])
    z[i] = float( lst[3])

  # now we are ready to store the elements into the ikle array
  # count for the 2d elements
  count = 0

  # read the elements
  for i in range(e):
    # reads the file from the file stream as a string
    line = fin.readline()

    # converts the line as a list of strings
    lst = line.split()

    # store the mesh flag (convert string to an integer)
    mesh_flag[i] = int(lst[1])

    # store everything in the ikle array (1d+2d)
    # count the ones that are 203 (these are 2d elements)
    if (mesh_flag[i] == 203):
      ikle[i,0] = lst[2]
      ikle[i,1] = lst[3]
      ikle[i,2] = lst[4]

      # update the count
      count = count + 1

  # now that we have the count for the number of 2d elements, we can define
  # the ikle2d array
  ikle2d = np.zeros((count, 3), dtype=np.int32)

  # go through the ikle array, and write only the 2d elements to the ikle2d array
  a = 0 
  for i in range(e):
    if (mesh_flag[i] == 203):
      ikle2d[a,0] = ikle[i,0]
      ikle2d[a,1] = ikle[i,1]
      ikle2d[a,2] = ikle[i,2]

      # increment the counter
      a = a + 1
      
  # the number of 2d elements is this
  e = count

  # change the indexes of the ikle2d array to zero based
  ikle2d[:,0] = ikle2d[:,0] - 1
  ikle2d[:,1] = ikle2d[:,1] - 1
  ikle2d[:,2] = ikle2d[:,2] - 1
  
  # close the input file
  fin.close()

  return n,e,x,y,z,ikle2d
