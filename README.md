# LASSO-Python

a python extension for the LASSO Plattform

## Automatic Setup

### Execute ```sh ./start.sh```

## Maunal Setup

### Solr

create a directory to store the server/solr directory <br>
```mkdir lassoindex```

make sure its host owner matches the container's solr user <br>
```sudo chown -R 8983:8983 lassoindex```<br>
sudo rights necessary

creates and runs a solr container on http://localhost:8983, creates a new index called 'lasso_quickstart' <br>
```docker run -d -v "$PWD/lassoindex:/var/solr" -p 8983:8983 --name lasso_solr_quickstart solr solr-precreate lasso_quickstart```

### Build Docker container

```docker build -t backend .```

### Run the Container

Either with: <br>
```docker run -p 8000:8000 -e DOCKER=test -e SOLR_PATH=http://solr:8983/solr/ --link lasso_solr_quickstart:solr --name py-app app```

Or with:
```docker-compose up -d```




