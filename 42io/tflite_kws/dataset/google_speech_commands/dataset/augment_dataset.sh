#!/bin/bash

set -e
set -u

readonly DATASET_NOISE_DIR="${1}/_background_noise_"
readonly DATASET_WANTED_DIR=$2
readonly WANTED_WORDS=${@:3}
readonly DATASET_NOISE_FILE="${DATASET_NOISE_DIR}/noise_list.txt"
readonly AUGMENT_NUM=10

declare -i cursor=0

check_dataset_md5() {
  local expected=$1
  local src=${2:-${DATASET_WANTED_DIR}}
  local md5
  echo "Checking md5 ${src}..."
  md5=`cd "${src}" && find . -type f -print0 | sort -z | xargs -0 md5sum | md5sum | awk '{ print $1 }'`
  if [ "${expected}" != "${md5}" ]; then
    echo "ASSERT: md5 mismatch ${expected} != ${md5}"
    exit 1
  fi
}

words_from_demo() {
  if [ 'zeroonetwothreefourfivesixseveneightnine' == "${WANTED_WORDS//[[:blank:]]/}" ]
  then
    return 1
  fi
  return 0
}

shuf() {
  local filename=$1
  mawk 'BEGIN {srand(42); OFMT="%.17f"} {print rand(), $0}' "$filename" \
    | sort -k1,1n | awk '{print $2}'
}

aseq() {
  mawk "
    BEGIN { srand(${cursor}) }
    function rndf(min, max) {
      return min+rand()*(max-min)
    }
    function rndi(min, max) {
      return int(min+rand()*(max-min+1))
    }
    function augment(arr) {
      for(i=0; i<${AUGMENT_NUM}; i++) {
        do {
          v = sprintf(\"${1}%%d.wav\n\", ${2})
        } while(v in arr)
        arr[v] = 00
        printf(v, i)
      }
    }
    { augment() }"
}

a1x() {
  aseq 'sox -R %s.wav -p norm %d | sox -R -G -p -p pitch %d | sox -R -v0.99 -p -b16 %s_a1' \
       '$1, rndi(-25,-2), 16*rndi(-20,20), $1'
}

a2x() {
  aseq 'sox -R %s.wav -p norm %d | sox -R -G -p -p pitch %d | sox -R -G -p -p reverb %d %d %d | sox -R -v0.99 -p -b16 %s_a2' \
       '$1, rndi(-25,0), 16*rndi(-20,20), rndi(1,100), rndi(1,100), rndi(1,100), $1'
}

a3x() {
  aseq 'sox -R %s.wav -p norm %d | sox -R -G -p -p pitch %d | sox -R -G -p -p echo 1 %f %d %f trim 0 1 | sox -R -v0.99 -p -b16 %s_a3' \
       '$1, rndi(-25,0), 16*rndi(-20,20), rndf(0.1,0.5), rndi(1,250), rndf(0.1,1), $1'
}

a4x() {
  aseq 'sox -R %s.wav -p norm %d | sox -R -G -p -p pitch %d | sox -R -G -p -p echo 1 %f %d %f %d %f trim 0 1 | sox -R -v0.99 -p -b16 %s_a4' \
       '$1, rndi(-25,0), 16*rndi(-20,20), rndf(0.1,0.5), rndi(1,350), rndf(0.1,0.5), rndi(1,350), rndf(0.1,0.5), $1'
}

a5x() {
  local noise
  noise=`shuf "${DATASET_NOISE_FILE}" \
    | awk -v c="${cursor}" '{rows[NR-1]=$0};END{c=c%NR; print rows[c]}'`
  aseq "sox -R %s.wav -p norm | sox -R -G -m -v%f -p -v%f ${DATASET_NOISE_DIR}/${noise} -p | sox -R -v0.99 -p -b16 %s_a5" \
       '$1, rndf(0.1,0.95), rndf(0.01,0.05), $1'
}

list_word_wav() {
  find "${DATASET_WANTED_DIR}/training/${1}/" -type f \
    | sort \
    | awk -F '.' '{for(i=1;i<NF-1;i++) printf("%s.", $i); print $(NF-1)}'
}

exec_list() {
  tr '\n' '\0' | xargs -0 -I{} sh -c '{}'
}


for word in ${WANTED_WORDS} ; do
  echo "Augmentation ${word}..."
  for wav in `list_word_wav "${word}"`; do
    echo "${wav}" | a1x | exec_list
    echo "${wav}" | a2x | exec_list
    echo "${wav}" | a3x | exec_list
    echo "${wav}" | a4x | exec_list
    echo "${wav}" | a5x | exec_list
    cursor+=1
  done
done


