import os


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
    # Replace 'your_directory_path' with the actual path to your directory
    remove_except_python('packages')
