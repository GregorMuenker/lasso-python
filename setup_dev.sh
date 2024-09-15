pip install -r ./backend/crawl/requirements.txt
pip install -r ./backend/arena/requirements.txt
pip install GitPython
sh lassoindex_setup.sh
echo {} > backend/crawl/index.json
docker-compose -f docker-compose-dev.yaml up -d
# docker compose -f docker-compose-dev.yaml up -d
docker cp solr/data/lasso_python/conf/managed-schema.xml lasso_solr_quickstart:/var/solr/data/lasso_python/conf/managed-schema.xml
# Wait for the container to be ready
sleep 120
sh nexus/setup.sh