"""constants.py"""

import os
from dotenv import load_dotenv

import git
repo = git.Repo(search_parent_directories=True)
REPOSITORY = repo.working_tree_dir
INSTALLED = f"{REPOSITORY}/backend/crawl/installed"
INDEX = f"{REPOSITORY}/backend/crawl/index.json"
RUNTIME = f"{REPOSITORY}/backend/arena/runtime"
CORPUS = f"{REPOSITORY}/nexus/corpus.json"
TYPE_INFERENCING_TEMP = f"{REPOSITORY}/backend/crawl/temp"

load_dotenv()

# ANSI escape codes for colored output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

STANDARD_CONSTRUCTOR_VALUES = {
    "str": "",
    "int": 1,
    "float": 1.0,
    "complex": 1 + 1j,
    "list": [],
    "tuple": (),
    "range": range(1),
    "dict": {},
    "set": set(),
    "frozenset": frozenset(),
    "bool": True,
    "bytes": b"",
    "bytearray": bytearray(b""),
    "memoryview": memoryview(b""),
    "None": None,
}

TYPE_MAPPING = {
    "str": str,
    "int": int,
    "float": float,
    "complex": complex,
    "list": list,
    "tuple": tuple,
    "range": range,
    "dict": dict,
    "set": set,
    "frozenset": frozenset,
    "bool": bool,
    "bytes": bytes,
    "bytearray": bytearray,
    "memoryview": memoryview,
}

POSSIBLE_CONVERSIONS = {
    "bool": ["bool", "str", "int", "float", "complex", "range", "bytes", "bytearray"],
    "bytearray": [
        "bytearray",
        "str",
        "list",
        "tuple",
        "set",
        "frozenset",
        "bool",
        "bytes",
        "memoryview",
    ],
    "bytes": [
        "bytes",
        "str",
        "list",
        "tuple",
        "set",
        "frozenset",
        "bool",
        "bytearray",
        "memoryview",
    ],
    "complex": ["complex", "str", "bool"],
    "dict": ["dict", "str", "list", "tuple", "set", "frozenset", "bool"],
    "float": ["float", "str", "int", "complex", "bool"],
    "frozenset": [
        "frozenset",
        "str",
        "list",
        "tuple",
        "set",
        "bool",
        "bytes",
        "bytearray",
    ],
    "int": ["int", "str", "float", "complex", "range", "bool", "bytes", "bytearray"],
    "list": [
        "list",
        "str",
        "tuple",
        "set",
        "frozenset",
        "bool",
        "bytes",
        "bytearray",
    ],
    "memoryview": [
        "memoryview",
        "str",
        "bytes",
        "bytearray",
        "bool",
        "list",
        "tuple",
        "set",
        "frozenset",
    ],
    "range": ["range", "str", "bytes", "bytearray", "bool", "list", "tuple", "set", "frozenset"],
    "set": [
        "set",
        "str",
        "list",
        "tuple",
        "frozenset",
        "bool",
        "bytes",
        "bytearray",
    ],
    "str": ["str", "list", "tuple", "set", "frozenset", "bool"],
    "tuple": [
        "tuple",
        "str",
        "list",
        "set",
        "frozenset",
        "bool",
        "bytes",
        "bytearray",
    ],
    "None": ["None", "str", "bool", "list", "tuple", "set", "frozenset"],
}

LIST_LIKE_TYPES = [list, tuple, set, frozenset]