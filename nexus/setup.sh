#!/bin/bash

# Variables
NEXUS_URL="http://localhost:8081"
ADMIN_USER="admin"
NEW_PASSWORD="9Fa4tLiZKnRJnUm"
BLOB_STORE_NAME="pypi-raw"
REPO_NAME="pypi-raw"
CONTAINER_NAME="lasso-nexus"

# Check if the container is running
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    # Get the current password
    OLD_PASSWORD=$(docker exec -it $CONTAINER_NAME cat /nexus-data/admin.password)

    echo "Changing Nexus password..."

    # Change password
    curl -u $ADMIN_USER:"$OLD_PASSWORD" -X PUT -H "Content-Type: text/plain" -d "$NEW_PASSWORD" \
        $NEXUS_URL/service/rest/v1/security/users/admin/change-password

    # Create Blob Store
    curl -u $ADMIN_USER:"$NEW_PASSWORD" -X POST -H "Content-Type: application/json" \
        -d "{\"softQuota\": {},\"path\": \"/nexus-data/blobs/$BLOB_STORE_NAME\",\"name\": \"$BLOB_STORE_NAME\"}" \
        $NEXUS_URL/service/rest/v1/blobstores/file

    # Create Repository
    curl -u $ADMIN_USER:$NEW_PASSWORD -X POST -H "Content-Type: application/json" \
        -d "{\"name\":\"$REPO_NAME\",\"online\":true,\"storage\":{\"blobStoreName\":\"$BLOB_STORE_NAME\",\"strictContentTypeValidation\":true, \"writePolicy\": \"allow_once\"},\"cleanup\":{\"policyNames\":[\"string\"]},\"component\":{\"proprietaryComponents\":true},\"raw\":{\"contentDisposition\":\"ATTACHMENT\"}}" \
        $NEXUS_URL/service/rest/v1/repositories/raw/hosted


    # Command to execute inside the container
    #COMMAND="echo 'nexus.baseUrl=http://$CONTAINER_NAME:8081' >> /nexus-data/etc/nexus.properties"
    #echo "Modifying Nexus configuration..."
    #docker exec -it $CONTAINER_NAME /bin/bash -c "$COMMAND"
    #echo "Restarting Nexus container..."
    #docker restart $CONTAINER_NAME
    #echo "Nexus configuration updated and container restarted."
else
    echo "Nexus container is not running. Please start the container first."
fi