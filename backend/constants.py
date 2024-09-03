"""constants.py"""

import os
from dotenv import load_dotenv
import git

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

repo = git.Repo(search_parent_directories=True)
REPOSITORY = repo.working_tree_dir
INSTALLED = f"{REPOSITORY}/backend/crawl/installed"
INDEX = f"{REPOSITORY}/backend/crawl/index.json"
RUNTIME = f"{REPOSITORY}/backend/arena/runtime"