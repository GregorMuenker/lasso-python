# Nexus and LASSO
<sub><sup>_This guide is a modified version of the official nexus setup for lasso guide from the lasso repository by Marcus Kessel._</sup></sub>

This short guide demonstrates how to set up a new artifact repository as part of LASSO's executable corpus.

Important: Possible security risks are not taken into consideration, so do not expose your instances.

## Quickstart guide (docker)

This guide assumes that a working docker installation (user space level, see https://docs.docker.com/engine/install/linux-postinstall/) is present on the local machine.

Important: Possible security risks are not taken into consideration, so do not expose your instances.

For this guide, we use the official docker image of Sonatype's Nexus OSS (see https://hub.docker.com/r/sonatype/nexus3)

```bash
# start nexus in a container
docker run -d -p 8081:8081 --name nexus-lasso sonatype/nexus3

# NOTE: be patient (!), nexus takes some time to start

#Setup repository and password
sh ./setup.sh 

# get password for user 'admin'
# (you need to change in the dashboard after the first login)
#docker exec -it nexus bash
#cat sonatype-work/nexus3/admin.password
# terminate bash - ctrl-d
```

Tested with _Sonatype Nexus OSS 3.71.0-06_.

### Nexus configuration

Open your web browser and go to http://localhost:8081/ and login as 'admin' using the aforementioned password.

After a successful login, Nexus starts a quick wizard. Make sure to enable anonymous access.

### Deployment of subject artifacts within LASSO

This requires the presence of a repository in which artifacts can be deployed.

1. Log in to your Nexus Repository manager using your admin account (e.g., http://localhost:8081/)
2. Go to http://localhost:8081/#admin/repository/blobstores
3. Click `Create Blob Store`
4. Select Type `File` and assign a uniquq identifier (e.g. `lasso-blob`)
5. Go to http://localhost:8081/#admin/repository/repositories
6. Click `Create repository`
7. Choose repository type `raw (hosted)`
8. Assign a unique identifier (e.g. `lasso-deploy`)
9. Select the blob store created before
10. Set deployment policy to `Allow redeploy`
11. Go to http://localhost:8081/#admin/repository/repositories:maven-public and add your newly created repository to _Members_, so we can retrieve deloyed artifacts via the _maven-public_ repository

Change the deployment url, user and password in [corpus.json](corpus.json) (requires new LASSO service instance!)

```json
  "artifactRepository": {
    "id": "lasso_quickstart_nexus",
    "name": "Quickstart nexus",
    "url": "http://localhost:8081",
    "deploymentUrl": "http://localhost:8081/repository/lasso-deploy",
    "user": "XXX",
    "pass": "XXX",
    "description": "quickstart repository of LASSO"
  }
```

You have to restart LASSO with the updated `corpus.json` configuration file.

docker cp solr/data/lasso_python/conf/managed-schema.xml lasso_solr_quick:/var/solr/data/lasso_python/conf/managed-schema.xml