import os
from pypi_simple import PyPISimple, tqdm_progress_factory


def download(package):
    with PyPISimple() as client:
        page = client.get_project_page(package)
        pkg = page.packages[-1]
        workingdir = os.path.dirname(__file__)
        destination = os.path.join(workingdir, "archive", pkg.filename)
        client.download_package(
            pkg, path=destination, progress=tqdm_progress_factory(),
        )


if __name__ == '__main__':
    download("pypi-simple")
