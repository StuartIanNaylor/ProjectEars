#!/bin/bash

set -e
set -u

readonly DATA_FILE=$1
readonly DATASET_DIR=$2
readonly TAKE_NUM=$3
readonly DATASET_WAV_LIST_FILE='wav_list.txt'

check_datafile_md5() {
  local expected=$1
  local src=${DATA_FILE}
  local md5
  echo "Checking md5 ${src}..."
  md5=`md5sum "${src}" | awk '{ print $1 }'`
  if [ "${expected}" != "${md5}" ]; then
    echo "ASSERT: md5 mismatch ${expected} != ${md5}"
    exit 2
  fi
}

bash ./../../google_speech_commands/src/features/build.sh

rm -f "${DATA_FILE}"

head -n"${TAKE_NUM}" "${DATASET_DIR}/${DATASET_WAV_LIST_FILE}" | while IFS= read -r wav; do
  ./../../google_speech_commands/bin/fe "${DATASET_DIR}/${wav}" | xargs echo >> "${DATA_FILE}"
done

check_datafile_md5 'd22802d42b46d2d87ffcb4d2e023fbee'
