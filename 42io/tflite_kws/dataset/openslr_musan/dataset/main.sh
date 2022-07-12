#!/bin/bash

set -e
set -u

export LC_ALL=C

cd "`dirname "${BASH_SOURCE[0]}"`"

readonly DATASET_SOURCE_DIR='/tmp/openslr_musan'
readonly FEATURES_DATA_FILE='/tmp/openslr_musan.data'

bash maybe_download.sh "${DATASET_SOURCE_DIR}"
bash extract_features.sh "${FEATURES_DATA_FILE}" "${DATASET_SOURCE_DIR}"
bash make_artifacts.sh "${FEATURES_DATA_FILE}"