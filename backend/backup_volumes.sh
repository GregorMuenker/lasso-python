#!/bin/bash

if ! command -v mc &> /dev/null; then
    curl -O https://dl.min.io/client/mc/release/linux-amd64/mc
    chmod +x mc
    sudo mv mc /usr/local/bin/
fi

mc alias set myminio ${MINIO_SERVER} ${MINIO_ACCESS_KEY} ${MINIO_SECRET_KEY}

mc cp -r /var/solr myminio/${MINIO_BUCKET}/solr-data/
mc cp -r /nexus-data myminio/${MINIO_BUCKET}/opt/sonatype-work/nexus3
mc cp -r /apache-ignite/work myminio/${MINIO_BUCKET}/ignite-data/
mc cp -r /apache-ignite/logs myminio/${MINIO_BUCKET}/ignite-logs/