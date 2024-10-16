import requests
import os

def upload_index(index):
    if os.environ.get('SOLR_PATH'):
        requests.post(f'{os.environ.get("SOLR_PATH")}{os.environ.get("SOLR_COLLECTION")}/update/json/docs', json=index)
    else:
        response = requests.post('http://localhost:8983/solr/lasso_python/update/json/docs', json=index)
        print(response.text)