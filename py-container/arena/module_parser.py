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

    for arg in node.args.args:
        if arg.annotation:
            param_type = get_type_annotation(arg.annotation)
        else:
            param_type = "Any"
        parameterTypes.append(param_type)
    
    # remove first parameter (self) for class methods
    if parentClass:
        parameterTypes = parameterTypes[1:]
    
    return FunctionSignature(functionName, returnType, parameterTypes, parentClass)

def parse_class(node):
    className = node.name
    functions = []
    constructors = []
    for item in node.body:
        if isinstance(item, ast.FunctionDef):
            if item.name == '__init__':
                constructors.append(parse_function(item, parentClass=className))
            else:
                functions.append(parse_function(item, parentClass=className))
    return className, functions, constructors

def parse_code(code_string):
    from adaptation import ModuleUnderTest
    tree = ast.parse(code_string)
    moduleName = 'parsed_module'
    functions = []
    classes = []
    constructors = []
    
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            functions.append(parse_function(node))
        elif isinstance(node, ast.ClassDef):
            className, class_functions, class_constructors = parse_class(node)
            classes.append(className)
            functions.extend(class_functions)
            constructors.extend(class_constructors)
    
    module = ModuleUnderTest(moduleName, code_string, functions)
    module.classes = classes
    module.constructors = constructors

    print(f"Module Name: {module.moduleName}")
    print(f"Classes: {module.classes}")
    for func in module.constructors:
        print(f"Constructor Name: {func.functionName}, Parent Class: {func.parentClass}, Parameters: {func.parameterTypes}, Return Type: {func.returnType}")
    for func in module.functions:
        print(f"Function Name: {func.functionName}, Parent Class: {func.parentClass}, Parameters: {func.parameterTypes}, Return Type: {func.returnType}")
    
    return module

# Example usage
if __name__ == "__main__":
    code_string = """
from typing import List

class MyClass:
    def __init__(self, param1: int):
        self.param1 = param1
    
    def my_method(self, param2: List[str]) -> str:
        return param2[0]

def standalone_function(param3) -> int:
    return param3
"""

    module = parse_code(code_string)
