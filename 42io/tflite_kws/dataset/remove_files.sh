#!/bin/bash
last=""
count=0
input="files.txt"

while IFS= read -r line1
do
  rm "$line1"
done < "$input"


