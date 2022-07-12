#!/bin/bash

set -e
set -u

readonly DATA_FILE=$1
readonly DATASET_WANTED_DIR=$2
readonly UNKNWN_WORD=$3
readonly PUBLIC_WORD=$4
readonly WANTED_WORDS=${@:5}

declare -i output_idx=0

if [ '1' != `find "${DATASET_WANTED_DIR}/training/" -mindepth 1 -type d | xargs -I{} sh -c 'ls "{}" | wc -l' | sort -u | wc -l` ]; then
  echo "ASSERT: each train directory should have equal file count"
  exit 1
fi

echo "Checking keyword dataset for duplicates..."
if [ '0' != `fdupes -r "${DATASET_WANTED_DIR}" | wc -l` ]; then
  echo "ASSERT: duplicates found"
  exit 2
fi

bash ./../src/features/build.sh

rm -f "${DATA_FILE}"

extract_features() {
  local type=$1
  local word
  for word in ${WANTED_WORDS} ${UNKNWN_WORD} ${PUBLIC_WORD} ; do
    echo "Extracting ${type} features ${word}..."
    for wav in `find "${DATASET_WANTED_DIR}/${type}/${word}/" -type f | sort`; do
      ./../bin/fe "${wav}" | xargs echo "${output_idx}" >> "${DATA_FILE}"
    done
    output_idx+=1
  done
}

extract_features "training"
extract_features "validation"
extract_features "testing"

words_from_demo() {
  if [ 'zeroonetwothreefourfivesixseveneightnine' == "${WANTED_WORDS//[[:blank:]]/}" ]
  then
    return 1
  fi
  return 0
}

check_datafile_md5() {
  local expected=$1
  local src=${DATA_FILE}
  local md5
  echo "Checking md5 ${src}..."
  md5=`md5sum "${src}" | awk '{ print $1 }'`
  #if [ "${expected}" != "${md5}" ]; then
    #echo "ASSERT: md5 mismatch ${expected} != ${md5}"
    #exit 3
  #fi
}


echo "Zipping..."
mkdir -p "`dirname "$0"`/../artifacts/"
lrzip "${DATA_FILE}" -z -o "`dirname "$0"`/../artifacts/`basename "${DATA_FILE}"`.lrz"
