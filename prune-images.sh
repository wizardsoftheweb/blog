#!/usr/bin/env bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
IMAGES=$(
    find "${SCRIPT_DIR}/static/images" -type f |
        sed -e 's#/static/images##' |
        sed -e "s#${SCRIPT_DIR}##"
)

for image in ${IMAGES}; do
    if ! grep -qR "${image}" "${SCRIPT_DIR}/content/posts"; then
        mkdir -p "${SCRIPT_DIR}/remove/$(dirname "${image}")"
        mv "${SCRIPT_DIR}/static/images/${image}" "${SCRIPT_DIR}/remove/${image}"
    fi
done
