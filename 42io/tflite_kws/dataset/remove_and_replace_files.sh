#!/bin/bash

if [ -z $1 ]; then
echo "remove_and_replace_files.sh [source dir]"
exit 0
fi
input="files.txt"

while IFS= read -r line1
do
  #rm "$line1"
  for f in $1/*.wav; do
    dest=$(dirname "$line1")
    filename=$(basename "$f")
    mv "$f" "$dest/$filename"
    rm "$line1"
    break
  done

done < "$input"


