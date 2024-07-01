import subprocess
import sys
import os
import shutil
from io import StringIO
from tokenize import generate_tokens


def get_info(folder):
    path = f"installed/{folder}/METADATA"
    file = open(path, "r", encoding="utf-8")
    dependencies = []
    for line in file:
        if line.startswith("Name: "):
            name = line.split(":")[1].strip()
        if line.startswith("Version: "):
            version = line.split(":")[1].strip()
        if line.startswith("Requires-Dist: "):
            dependencies.append(line.split(":")[1].strip())
    return {
        "name": name,
        "version": version,
        "dependencies": dependencies
    }


def tokenize(string):
    STRING = 1
    return list(
        token[STRING]
        for token in generate_tokens(StringIO(string).readline)
        if token[STRING]
    )


def install(package):
    path = "installed/tmp"
    name = tokenize(package)[0]
    print(name)
    subprocess.check_call([sys.executable, "-m", "pip",
                          "install", package, "-q", "-t", path])
    version = [get_info(f"tmp/{item}")["version"] for item in os.listdir(
        path) if item.lower().startswith(name) and item.endswith(".dist-info")][0]
    destination = f"installed/{name}-{version}"
    shutil.move(path, destination)


if __name__ == "__main__":
    install("six")
    # dependency = "pysocks!=1.5.7,<2.0,>=1.5.6"
    # install(dependency)
