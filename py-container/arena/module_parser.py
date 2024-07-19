import ast

def get_type_annotation(annotation):
    if annotation is None:
        return "Any"
    if isinstance(annotation, ast.Name):
        return annotation.id
    if isinstance(annotation, ast.Attribute):
        return f"{annotation.value.id}.{annotation.attr}"
    if isinstance(annotation, ast.Subscript):
        value = get_type_annotation(annotation.value)
        if isinstance(annotation.slice, ast.Index):  # Compatibility for Python 3.8
            subscript = get_type_annotation(annotation.slice.value)
        else:  # For Python 3.9+
            subscript = get_type_annotation(annotation.slice)
        return f"{value}[{subscript}]"
    return "Any"

def parse_function(node, parentClass=None):
    from adaptation import FunctionSignature
    functionName = node.name
    if parentClass:
        functionName = f"{parentClass}.{functionName}"
    returnType = get_type_annotation(node.returns)
    parameterTypes = []

    # Index of the first parameter with a default value (parameters with values are always at the end of the signature)
    firstDefault = len(node.args.args) # set to one element behind the last index by default (out of range)
    firstDefault = len(node.args.args) - len(node.args.defaults)

    for arg in node.args.args:
        if arg.annotation:
            param_type = get_type_annotation(arg.annotation)
        else:
            param_type = "Any"
        parameterTypes.append(param_type)
    
    # remove first parameter (self) for class methods
    if parentClass:
        parameterTypes = parameterTypes[1:]
        firstDefault -= 1 # as self is not counted, the index of the first default parameter is reduced by 1
    
    return FunctionSignature(functionName, returnType, parameterTypes, parentClass, firstDefault)

def parse_class(node):
    className = node.name
    functions = []
    constructors = []
    for item in node.body:
        if isinstance(item, ast.FunctionDef):
            if item.name == '__init__' or item.name == '__new__':
                constructors.append(parse_function(item, parentClass=className))
            else:
                functions.append(parse_function(item, parentClass=className))
    return className, functions, constructors

def parse_code(code_string, module_name):
    from adaptation import ModuleUnderTest
    tree = ast.parse(code_string)
    functions = []
    classes = {}
    constructors = []
    
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            functions.append(parse_function(node))
        elif isinstance(node, ast.ClassDef):
            className, class_functions, class_constructors = parse_class(node)
            classes[className] = class_constructors
            functions.extend(class_functions)
            constructors.extend(class_constructors)
    
    module = ModuleUnderTest(module_name, functions)
    module.classes = classes
    module.constructors = constructors

    print(f"Module Name: {module.moduleName}")
    print(f"Classes: {module.classes}")
    for func in module.constructors:
        print(f"Constructor Name: {func.functionName}, Parent Class: {func.parentClass}, Parameters: {func.parameterTypes}, Return Type: {func.returnType}, First Default: {func.firstDefault}")
    for func in module.functions:
        print(f"Function Name: {func.functionName}, Parent Class: {func.parentClass}, Parameters: {func.parameterTypes}, Return Type: {func.returnType}, First Default: {func.firstDefault}")
    
    return module

# Example usage
if __name__ == "__main__":
    code_string = """
def multiply(a: int, b: int, c: int, d=1):
    return a * b * c

def divide(a: float, b: int):
    return a / b

class Test:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def __init__(self):
        pass

    def add(self, a: int, b: int, c=1):
        return self.x + self.y + a + b

    def subtract(self, a: int, b: int):
        return self.x + self.y - a - b

class Hello:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def __init__(self):
        pass

    def add(self, a: int, b: int):
        return self.x + self.y + a + b

    def subtract(self, a: int, b: int):
        return self.x + self.y - a - b
"""

    module = parse_code(code_string)
