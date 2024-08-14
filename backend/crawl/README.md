# install.py

`install.py` is a Python script designed to install Python packages along with their dependencies. The script retrieves package information from PyPI (Python Package Index) and installs the specified packages into a local directory, ensuring all dependencies are satisfied.

## Features

- Retrieve all package names from PyPI.
- Retrieve the 8000 most downloaded packages from PyPI.
- Install packages and their dependencies locally.
- Check for existing local versions before installing new ones.
- Generate a JSON index of installed packages and their dependencies.

## Requirements

- Python 3.6+

## Setup

1. Ensure Python 3.6 or higher is installed on your system.

## Usage

1. Clone or download this repository.
2. Navigate to the `crawl` directory.
3. Run:
    ```bash
    python3 install.py
    ```

## Functions

### `get_all_packages()`
Retrieves all package names from PyPI.

**Returns:**
- `list of strings`: List of package names.

### `get_most_downloaded(download_count=False)`
Retrieves the 8000 most downloaded package names from PyPI.

**Args:**
- `download_count (bool, optional)`: If `True`, includes download counts.

**Returns:**
- `list of strings`: List of package names.

## Class

### `installHandler`
Handles the installation of packages and their dependencies.

**Methods:**
- `__init__()`: Initializes the handler and loads the index.
- `install(package)`: Installs a package and its dependencies.
- `dump_index()`: Dumps the index to a JSON file.

## Example

The following code installs the 10 most downloaded packages:

```python
if __name__ == "__main__":
    packages = get_most_downloaded()
    installHandler = installHandler()
    for package in packages[:10]:
        installHandler.install(package)
    installHandler.dump_index()
