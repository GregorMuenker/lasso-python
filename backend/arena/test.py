import importlib
import sys

sys.path.insert(0, "runtime")

if __name__ == "__main__":
    module = importlib.import_module("testpackage.test")
    function = "something"
    func = getattr(module, function)
    parameters = (3)
    result = func(parameters)
    print(result)