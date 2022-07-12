#!/bin/bash

set -e
set -u

export LC_ALL=C

cd "`dirname "${BASH_SOURCE[0]}"`"

readonly DATASET_SOURCE_DIR='/tmp/openslr_libri'
readonly FEATURES_DATA_FILE='/tmp/openslr_libri.data'
readonly TAKE_NUM='1m'

bash maybe_download.sh "${DATASET_SOURCE_DIR}"
bash augment.sh "${DATASET_SOURCE_DIR}"
bash extract_features.sh "${FEATURES_DATA_FILE}" "${DATASET_SOURCE_DIR}" "${TAKE_NUM}"
bash make_artifacts.sh "${FEATURES_DATA_FILE}"
