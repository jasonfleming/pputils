from struct import unpack,pack
import sys
import numpy as np

# TODO: make it general, for single and double precision!!!

# can use either of these statements to skip through 4 unwanted bytes
# garbage = unpack('>i', f.read(4))[0]
# f.seek(4,1)


# to determine if user is running python2 or python3
if (sys.version_info > (3, 0)):
	version = 3
elif (sys.version_info > (2, 7)):
	version = 2

endian = '>'

# open *.slf file
#f = open("no_ecf_interp.slf","rb")
f = open("f2d_malpasset-small.slf","rb")
garbage = unpack('>i', f.read(4))[0]

if (version == 2):
	title = unpack('>72s', f.read(72))[0]
	precision = unpack('>8s', f.read(8))[0]
else:
	title = unpack('>72s', f.read(72))[0].decode()
	precision = unpack('>8s', f.read(8))[0].decode()
garbage = unpack('>i', f.read(4))[0]

print(f.tell())

print(title[0:71])
print(precision[0:7])

garbage = unpack('>i', f.read(4))[0]
NBV1 = unpack('>i', f.read(4))[0] # variables
NBV2 = unpack('>i', f.read(4))[0] # quad variables, not used
garbage = unpack('>i', f.read(4))[0]

# print(NBV1,NBV2)

# names and units of each variable
vars = []

# each item in the vars list has 32 characters; 16 for name, and 16 for unit
for i in range(NBV1):
	garbage = unpack('>i', f.read(4))[0]
	if (version ==2):
		vars.append(unpack('>32s', f.read(32))[0])
	else:
		vars.append(unpack('>32s', f.read(32))[0].decode())
	garbage = unpack('>i', f.read(4))[0]
	
# variable names and units as lists
vnames = []; vunits = [];

for i in range(NBV1):
	vnames.append(vars[i][0:15])
	vunits.append(vars[i][16:31])
	# this strips the trailing spaces from the units
	#vunits.append(vars[i][16:31].strip())
	
print(vnames)
print(vunits)

# IPARAM
garbage = unpack('>i', f.read(4))[0]
IPARAM = unpack('>10i', f.read(10*4))
garbage = unpack('>i', f.read(4))[0]

# print(IPARAM)

# if the last element of IPARAM is 1, then the *.slf file
# contains the date
if (IPARAM[-1] == 1):
	garbage = unpack('>l', f.read(4))[0]
	# date is 6 integers stored as a list
	DATE = unpack('>6i', f.read(6*4))
	garbage = unpack('>i', f.read(4))[0]
	# print(DATE)
#else:
	# No date ...
	# print('no date in file')
	
# NELEM, NPOIN, NDP, dummy
garbage = unpack('>i', f.read(4))[0]
NELEM = unpack('>l', f.read(4))[0]
NPOIN = unpack('>l', f.read(4))[0]
NDP = unpack('>i', f.read(4))[0]
dummy = unpack('>i', f.read(4))[0]
garbage = unpack('>i', f.read(4))[0]

# print(NELEM, NPOIN, NDP, dummy)

# read IKLE array
# make sure it is 32 bit integers
IKLE = np.zeros((NELEM, NDP), dtype=np.int32)

garbage = unpack('>i', f.read(4))[0]
for i in range(NELEM):
	IKLE[i,0] = unpack('>l', f.read(4))[0]
	IKLE[i,1] = unpack('>l', f.read(4))[0]
	IKLE[i,2] = unpack('>l', f.read(4))[0]

garbage = unpack('>i', f.read(4))[0]

# print(IKLE)

# read IPOBI array
IPOBO = np.zeros(NPOIN, dtype=np.int32)
garbage = unpack('>i', f.read(4))[0]
for i in range(NPOIN):
	IPOBO[i] = unpack('>l', f.read(4))[0]
garbage = unpack('>i', f.read(4))[0]

# print(IPOBO)

# read x 
x = np.zeros(NPOIN)
garbage = unpack('>i', f.read(4))[0]
for i in range(NPOIN):
	x[i] = unpack('>f', f.read(4))[0] # this says float of sign 4
garbage = unpack('>i', f.read(4))[0]

# print(x)

# read y 
y = np.zeros(NPOIN)
garbage = unpack('>i', f.read(4))[0]
for i in range(NPOIN):
	y[i] = unpack('>f', f.read(4))[0] # this says float of sign 4
