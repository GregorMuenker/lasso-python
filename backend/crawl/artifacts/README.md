# run.py

`run.py` is a Python script that dynamically moves and runs packages along with their dependencies. The script handles the relocation of packages to a runtime directory, executes specified functions, and then cleans up the runtime environment by removing the packages.

## Features

- Move specified package and its dependencies to a runtime directory.
- Execute a function from the specified package.
- Clean up the runtime environment after execution.

## Requirements

- Python 3.6+
- Packages should be pre-installed in the `../../crawl/installed` directory.

## Setup

1. Ensure Python 3.6 or higher is installed on your system.
2. Ensure the `../../crawl/installed` directory contains the required packages and `index.json`.

## Usage

1. Clone or download this repository.
2. Navigate to the `py-container/arena` directory.
3. Run the script with the desired package, version, module path, function, and parameters.

## Functions

### `move(package, version)`
Moves the specified package and its dependencies to the runtime directory.

**Args:**
- `package (string)`: Package name.
- `version (string)`: Package version.

**Returns:**
- `list of strings`: List of moved folders.

### `remove(folders)`
Removes the specified folders from the runtime directory.

**Args:**
- `folders (list of strings)`: List of folders to remove.

### `run(package, version, path, function, parameters)`
Moves the package, runs the specified function, and cleans up the runtime directory.

**Args:**
- `package (string)`: Package name.
- `version (string)`: Package version.
- `path (string)`: Module path.
- `function (string)`: Function name.
- `parameters (tuple)`: Function parameters.

**Returns:**
- `any`: Result of the function execution.

## Example

The following example demonstrates how to use the `run` function:

```python
if __name__ == "__main__":
    package = "urllib3"
    version = "2.2.2"
    path = "urllib3.util.util"
    function = "to_bytes"

    # Prepare arguments for the function
    x = "café"
    encoding = "ascii"
    errors = "ignore"
    args = (x, encoding, errors)

    result = run(package, version, path, function, args)
    print(result)
