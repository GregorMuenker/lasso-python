import requests
from requests.auth import HTTPBasicAuth
import sys
import os
import tarfile
import io
import re
import json

import git
repo = git.Repo(search_parent_directories=True)
sys.path.insert(0, repo.working_tree_dir)

NEXUS_HOST="http://localhost:8081"
from dotenv import load_dotenv
load_dotenv()
if os.getenv("RUNTIME_ENVIRONMENT") == "docker":
    INSTALLED = os.getenv("INSTALLED")
    RUNTIME = os.getenv("RUNTIME")
    INDEX = os.getenv("INDEX")
    CORPUS = os.getenv("CORPUS")
    NEXUS_HOST = os.getenv("NEXUS_HOST")
else:
    from backend.constants import INSTALLED, RUNTIME, INDEX, CORPUS
    
class Package:
    def __init__(self, name, version):
        self.name = name
        self.version = version
        self.dir = f"{name}-{version}"
        self.local_dir_path = f'{INSTALLED}/{self.dir}'
        self.artifact_path = f'{self.name}/{self.version}/{self.dir}.tar.gz'

    def compress(self):
        """Compresses package directory to tar.gz file.
        """
        filename = f"{self.dir}.tar.gz"
        self.local_file_path = f'{INSTALLED}/{filename}'
        with tarfile.open(self.local_file_path, "w:gz") as tar:
            tar.add(self.local_dir_path,
                    arcname=os.path.basename(self.local_dir_path))


class Nexus:
    def __new__(cls, nexus_host=NEXUS_HOST):
        with open(CORPUS, 'r') as file:
            corpus = json.load(file)
        if cls.check_status(nexus_host):   #corpus["artifactRepository"]["url"]):
            return super(Nexus, cls).__new__(cls)
        else:
            print(f"Cannot reach Nexus server at {nexus_host}")
            return None

    def __init__(self, nexus_host=NEXUS_HOST):
        # Configuration
        with open(CORPUS, 'r') as file:
            corpus = json.load(file)["artifactRepository"]
        self.nexus_host = corpus["url"]
        self.repository = corpus["repoName"]
        self.nexus_url = corpus["deploymentUrl"]
        self.username = corpus["user"]
        self.password = corpus["pass"]

    @staticmethod
    def check_status(nexus_host):
        """Checks if Nexus service is reachable.

        Returns:
            boolean: Depending on whether or not Nexus can be reached.
        """
        url = f"{nexus_host}/service/rest/v1/status"
        #try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Nexus is up and running!")
            return True
        else:
            print(f"Nexus returned status code {response.status_code}")
            return False
        #except requests.ConnectionError:
        print("Failed to connect to Nexus. The server might be down.")
        return False
    
    def upload(self, package: Package):
        """Uploads a compressed Package file to the Nexus Repository.

        Args:
            package (Package): Package object of package to be uploaded.
        """
        # Build the upload URL
        upload_url = f'{self.nexus_url}/{package.artifact_path}'

        # Open the file in binary mode
        with open(package.local_file_path, 'rb') as file_data:
            # Perform the upload
            response = requests.put(
                upload_url, data=file_data, auth=HTTPBasicAuth(self.username, self.password))

            # Check the response
            if response.status_code == 201:
                print(
                    f'Successfully uploaded {package.local_file_path} to {upload_url}')
                # Deleting compressed file.
                os.remove(package.local_file_path)
                package.local_file_path = None
                return True
            else:
                print(
                    f'Failed to upload {package.local_file_path}. HTTP Status Code: {response.status_code}')
                # print('Response:', response.text)
                return False

    def download(self, package: Package, runtime=True):
        """Downloads and extracts package file to Runtime folder.

        Args:
            package (Package): Package object of package to be downloaded.
            runtime: Identifies, whether the package download is for the runtime or for splitting. Default: True
        """
        print(f"Downloading {package.name} {package.version}")
        # Download the file
        response = requests.get(
            f"{self.nexus_url}/{package.artifact_path}", auth=HTTPBasicAuth(self.username, self.password))

        if response.status_code == 200:
            # Create a BytesIO object to handle the downloaded content in memory
            file_like_object = io.BytesIO(response.content)
            
            # Open the tar.gz file directly from the BytesIO object
            with tarfile.open(fileobj=file_like_object, mode='r:gz') as tar:
                # Get the top-level directory name (common prefix)
                top_level_dir = os.path.commonprefix([member.name for member in tar.getmembers()]).rstrip('/')
                
                # Iterate over each member in the tar file
                for member in tar.getmembers():
                    # Skip the top-level directory itself
                    if member.name == top_level_dir:
                        continue
                    # Create the relative path by removing the top-level directory
                    member.name = os.path.relpath(member.name, top_level_dir)
                    if runtime:
                        tar.extract(member, path=RUNTIME)
                    else:
                        tar.extract(member, path=os.path.join(INSTALLED, f"{package.name}-{package.version}"))
            
            with open(INDEX, 'r') as file:
                index = json.load(file)
            dependencies = index[f"{package.name}:{package.version}"]
            for dep_name, dep_dict in dependencies.items():
                dep_version = dep_dict["version"]
                if dep_version:
                    pkg = Package(dep_name, dep_version)
                    self.download(pkg)
                else:
                    # TODO: What if dependency is missing. Handle at the start?
                    pass

        else:
            print(
                f'Failed to download {package.name} {package.version}. HTTP Status Code: {response.status_code}')
            # print('Response:', response.text)

    def get_versions(self, package):
        """Fetches package versions from Nexus.

        Args:
            package (str): Package name.

        Returns:
            versions (list of str): List of version numbers.
        """
        versions = []
        continuation_token = None  # Used for pagination

        while True:
            # Construct the request URL with the continuation token if available
            url = f'{self.nexus_host}/service/rest/v1/components?repository={self.repository}'
            if continuation_token:
                url += f'&continuationToken={continuation_token}'

            # Make the GET request to list components
            response = requests.get(url, auth=HTTPBasicAuth(self.username, self.password))

            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()
                components = [item['group'] for item in response.json()['items']]
                matches = [re.search(r'\/([^\/]+)\/([^\/]+)$', item) for item in components]
                versions.extend([match.group(2) for match in matches if match.group(1) == package])

                # Check if there's a continuation token for the next page
                continuation_token = data.get('continuationToken')
                if not continuation_token:
                    break  # No more pages, exit the loop

            else:
                print(f"Failed to retrieve components. Status code: {response.status_code}")
                break

        return versions

if __name__ == "__main__":
    nexus = Nexus()
    package = Package("numpy", "2.0.2")
    package.compress()
    nexus.upload(package)
    nexus.download(package)
    # nexus.get_versions(package)
