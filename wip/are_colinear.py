# finds out if the set of points are colinear

import itertools

def arecolinear(points):
    xdiff1 = float(points[1][0] - points[0][0])
    ydiff1 = float(points[1][1] - points[0][1])
    xdiff2 = float(points[2][0] - points[1][0])
    ydiff2 = float(points[2][1] - points[1][1])

    # infinite slope?
    if xdiff1 == 0 or xdiff2 == 0:
        return xdiff1 == xdiff2
    elif ydiff1/xdiff1 == ydiff2/xdiff2:
        return True
    else:
        return False

# this is an array of tupples
pointlist = [(10, 20), (55, 18), (10, -45.5), (90, 34), (-34, -67), (10, 99)]

for points in itertools.combinations(pointlist, 3):
	if arecolinear(points):
		print points
		print 'Points are colinear'
		print ' '
	else:
		print points
		print 'Points are NOT colinear'
		print ' '
