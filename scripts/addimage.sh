#!/usr/bin/env bash

IMAGE_URL="${1}"



if [ -z ${IMAGE_URL} ]; then 
    echo "usage $0 <IMAGE_URL> <OUTPUT_DIR>"
    exit -1
else
    FILE_NAME="${2:-$(basename ${IMAGE_URL})}"


    
fi 
OUTPUT_DIR="${3:-static/images}"
curl -v -L -o ${OUTPUT_DIR}/${FILE_NAME} "${IMAGE_URL}"
