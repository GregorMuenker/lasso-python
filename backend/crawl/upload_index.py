import requests


def upload_index(index):
    requests.post('http://localhost:8983/solr/lasso_quickstart/update/json/docs', json=index)