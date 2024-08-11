# LASSO-Python

a python extension for the LASSO Plattform

## Docs
[Link to Docs](./docs/structure.md)

## Automatic Setup

### Execute ```docker-compose up -d```
lassoindex folder has to be set up already ```lassoindex_setup.sh```
also possible startup with ```sh ./start.sh```

## Maunal Setup

### Solr

create a directory to store the server/solr directory <br>
```mkdir lassoindex```

make sure its host owner matches the container's solr user <br>
```sudo chown -R 8983:8983 lassoindex```<br>
sudo rights necessary

creates and runs a solr container on http://localhost:8983, creates a new index called 'lasso_quickstart' <br>
```docker run -d -v "./lassoindex:/var/solr" -p 8983:8983 --name lasso_solr_quickstart solr solr-precreate lasso_quickstart```

copy LASSO document schema to your index
```cp -r solr/data/lasso_python/conf/* lassoindex/data/lasso_python/conf/```

make sure its host owner matches the container's solr user
```sudo chown -R 8983:8983 lassoindex/data/lasso_python/conf/```

### Build Docker container

```docker build -t backend .```

### Run the Container

Either with: <br>
```docker run -p 8000:8000 -e DOCKER=test -e SOLR_PATH=http://solr:8983/solr/ --link lasso_solr_quickstart:solr --name py-app app```

Or with:
```docker-compose up -d```




```sh ./start.sh```