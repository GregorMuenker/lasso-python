docker build -t app ./py-container
docker run -p 8000:8000 -e DOCKER=test -e SOLR_PATH=http://solr:8983/solr/ --link lasso_solr_quickstart:solr --name py-app app
