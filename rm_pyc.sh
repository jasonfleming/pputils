#!/bin/bash          

echo "Deleting the following *.pyc files recursively ... "

# to list all files ending with *.pyc
find . -iname "*.pyc" -type f

# to delete them all
find . -iname "*.pyc" -type f -exec rm -rf {} \;