garbage = unpack('>i', f.read(4))[0]

# print(y)

# to determine how many time steps in the *.slf file
time = []

pos_prior_to_time_reading = f.tell()
# print(f.tell())

# this code here gets the times of the selafin file
while True:
	try:
		# get the times
		f.seek(4,1)
		time.append( unpack('>f', f.read(4))[0] )
		f.seek(4,1)
		
		# skip through the variables
		f.seek(NBV1*(4+4*NPOIN+4), 1)
		
		# skip the variables
		# 4 at begining and end are garbage
		# 4*NPOIN assumes each times step there are NPOIN nodes of 
		# size 4 bytes (i.e., single precision)
		# f.seek(NBV1*(4+4*NPOIN+4), 1)
	except:
		break
	
print(time)

# rewinds the file back to the position before time was read
f.seek(pos_prior_to_time_reading)

# now we can go and read the variables we want ...

# time2 is exacly the same as time
time2 = []

# time index
t = -1
###########################################################################
# desired time index
t_des = 0

# desired variable index
v_des = 0
###########################################################################

temp = np.zeros((NBV1,NPOIN))

while True:
	try:
		f.seek(4,1)
		time2.append( unpack('>f', f.read(4))[0] )
		f.seek(4,1)
		
		t = t + 1
		
		if ((t_des - t) < 0.1):
			for i in range(NBV1):
				f.seek(4,1)
				for j in range(NPOIN):
					temp[i,j] = unpack('>f', f.read(4))[0]
				f.seek(4,1)
		else:
			f.seek(NBV1*(4+4*NPOIN+4), 1)
		
	except:
		break
		f.close()

# print(time2)
#print(temp.shape)

# to output the extracted stuff from a file
fout = open('out.txt', 'w')

fout.write('x y ' + vnames[v_des].strip() + '\n')
for i in range(NPOIN):
	fout.write(str(x[i]) + ' ' + str(y[i]) + ' ' + str(temp[v_des,i]) + '\n')
	
fout.close()




'''
# for time step 0
################################################
garbage = unpack('>i', f.read(4))[0]
time.append( unpack('>f', f.read(4))[0] )
garbage = unpack('>i', f.read(4))[0]

bottom = np.zeros(NPOIN)
garbage = unpack('>i', f.read(4))[0]
for i in range(NPOIN):
	bottom[i] = unpack('>f', f.read(4))[0]
garbage = unpack('>i', f.read(4))[0]

################################################

'''




'''
# this is how sebastien bourban did it
# I made it work for python3 and python2
# ~~ Read title ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
l,title,chk = unpack(endian+'i80si',f.read(4+80+4))

# ~~ Read NBV(1) and NBV(2) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
l,NBV1,NBV2,chk = unpack(endian+'iiii',f.read(4+8+4))

var_names = list()
var_units = list()

# ~~ Read variable names and units ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
for i in range(NBV1):
	# means integer, string of 16, string of 16, and integer
	l,name,unit,chk = unpack(endian+'i16s16si',f.read(4+16+16+4))
	
	# to accomodate both python2 and python 3	
	if (version == 3):
		var_names.append(name.decode())
		var_units.append(unit.decode())
	elif (version == 2):
		var_names.append(name)
		var_units.append(unit)

print(var_names)
print(var_units)

# ignore cladenstine variables

# ~~ Read IPARAM array ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
d = unpack(endian+'12i',f.read(4+40+4)) # it reads 12 integers as a tupple
IPARAM = d[1:11]
#print(IPARAM)

# ~~ Read NELEM3, NPOIN3, NDP3, NPLAN ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
l,NELEM3,NPOIN3,NDP3,NPLAN,chk = unpack(endian+'6i',f.read(4+16+4))

# the problem is here ... somehow it thinks there is only one node!!!
print(NPOIN3)

# ~~ Read the IKLE array ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
f.seek(4,1)
IKLE3 = np.array( unpack(endian+str(NELEM3*NDP3)+'i',f.read(4*NELEM3*NDP3)) ) - 1
f.seek(4,1)

# ~~ Read the IPOBO array ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
f.seek(4,1)
IPOB3 = np.asarray( unpack(endian+str(NPOIN3)+'i',f.read(4*NPOIN3)) )
f.seek(4,1)
'''



