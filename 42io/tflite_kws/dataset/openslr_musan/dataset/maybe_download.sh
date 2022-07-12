#!/bin/bash

set -e
set -u

readonly DATASET_DIR=$1
readonly HTTP_URL='https://www.openslr.org/resources/17/musan.tar.gz'
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
    rm -r "${DATASET_DIR}"
    exit 1
  fi
}

# entry point

if [ ! -d "${DATASET_DIR}" ]; then

  wget --directory-prefix="${DATASET_DIR}" "${HTTP_URL}"

  base=`basename "${HTTP_URL}"`

  check_dataset_md5 '0c472d4fc0c5141eca47ad1ffeb2a7df' "${DATASET_DIR}/${base}"

  echo "Extracting ${base}..."
  tar zxf "${DATASET_DIR}/${base}" \
    --checkpoint-action=ttyout="#%u: %T\r" \
    -C "${DATASET_DIR}"
  rm "${DATASET_DIR}/${base}"

  mkdir "${DATASET_1S_DIR}"
  find "${DATASET_DIR}/musan" -name '*.wav' -print0 \
    | xargs -0 -I{} mv {} "${DATASET_1S_DIR}"
  rm -r "${DATASET_DIR}/musan"

  check_dataset_md5 '33eabed1773b89407c3d8cec8e79848b' "${DATASET_1S_DIR}"

  echo 'Slicing to 1s...'
  find "${DATASET_1S_DIR}" -name '*.wav' -print0 \
    | xargs -0 -I{} sox -V1 {} {} trim 0 1 : newfile : restart

  check_dataset_md5 'a5b6767a21e99ac3e401d0721d4c6554' "${DATASET_1S_DIR}"

  for wav in `find "${DATASET_1S_DIR}" -name '*.wav'`; do
    wav_size_ok "${wav}" || rm "${wav}"
  done

  echo "Checking for duplicates, be patient..."
  fdupes -rdN --order=name "${DATASET_1S_DIR}"

  check_dataset_md5 'c8c15bc75851b9179f6848d25c9f3951' "${DATASET_1S_DIR}"

  echo "Multiplexing x3..."
  for wav in ${DATASET_1S_DIR}/*.wav; do
    sox -R -v 0.6 "${wav}" "${wav%.*}_a1.wav" pitch 350
    sox -R -v 0.3 "${wav}" "${wav%.*}_a2.wav" pitch -350
  done

  echo "Checking for duplicates, be patient..."
  fdupes -rdN --order=name "${DATASET_1S_DIR}"

  check_dataset_md5 '2d373015eb63608168facbb72dc3a3dc' "${DATASET_1S_DIR}"

  find "${DATASET_1S_DIR}" -name '*.wav' \
    | sort \
    | awk -F '/' '{ print $(NF-1)"/"$NF }' \
    | shuf \
    > "${DATASET_DIR}/${DATASET_WAV_LIST_FILE}"

fi