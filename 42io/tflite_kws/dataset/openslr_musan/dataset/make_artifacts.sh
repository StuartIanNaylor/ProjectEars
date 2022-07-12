#!/bin/bash

set -e
set -u

readonly DATA_FILE=$1

echo "Zipping..."
mkdir -p "`dirname "$0"`/../artifacts/"
lrzip "${DATA_FILE}" -z -L9 -o "`dirname "$0"`/../artifacts/`basename "${DATA_FILE}"`.lrz"