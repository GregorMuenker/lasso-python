import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-t", f"installed/{package}"])

if __name__ == "__main__":
    install("pandas")