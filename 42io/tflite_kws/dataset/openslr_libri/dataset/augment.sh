#!/bin/bash

set -e
set -u

readonly DATASET_DIR=$1
readonly DATASET_WAV_LIST_FILE='wav_list.txt'

declare -i cursor=0

check_dataset_md5() {
  local expected=$1
  local src=${2:-${DATASET_DIR}}
  local md5
  echo "Checking md5 ${src}..."
  if [ -d "${src}" ]; then
    md5=`cd "${src}" && find . -type f -print0 | sort -z | xargs -0 md5sum | md5sum | awk '{ print $1 }'`
  else
    md5=`md5sum "${src}" | awk '{ print $1 }'`
  fi
  if [ "${expected}" != "${md5}" ]; then
    echo "ASSERT: md5 mismatch ${expected} != ${md5}"
    rm -rf "${DATASET_DIR}"
    exit 1
  fi
}

arnd() {
  mawk "
    BEGIN { srand(${cursor}) }
    function rndf(min, max) {
      return min+rand()*(max-min)
    }
    function rndi(min, max) {
      return int(min+rand()*(max-min+1))
    }
    { printf(\"${1}.wav\n\", ${2}) }"
}

a1x() {
  arnd 'sox -R %s -p norm %d | sox -R -G -p -p pitch %d | sox -R -v0.99 -p -b16 %s_a' \
       '$1, rndi(-35,0), 16*rndi(-20,20), $1'
}

a2x() {
  arnd 'sox -R %s -p norm %d | sox -R -G -p -p pitch %d | sox -R -G -p -p reverb %d %d %d | sox -R -v0.99 -p -b16 %s_a' \
       '$1, rndi(-35,0), 16*rndi(-20,20), rndi(1,100), rndi(1,100), rndi(1,100), $1'
}

a3x() {
  arnd 'sox -R %s -p norm %d | sox -R -G -p -p pitch %d | sox -R -G -p -p echo 1 %f %d %f trim 0 1 | sox -R -v0.99 -p -b16 %s_a' \
       '$1, rndi(-35,0), 16*rndi(-20,20), rndf(0.1,0.5), rndi(1,250), rndf(0.1,1), $1'
}

a4x() {
  arnd 'sox -R %s -p norm %d | sox -R -G -p -p pitch %d | sox -R -G -p -p echo 1 %f %d %f %d %f trim 0 1 | sox -R -v0.99 -p -b16 %s_a' \
       '$1, rndi(-35,0), 16*rndi(-20,20), rndf(0.1,0.5), rndi(1,350), rndf(0.1,0.5), rndi(1,350), rndf(0.1,0.5), $1'
}

readonly AUG=(a1x a2x a3x a4x)
readonly AUG_LEN=${#AUG[@]}

echo "Augmenting..."

while IFS= read -r wav; do
  echo "${DATASET_DIR}/${wav}" | ${AUG[cursor % AUG_LEN]} | tee -a "${DATASET_DIR}/augment.log" | xargs -I{} sh -c '{}'
  mv "${DATASET_DIR}/${wav}_a.wav" "${DATASET_DIR}/${wav}"
  cursor+=1
done < "${DATASET_DIR}/${DATASET_WAV_LIST_FILE}"

check_dataset_md5 'f031675041e0159cc23ada4b0cf27e64'
