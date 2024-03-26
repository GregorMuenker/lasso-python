import tarfile
import os


def unpack_all():
    workingdir = os.path.dirname(__file__)
    archivedir = os.path.join(workingdir, "archive")
    files = os.listdir(archivedir)
    for file in files:
        filepath = os.path.join(archivedir, file)
        destination = os.path.join(workingdir, "packages")
        unpack_targz(filepath, destination)


def unpack_targz(archive_file, destination_path):
    with tarfile.open(archive_file, "r:gz") as tar:
        tar.extractall(destination_path)


if __name__ == '__main__':
    unpack_all()
