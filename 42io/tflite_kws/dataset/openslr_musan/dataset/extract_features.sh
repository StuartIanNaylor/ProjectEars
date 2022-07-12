#!/bin/bash

set -e
set -u

readonly DATA_FILE=$1
readonly DATASET_DIR=$2
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

while IFS= read -r wav; do
  ./../../google_speech_commands/bin/fe "${DATASET_DIR}/${wav}" | xargs echo >> "${DATA_FILE}"
done < "${DATASET_DIR}/${DATASET_WAV_LIST_FILE}"

check_datafile_md5 'f782c905cdba015527d570941d1d4ca6'