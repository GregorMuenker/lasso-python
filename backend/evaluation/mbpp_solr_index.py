import json
import os

import requests
from mbpp_loader import load_mbpp_data


def index_data_in_solr(data):
    solr_url = (
        os.getenv("SOLR_URL", "http://localhost:8983/solr/") + "mbpp/update?commit=true"
    )
    headers = {"Content-Type": "application/json"}

    response = requests.post(solr_url, headers=headers, data=json.dumps(data))
    print(response.status_code)


if __name__ == "__main__":
    mbpp_data = load_mbpp_data("mbpp.jsonl")
    index_data_in_solr(mbpp_data)
    mbpp_data = load_mbpp_data("mbpp.jsonl")
    index_data_in_solr(mbpp_data)
