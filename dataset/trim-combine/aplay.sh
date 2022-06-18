#!/bin/bash
clear
echo "key press p=play, n=next, d=delete"
for f in *.wav; do
  aplay -Dplughw:4 "$f"
  while true; do
    read -rsn1 input
    if [ "$input" = "p" ]
    then 
      aplay -Dplughw:4 "$f"
    fi
    if [ "$input" = "n" ]; then
      break
    fi
    if [ "$input" = "d" ]; then
      rm $f
      break
    fi
  done
done

