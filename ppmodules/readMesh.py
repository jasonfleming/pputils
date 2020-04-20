#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import numpy as np # numpy
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Functions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def readAdcirc(adcirc_file):

  fin = open(adcirc_file)

  # first line is the title string
  str = fin.readline()

  # second line is e, n
  str = fin.readline()
  e = int(str.split()[0])
  n = int(str.split()[1])

  # now we can declare the arrays that are needed to store the values read
  x = np.zeros(n, dtype=np.float64)
  y = np.zeros(n, dtype=np.float64)
  z = np.zeros(n, dtype=np.float64)

  ikle = np.zeros( (e,3), dtype = np.int64)

  # now we can read in the nodes
  for i in range(n):
    str = fin.readline()
    lst = str.split()

    x[i] = lst[1]
    y[i] = lst[2]
    z[i] = lst[3]

  # now we can read in the element connectivity
  for j in range(e):
    str = fin.readline()
    lst = str.split()

    ikle[j,0] = int(lst[2])
    ikle[j,1] = int(lst[3])
    ikle[j,2] = int(lst[4])

  # now we shift the element connectivities, so that they are zero based
  ikle[:,0] = ikle[:,0] - 1
  ikle[:,1] = ikle[:,1] - 1
  ikle[:,2] = ikle[:,2] - 1
  
  return n,e,x,y,z,ikle

def read2dm(two_dm_file):

  fin = open(two_dm_file)

  # https://stackoverflow.com/questions/845058/how-to-get-line-count-of-a-large-file-cheaply-in-python
  # this code here cheaply reads the number of lines of a text file
  def _make_gen(reader):
    b = reader(1024 * 1024)
    while b:
      yield b
      b = reader(1024*1024)
  def rawgencount(filename):
    f = open(filename, 'rb')
    f_gen = _make_gen(f.raw.read)
    return sum( buf.count(b'\n') for buf in f_gen )

  num_lines = rawgencount(two_dm_file)

  # because of the header line, the total number of lines in the file
  # (which is nodes and elements joined is) n_plus_e
  n_plus_e = num_lines - 1

  # reads the header line
  str = fin.readline()

  # the number of elements counter
  e = 0
  n = 0
  
  # go through each line and count the total number of elements and nodes
  for i in range(n_plus_e):
    str = fin.readline()
    three_chars = str[0:3]
    two_chars = str[0:2]
    
    if (three_chars == 'E3T'):
      e = e + 1
    if (two_chars == 'ND'):
      n = n + 1

  fin.close()

  # open the same file again
  fin = open(two_dm_file)
  
  # now we can declare the arrays that are needed to store the values read
  x = np.zeros(n, dtype=np.float64)
  y = np.zeros(n, dtype=np.float64)
  z = np.zeros(n, dtype=np.float64)

  ikle = np.zeros( (e,3), dtype = np.int64)

  # counters for nodes and elements
  node_count = 0
  ele_count = 0
  
  # now to fill in x,y,z and ikle arrays
  for i in range(n_plus_e):
    str = fin.readline()
    three_chars = str[0:3]
    two_chars = str[0:2]
    tmp = str.split(' ')
    
    if (three_chars == 'E3T'):
      
      ele_count = int(tmp[1])
      ikle[ele_count-1,0] = int(tmp[2])
      ikle[ele_count-1,1] = int(tmp[3])
      ikle[ele_count-1,2] = int(tmp[4])

    if (two_chars == 'ND'):
      node_count = int(tmp[1])
      x[node_count-1] = float(tmp[2])
      y[node_count-1] = float(tmp[3])
      z[node_count-1] = float(tmp[4])

  fin.close()

  # now we shift the element connectivities, so that they are zero based
  ikle[:,0] = ikle[:,0] - 1
  ikle[:,1] = ikle[:,1] - 1
  ikle[:,2] = ikle[:,2] - 1
  
  return n,e,x,y,z,ikle

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
  x = np.zeros(n, dtype=np.float64)
  y = np.zeros(n, dtype=np.float64)
  z = np.zeros(n, dtype=np.float64)

  # this is the ikle array, but it has the shape that includes all
  # elements (1d+2d)
  ikle = np.zeros( (e,3), dtype=np.int64)

  # element type flag in the *.dat mesh (103 = 1d mesh; 203 = 2d mesh)
  mesh_flag = np.zeros(e, dtype=np.int64)
  
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
  ikle2d = np.zeros((count, 3), dtype=np.int64)

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
