import os

import requests


def query_solr_for_methods(method_name):
    solr_url = (
        os.getenv("SOLR_URL", "http://localhost:8983/solr/")
        + f"mbpp/select?q=method:{method_name}"
    )
    response = requests.get(solr_url)
    return response.json()


if __name__ == "__main__":
    result = query_solr_for_methods("add_numbers")
    print(result)
    result = query_solr_for_methods("add_numbers")
    print(result)
