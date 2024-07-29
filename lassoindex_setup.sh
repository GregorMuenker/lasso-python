mkdir lassoindex
echo "created lassoindex directory"
sudo chown -R 8983:8983 ./lassoindex
sudo chmod -R 777 ./lassoindex
sudo mkdir lassoindex/data
sudo mkdir lassoindex/data/lasso_python
sudo mkdir lassoindex/data/lasso_python/conf
sudo cp -r solr/data/lasso_python/conf/* lassoindex/data/lasso_python/conf/
sudo chown -R 8983:8983 ./lassoindex/data/lasso_python/conf/