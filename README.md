# LASSO-Python

a python extension for the LASSO Plattform

## Docs
[Link to Docs](./docs/structure.md)

## Automatic Setup

### Execute ```sh ./setup.sh```
watch out for ignite to start correctly
and that the nexus container has fully started when the nexus password will be changed

## Manual Setup

### Solr persistent volume (optional)
automatic script: ```lassoindex_setup.sh````

<br><br>
Otherwise manual:
<br>

create a directory to store the server/solr directory <br>
```mkdir lassoindex```

make sure its host owner matches the container's solr user <br>
```sudo chown -R 8983:8983 lassoindex```<br>
sudo rights necessary

creates and runs a solr container on http://localhost:8983, creates a new index called 'lasso_quickstart' <br>
```docker run -d -v "./lassoindex:/var/solr" -p 8983:8983 --name lasso_solr_quickstart solr solr-precreate lasso_python```

copy LASSO document schema to your index
```cp -r solr/data/lasso_python/conf/* lassoindex/data/lasso_python/conf/```

make sure its host owner matches the container's solr user
```sudo chown -R 8983:8983 lassoindex/data/lasso_python/conf/```

### Build and Run Docker containers

```docker-compose up -d```

### Add managed Schema manually
```docker cp solr/data/lasso_python/conf/managed-schema.xml lasso_solr_quick:/var/solr/data/lasso_python/conf/managed-schema.xml```

### Set up Nexus
then when nexus is ready:
```sh ./nexus/setup.sh```

## Calls to the containers
call to curl numpy package:
```curl -X POST localhost:8010/crawl/numpy==1.26.4```

call to execute sequence sheet arena_development on the lql query:
```curl -X POST -H "Content-Type: text/plain" -d $'Calculator {\n Calculator(int)->None\n addme(int)->int\n subme(int)->int\n }' localhost:8020/arena/arena_development.xlsx```

## Frontend

The frontend with the pages and functions for the arena and crawl part can then be found at the address: http://localhost:8501/

## Limitations
- No other version than 1.26.4 of numpy can be crawled, analysed and used in the arena due to depedencies in the project. 