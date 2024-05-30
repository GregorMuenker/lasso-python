import sys
import importlib

def load_and_use_function_from_folder(folder_path, module_name, function_name, *args, **kwargs):
    try:
        # Add the folder to the system path
        if folder_path not in sys.path:
            sys.path.insert(0, folder_path)

        # Dynamically load the module
        module = importlib.import_module(module_name)

        # Access the specific function from the module
        function = getattr(module, function_name)

        # Call the function with the provided arguments
        result = function(*args, **kwargs)

        return result
    except ModuleNotFoundError:
        return f"Module '{module_name}' not found in folder '{folder_path}'."
    except AttributeError:
        return f"Function '{function_name}' not found in module '{module_name}'."
    except Exception as e:
        return f"An error occurred: {e}"

# Example usage:
# Assuming you have a folder '/path/to/your/library' and a module 'mymodule' with a function 'myfunction' in it:
result = load_and_use_function_from_folder('./numpy-2.0.0rc1', 'numpy', 'exp', 3)
print(result)
