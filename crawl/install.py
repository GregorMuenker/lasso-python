import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-t", "installed"])

if __name__ == "__main__":
    install("pandas")