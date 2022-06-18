#!/bin/bash
for f in *.wav; do
  cp "$f" /tmp/norm1.wav
  sox /tmp/norm1.wav "$f" norm -3.1
done

