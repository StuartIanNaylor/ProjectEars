#!/bin/bash

set -e
set -u

readonly DATASET_DIR=$1
readonly HTTP_URL='https://www.openslr.org/resources/12/train-clean-360.tar.gz'
readonly DATASET_1S_DIR="${DATASET_DIR}/_1s_"
readonly DATASET_WAV_LIST_FILE='wav_list.txt'

# functions

wav_size_ok() {
  local wav_size_in_frames=`sox --info -s "${1}"`
  if ((wav_size_in_frames != 16000)); then
    echo "Suspicious size: ${wav_size_in_frames} ${1}"
    return 1
  fi
  return 0
}

shuf() {
  mawk 'BEGIN {srand(42); OFMT="%.17f"} {print rand(), $0}' \
    | sort -k1,1n | awk '{print $2}'
}

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

# entry point

if [ ! -d "${DATASET_DIR}" ]; then

  wget --directory-prefix="${DATASET_DIR}" "${HTTP_URL}"

  base=`basename "${HTTP_URL}"`

  check_dataset_md5 'c0e676e450a7ff2f54aeade5171606fa' "${DATASET_DIR}/${base}"

  echo "Extracting ${base}..."
  tar zxf "${DATASET_DIR}/${base}" \
    --checkpoint-action=ttyout="#%u: %T\r" \
    -C "${DATASET_DIR}"
  rm "${DATASET_DIR}/${base}"

  echo 'Slicing to 1s...'
  find "${DATASET_DIR}" -name '*.flac' -print0 \
    | xargs -0 -I{} sox -V1 {} {}.wav trim 0 1 : newfile : restart

  check_dataset_md5 'a35120b42597420b9f3b369e3291322a' "${DATASET_DIR}"

  mkdir "${DATASET_1S_DIR}"
  find "${DATASET_DIR}/LibriSpeech" -name '*.wav' -print0 \
    | xargs -0 -I{} mv {} "${DATASET_1S_DIR}"
  rm -rf "${DATASET_DIR}/LibriSpeech"

  check_dataset_md5 '24664958eccb2dd7145c159ea9760c4e' "${DATASET_1S_DIR}"

  for wav in ${DATASET_1S_DIR}/*.wav; do
    wav_size_ok "${wav}" || rm "${wav}"
  done

  echo "Checking for duplicates, be patient..."
  fdupes -rdN --order=name "${DATASET_1S_DIR}"

  check_dataset_md5 'e9185ab6e7187eea43e0edb7a6b3a0a3' "${DATASET_1S_DIR}"

  find "${DATASET_1S_DIR}" -name '*.wav' \
    | sort \
    | awk -F '/' '{ print $(NF-1)"/"$NF }' \
    | shuf \
    > "${DATASET_DIR}/${DATASET_WAV_LIST_FILE}"

fi
