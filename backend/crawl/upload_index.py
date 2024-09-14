import requests
import os

def upload_index(index):
    if os.environ.get('SOLR_PATH'):
        requests.post(f'{os.environ.get("SOLR_PATH")}/lasso_python/update/json/docs', json=index)
    else:
        requests.post('http://localhost:8983/solr/lasso_python/update/json/docs', json=index)