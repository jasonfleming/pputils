#!/bin/bash          

# generate the Triangle poly file
python gis2triangle.py -n nodes.csv -b boundary.csv -l lines.csv -h holes.csv -o out.poly

# move poly file to Triangle's directory
mv *.poly /home/pprodano/Desktop/pputils_v1.0/triangle/bin

# change directory, and go to Triangle
cd /home/pprodano/Desktop/pputils_v1.0/triangle/bin

# execute Triangle
./triangle_64 out.poly

# move Triangle's files to root of pputils
mv out* /home/pprodano/Desktop/pputils_v1.0

# change directory back to root of pputils
cd /home/pprodano/Desktop/pputils_v1.0

# run triangle2adcirc converstion
python triangle2adcirc.py -n *.node -e *.ele -o out.grd

# produce the WKT file
python adcirc2wkt.py -i out.grd -o outWKT_e.csv outWKT_n.csv

