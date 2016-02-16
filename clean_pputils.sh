#!/bin/bash          
############################
echo "Deleting the following *.pyc files recursively ... "

# to list all files ending with *.pyc
find . -iname "*.pyc" -type f

# to delete them all
find . -iname "*.pyc" -type f -exec rm -rf {} \;
############################
echo "Deleting the following *~ files recursively ... "

# to list all files ending with *.pyc
find . -iname "*~" -type f

# to delete them all
find . -iname "*~" -type f -exec rm -rf {} \;


############################
echo "Deleting the following __pycache__ files recursively ... "
# to list all "__pycache__" directories 
find . -iname "__pycache__" -type d

# to delete them
find . -iname "__pycache__" -type d -exec rm -rf {} \;

############################

