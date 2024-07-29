if [ ! -d "lassoindex" ]; then
    mkdir lassoindex
    echo "created lassoindex directory"
    sudo chown -R 8983:8983 lassoindex
    cp -r solr/data/lasso_python/conf/* lassoindex/data/lasso_python/conf/
    sudo chown -R 8983:8983 lassoindex/data/lasso_python/conf/
fi

docker run -d -v "$PWD/lassoindex:/var/solr" -p 8983:8983 --name lasso_solr_quickstart solr solr-precreate lasso_quickstart

docker build -t backend ./
docker run -p 8000:8000 -e DOCKER=test -e SOLR_PATH=http://solr:8983/solr/ --link lasso_solr_quickstart:solr --name py-app backend
