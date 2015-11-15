#
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#                                                                       #
#                                 transp.py                             # 
#                                                                       #
#+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!+!
#
# Author: Pat Prodanovic, Ph.D., P.Eng.
# 
# Date: Oct 21, 2015
#
# Purpose: Script takes in a telemac results file, and transposes results
# of a particular time step to another mesh. This is useful for generating
# hot start files. If the meshes are the same, no need to run this script,
# but simply run chop.py (which already exists in Telemac python scripts).
#
# WARNING #
# Note the mesh.slf should be completely enclosed within the results file.
# Otherwise, this script will just assign 0.0 to that part of the mesh
# that lies outside the boundary of the results file. There is a warning
# that is given to the user when this happens.
#
# Uses: Python2.7.9, Matplotlib v1.4.2, Numpy v1.8.2
#
# Example:
#
# python transp.py -r result.slf -t 0 -m mesh.slf -o mesh_transp.slf
# where:
# -r telemac result file
# -t time index to extract (see probe.py for time indexes)
# -m the input *.slf mesh which will be used to tranpose the result to
# -o final output file with the transposed results, for the time step t
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os,sys                              # system parameters
import matplotlib.tri    as mtri           # matplotlib triangulations
import numpy             as np             # numpy
from parsers.parserSELAFIN import SELAFIN
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
curdir = os.getcwd()
#
# I/O
if len(sys.argv) != 9 :
	print 'Wrong number of Arguments, stopping now...'
	print 'Usage:'
	print 'python transp.py -r result.slf -t 0 -m mesh.slf -o mesh_transp.slf'
	sys.exit()

dummy1 =  sys.argv[1]
result_file = sys.argv[2]
dummy2 =  sys.argv[3]
t = int(sys.argv[4])
dummy3 =  sys.argv[5]
mesh_file = sys.argv[6]
dummy4 = sys.argv[7]
output_file = sys.argv[8]

# reads the results *.slf file
res = SELAFIN(result_file)

# get the mesh geometry of the results file
x_r = res.MESHX
y_r = res.MESHY
ikle_r = np.array(res.IKLE2)


# immutables tupples for variable names and their units
var_r = []
units_r = []
for var_names in res.VARNAMES[0:len(res.VARNAMES)]:
	var_r.append(var_names)
for unit_names in res.VARUNITS[0:len(res.VARUNITS)]:
	units_r.append(unit_names)

# master results list (for time step t)
results = []

# reads all results for time t
for i,n in enumerate(res.VARNAMES[0:len(res.VARNAMES)]):
	values = res.getVALUES(t)
	results.append(values[i])

# this creates the results list
# if there is 7 vars, the size of the list will be 7
# if we go, results[0] we will get an array of size n, where n is the
# number of mesh nodes for variable at index 0

# reads the mesh *.slf file
mesh = SELAFIN(mesh_file)

# get the mesh geometry of the mesh file
x_m = mesh.MESHX
y_m = mesh.MESHY
ikle_m = np.array(mesh.IKLE2)

# now the task is to create another results list (the one that is
# interpolated to the mesh

mesh_results = list()
dummy = list()
for j in range(len(x_m)):
	dummy.append(j-j + 0.0)
	
# create an empty mesh_results
for i,n in enumerate(res.VARNAMES[0:len(res.VARNAMES)]):
	mesh_results.append(dummy)

# now, to use matplotlib and interpolate every variable to the new mesh
# create a matplotlib triangulation object
triang = mtri.Triangulation(x_r, y_r, ikle_r)

# to test writing the output to a text file
#fout = open('output.txt',"w")

# to perform the triangulation for each variable in the result file
for i in range (res.NVAR):
	interpolator = mtri.LinearTriInterpolator(triang,results[i])
	mesh_results[i] = interpolator(x_m, y_m)
	
# convert mesh_results to a numpy array with all zeros
mesh_results_np = np.zeros((len(res.VARNAMES), len(mesh.MESHX) ))

'''transfer values from mesh_results list to mesh_results_np array
this would be very inefficient for large result files, but it will
have to do for now

TODO vectorize this!!!'''

# i is variable, j is the mesh node
for i in range(len(res.VARNAMES)):
	for j in range(len(mesh.MESHX)):
		mesh_results_np[i,j] = mesh_results[i][j]
		# if there is a nan, replace it with zeros
		if (np.isnan(mesh_results_np[i,j])):
			mesh_results_np[i,j] = 0.0
		#fout.write(str(mesh_results_np[i,j]) + ' ')
	#fout.write(str('\n'))	
			
# writes the mesh_transp
out = SELAFIN('')

#print '     +> Set SELAFIN variables'
out.TITLE = 'created by pputils'
out.NBV1 = res.NVAR
out.NVAR = res.NVAR
out.VARINDEX = range(res.NVAR)
for i in range(res.NVAR):
	out.VARNAMES.append(var_r[i])
	out.VARUNITS.append(units_r[i])
	
#print '     +> Set SELAFIN sizes'
out.NPLAN = mesh.NPLAN
out.NDP2 = mesh.NDP2
out.NDP3 = mesh.NDP3
out.NPOIN2 = mesh.NPOIN2
out.NPOIN3 = mesh.NPOIN3
out.NELEM2 = mesh.NELEM2
out.NELEM3 = mesh.NELEM2
out.IPARAM = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]

#print '     +> Set SELAFIN mesh'
out.MESHX = mesh.MESHX
out.MESHY = mesh.MESHY

#print '     +> Set SELAFIN IPOBO'
out.IPOB2 = mesh.IPOB2
out.IPOB3 = mesh.IPOB3

#print '     +> Set SELAFIN IKLE'
out.IKLE2 = mesh.IKLE2
out.IKLE3 = mesh.IKLE3

#print '     +> Set SELAFIN times and cores'
# these two lists are empty after constructor is instantiated
out.tags['cores'].append(0)
out.tags['times'].append(0)

#print '     +> Set SELAFIN date'
out.DATETIME = [2015, 1, 1, 1, 1, 1]

#print '     +> Write SELAFIN headers'
out.fole.update({ 'hook': open(output_file,'w') })
out.fole.update({ 'name': 'Created by pputils' })
out.fole.update({ 'endian': ">" })     # big endian
out.fole.update({ 'float': ('f',4) })  # single precision

out.appendHeaderSLF()
out.appendCoreTimeSLF(0) 

for i in range (res.NVAR):
	#fout.write(str(mesh_results[i]))
	out.appendCoreVarsSLF([mesh_results_np[i]])
