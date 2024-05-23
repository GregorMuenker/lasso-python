import tarfile
import os


def unpack_all():
    workingdir = os.path.dirname(__file__)
    archivedir = os.path.join(workingdir, "archive")
    files = [file for file in os.listdir(archivedir) if file.endswith(".tar.gz") and file[:-7] not in os.listdir("packages")]
    # print(files)
    for file in files:
        filepath = os.path.join(archivedir, file)
        destination = os.path.join(workingdir, "packages")
        unpack_targz(filepath, destination)


def unpack_targz(archive_file, destination_path):
    with tarfile.open(archive_file, "r:gz") as tar:
        tar.extractall(destination_path)


# TODO: Even Useful?
def remove_except_python(directory):
    for root, dirs, files in os.walk(directory):
        for item in list(dirs) + list(files):  # Create a copy of lists to avoid modification errors
            filepath = os.path.join(root, item)
            if filepath.endswith(".py"):
                pass
            elif os.path.isdir(filepath):
                remove_except_python(filepath)
                if not os.listdir(filepath):  # Check if the processed directory is empty
                    print(f"Removing empty directory: {filepath}")
                    os.rmdir(filepath)
            elif os.path.isfile(filepath):
                # Remove non-directory, non-Python files
                print(f"Removing: {filepath}")
                os.remove(filepath)


if __name__ == '__main__':
    unpack_all()
    # remove_except_python('packages')
