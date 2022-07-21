#!/bin/bash
PARAMETER=0
if [ -z $1 ]; then
PARAMETER=1
fi
if [ -z $2 ]; then
PARAMETER=1
fi
if [ -z $3 ]; then
PARAMETER=1
fi
if [ -z $4 ]; then
PARAMETER=1
fi
if [ -z $5 ]; then
PARAMETER=1
fi

if [ $PARAMETER -eq 1 ]; then
echo "Parameters not set enter as [test_model.sh dataset keyword index target gt/lt]"
echo "dataset = testing/training/vaildation"
echo "keyword = keyword folder for index test"
echo "index = nColumn of KW"
echo "target = 0 - 1 float of target value"
echo "gt/lt = 1=gt 0=lt test of target"
exit 0
fi
i=0
target=$(echo "($4 * 100000000000000000) / 1" | bc)
echo -n "" > files.txt
for f in $1/$2/*.wav; do
	hit=$(../bin/fe "$f" | ../bin/guess non-stream-dcnn.tflite 2>/dev/null | awk -v c1=$3 '{ print $c1 }')
	#echo $hit
        scaled=$(echo "($hit * 100000000000000000) / 1" | bc)
        if [ $5 -eq 1 ]; then
          if [ $scaled -gt $target ]; then
          echo $hit $f
          echo $f >> files.txt
          i=$((i+1))
          fi
        fi
        if [ $5 -eq 0 ]; then
          if [ $scaled -lt $target ]; then
          echo $hit $f
          echo $f >> files.txt
          i=$((i+1))
          fi
        fi
done
echo $i files found
