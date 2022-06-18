#!/bin/bash
for f in *.wav; do
  mv "$f" /tmp/dc1.wav
  dc=$(ffprobe -f lavfi "amovie=/tmp/dc1.wav,astats=metadata=1" 2>&1 | sed '/Overall/,$!d' | grep DC ) 
  #echo "$dc"
  dc=$(echo "$dc" | awk '{ print $6 }')
  #echo "$dc"
  dc=$(echo "$dc * -1" | bc)
  echo "bc" "$dc"
  ffmpeg -hide_banner -loglevel error -y -i "/tmp/dc1.wav" -af "dcshift=$dc:limitergain=0.02" "$f"
done

