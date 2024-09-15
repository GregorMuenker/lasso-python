sh lassoindex_setup.sh
echo {} > backend/crawl/index.json
docker-compose -f docker-compose.yaml up -d
docker cp solr/data/lasso_python/conf/managed-schema.xml lasso_solr_quickstart:/var/solr/data/lasso_python/conf/managed-schema.xml
# Wait for the container to be ready
sleep 60
sh nexus/setup.sh