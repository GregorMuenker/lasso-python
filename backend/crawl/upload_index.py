import requests
import os

def upload_index(index):
    if os.environ.get('SOLR_PATH'):
        requests.post(f'{os.environ.get("SOLR_PATH")}/update/json/docs', json=index)
    else:
        requests.post('http://localhost:8983/solr/lasso_quickstart/update/json/docs', json=index)