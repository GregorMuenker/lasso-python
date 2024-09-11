#!/bin/bash

# Variables
NEXUS_URL="http://localhost:8081"
ADMIN_USER="admin"
OLD_PASSWORD=$(docker exec -it nexus cat /nexus-data/admin.password)
NEW_PASSWORD="your_new_password"
BLOB_STORE_NAME="my_blob_store"
REPO_NAME="my_repo"

# Change password
curl -u $ADMIN_USER:$OLD_PASSWORD -X PUT -H "Content-Type: application/json" \
    -d "{\"userId\":\"admin\",\"oldPassword\":\"$OLD_PASSWORD\",\"newPassword\":\"$NEW_PASSWORD\"}" \
    $NEXUS_URL/service/rest/v1/security/users/admin/change-password

# Create Blob Store
curl -u $ADMIN_USER:$NEW_PASSWORD -X POST -H "Content-Type: application/json" \
    -d "{\"name\":\"$BLOB_STORE_NAME\",\"type\":\"File\"}" \
    $NEXUS_URL/service/rest/v1/blobstores/file

# Create Repository
curl -u $ADMIN_USER:$NEW_PASSWORD -X POST -H "Content-Type: application/json" \
    -d "{\"name\":\"$REPO_NAME\",\"online\":true,\"storage\":{\"blobStoreName\":\"$BLOB_STORE_NAME\",\"strictContentTypeValidation\":true},\"cleanup\":{\"policyNames\":[\"string\"]},\"component\":{\"proprietaryComponents\":false},\"docker\":{\"v1Enabled\":false,\"forceBasicAuth\":true,\"httpPort\":8082}}" \
    $NEXUS_URL/service/rest/v1/repositories/docker/hosted