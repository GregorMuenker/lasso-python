#!/bin/bash

if ! command -v mc &> /dev/null; then
    curl -O https://dl.min.io/client/mc/release/linux-amd64/mc
    chmod +x mc
    sudo mv mc /usr/local/bin/
fi

mc alias set myminio ${MINIO_SERVER} ${MINIO_ACCESS_KEY} ${MINIO_SECRET_KEY}

if mc cp -r myminio/${MINIO_BUCKET}/ignite-data /apache-ignite/work; then
    echo "Ignite data downloaded successfully."
else
    echo "Failed to download Ignite data."
fi

if mc cp -r myminio/${MINIO_BUCKET}/ignite-logs /apache-ignite/logs; then
    echo "Ignite data downloaded successfully."
else
    echo "Failed to download Ignite data."
fi
