#!/bin/bash          

# generate the Triangle poly file
echo "Running gis2triangle.py"
time python gis2triangle.py -n nodes.csv -b boundary.csv -l lines.csv -h holes.csv -o out.poly

# move poly file to Triangle's directory
mv *.poly /home/pprodano/Desktop/pputils_v1.1/triangle/bin

# change directory, and go to Triangle
cd /home/pprodano/Desktop/pputils_v1.1/triangle/bin

# sleep for 2 seconds
sleep 2

# execute Triangle
./triangle_64 out.poly

# move Triangle's files to root of pputils
mv out* /home/pprodano/Desktop/pputils_v1.1

# change directory back to root of pputils
cd /home/pprodano/Desktop/pputils_v1.1

# run triangle2adcirc converstion
python triangle2adcirc.py -n *.node -e *.ele -o out.grd

# produce the WKT file
python adcirc2wkt.py -i out.grd -o outWKT_e.csv outWKT_n.csv

