#!/bin/bash

FILES="*.log"
for f in $FILES
do
  echo "${f}.b"
  echo "Processing $f file..."
  sed '/^\[{/!d' $f > "${f}.b"
  rm $f
  mv "${f}.b" "${f}"
done
