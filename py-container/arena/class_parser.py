import ast

def parse_class(code_string):
    from adaptation import ClassUnderTest, MethodSignature
    class NodeVisitor(ast.NodeVisitor):
        def __init__(self):
            self.classes = []

        def visit_ClassDef(self, node):
            className = node.name
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_name = item.name
                    return_type = None
                    param_types = []
                    if item.returns:
                        return_type = ast.unparse(item.returns)
                    for arg in item.args.args:
                        # Extracting parameter type if annotated, else assume 'Any'
                        param_type = ast.unparse(arg.annotation) if arg.annotation else 'Any'
                        param_types.append(param_type)
                    methods.append(MethodSignature(method_name, return_type, param_types))
            self.classes.append(ClassUnderTest(className, code_string, methods))

    # Parsing the code string using AST
    tree = ast.parse(code_string)
    visitor = NodeVisitor()
    visitor.visit(tree)
    
    # Assuming there is at least one class in the code string
    return visitor.classes[0] if visitor.classes else None

if (__name__ == '__main__'):
    code = """
class Example:
    def method1(self, a: int) -> str:
        return str(a)
    def method2(self, b: str, c: bool) -> int:
        return int(b)
"""
    parsed_class = parse_class(code)
    print(f"Class Name: {parsed_class.className}")
    for m in parsed_class.methods:
        print(f"Method Name: {m.methodName}, Return Type: {m.returnType}, Parameter Types: {m.parameterTypes}")