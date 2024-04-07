import os
from packaging.metadata import parse_email
from pypi_simple import PyPISimple, tqdm_progress_factory
import urllib.request
import re


# Returns list of all PyPI packages
def get_all_packages():
    contents = urllib.request.urlopen('https://pypi.org/simple/').read().decode('utf-8')
    pattern = re.compile(r'>([^<]+)</a>')
    package_list = [match[1] for match in re.finditer(pattern, contents)]
    print(f'Total of {len(package_list):,} packages\n')
    return package_list


def download(package):
    with PyPISimple() as client:
        try:
            page = client.get_project_page(package)
            pkg = page.packages[-1]
            workingdir = os.path.dirname(__file__)
            destination = os.path.join(workingdir, "archive", pkg.filename)
            client.download_package(
                pkg, path=destination, progress=tqdm_progress_factory(),
            )
        except:
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


if __name__ == '__main__':
    # download("pypi-simple")
    # print(get_dependencies("scikit-learn"))
    packages = get_all_packages()
    print(packages[-5:])
