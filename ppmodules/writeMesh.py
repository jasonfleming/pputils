#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import numpy             as np             # numpy
# 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Functions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def writeAdcirc(n,e,x,y,z,ikle):
	
	# everything gets stored in this master list, where each entry
	# is a line in the output adcirc file
	master = list()
	
	# now to write the adcirc mesh file
	master.append("ADCIRC" + "\n")
	# writes the number of elements and number of nodes in the header file
	master.append(str(e) + " " + str(n) + "\n")
	
	# writes the nodes
	for i in range(n):
		master.append(str(i+1) + " " + str("{:.3f}".format(x[i] )) + " " + 
			str("{:.3f}".format(y[i])) + " " + str("{:.3f}".format(z[i])) + "\n")
	
	# writes the elements
	# the readAdcirc function assigns the ikle starting at zero, so that is why
	# we have to add 1
	for i in range(e):
		master.append(str(i+1) + " 3 " + str(ikle[i,0]+1) + " " + str(ikle[i,1]+1) + 
			" " + 	str(ikle[i,2]+1) + "\n")

	return master

