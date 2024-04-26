import os
from packaging.metadata import parse_email
from pypi_simple import PyPISimple, tqdm_progress_factory
import urllib.request
import re
import pandas as pd
from tqdm import tqdm


# Returns list of all PyPI packages
def get_all_packages():
    contents = urllib.request.urlopen('https://pypi.org/simple/').read().decode('utf-8')
    pattern = re.compile(r'>([^<]+)</a>')
    package_list = [match[1] for match in re.finditer(pattern, contents)]
    # print(package_list)
    print(f'Total of {len(package_list):,} packages\n')
    return package_list


def get_newest_tar(page):
    tar_list = [pkg for pkg in page.packages if pkg.filename.endswith(".tar.gz")]
    if tar_list:
        return tar_list[-1]
    else:
        return None


def download(package):
    with PyPISimple() as client:
        try:
            page = client.get_project_page(package)
            # pkg = page.packages[-1]
            pkg = get_newest_tar(page)
            if pkg.filename in os.listdir("archive"):
                print(f"{pkg.filename} already downloaded")
                return
            workingdir = os.path.dirname(__file__)
            destination = os.path.join(workingdir, "archive", pkg.filename)
            client.download_package(
                pkg, path=destination, progress=tqdm_progress_factory(),
            )
        except:
            print(f"Couldn't find any package files for {package}")
            pass


def get_dependencies(package):
    with PyPISimple() as client:
        deps = []
        page = client.get_project_page(package)
        pkg = page.packages[-1]
        if pkg.has_metadata:
            src = client.get_package_metadata(pkg)
            md, _ = parse_email(src)
            deps = md.get("requires_dist")
        return deps


def create_table(package_list, download_count=False):
    with PyPISimple() as client:
        info = []
        for package in tqdm(package_list, desc="Updating Info Table"):
            page = client.get_project_page(package)
            # print(page)
            if page.packages:
                # pkg = page.packages[-1]
                # print(pkg)
                pkg = get_newest_tar(page)
                if pkg:
                    package = {"project": pkg.project, "version": pkg.version, "package_type": pkg.package_type}
                    if pkg.requires_python:
                        package["requires_python"] = pkg.requires_python
                    if pkg.has_metadata:
                        src = client.get_package_metadata(pkg)
                        md, _ = parse_email(src)
                        package["requires_dist"] = md.get("requires_dist")
                    info.append(package)
        df = pd.DataFrame(info)
        # df.to_pickle("info")
        df.to_csv("info.csv")


def get_most_downloaded(download_count=False):
    from urllib.request import urlopen
    import json
    url = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json"
    response = urlopen(url)
    data_json = json.loads(response.read())
    # most = [(pkg["project"], pkg["download_count"]) for pkg in data_json["rows"]]
    if download_count:
        most = [(pkg["project"], pkg["download_count"]) for pkg in data_json["rows"]]
    else:
        most = [pkg["project"] for pkg in data_json["rows"]]
    return most


if __name__ == '__main__':
    # download("pypi-simple")
    # print(get_dependencies("pandas"))
    # package_list = get_all_packages()
    # package_list = package_list[-200:]
    # print(packages[-5:])
    package_list = get_most_downloaded()
    package_list = package_list[:50]
    create_table(package_list)
    # print(get_most_downloaded())
