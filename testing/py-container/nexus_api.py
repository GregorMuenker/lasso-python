import requests

NEXUS_URL = 'http://localhost:8081'
REPO_NAME = 'your-repo'
USERNAME = 'your-username'
PASSWORD = 'your-password'

def upload_artifact(file_path, artifact_path):
    url = f"{NEXUS_URL}/repository/{REPO_NAME}/{artifact_path}"
    with open(file_path, 'rb') as file:
        response = requests.put(url, data=file, auth=(USERNAME, PASSWORD))
    return response.status_code

def get_artifact(artifact_path):
    url = f"{NEXUS_URL}/repository/{REPO_NAME}/{artifact_path}"
    response = requests.get(url, auth=(USERNAME, PASSWORD))
    if response.status_code == 200:
        return response.content
    else:
        return None
