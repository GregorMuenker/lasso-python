docker run -d -v "./lassoindex:/var/solr/" -p 8983:8983 --name lasso_solr_quickstart solr solr-precreate lasso_quickstart

docker build -t backend ./backend
docker run -p 8000:8000 -e DOCKER=test -e SOLR_PATH=http://solr:8983/solr/ --link lasso_solr_quickstart:solr --name py-app backend
