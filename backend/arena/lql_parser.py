import re

from adaptation import InterfaceSpecification, MethodSignature


def parse_method_signature(signature):
    """
    (\w+): Match and capture one or more word characters (the method name).
    \(: Match the literal opening parenthesis (.
    ([^)]*): Match and capture zero or more characters that are not closing parentheses ) (the parameter list).
    \): Match the literal closing parenthesis ).
    (->(\w+|\w+\[\]))?: Optionally match the literal arrow -> followed by either a simple type (one or more word characters) or an array type (one or more word characters followed by []) as the return type.
    """
    pattern = re.compile(r"(\w+)\(([^)]*)\)(?:->(\w+|\w+\[\]))?")
    match = pattern.match(signature.strip())
    if not match:
        return None

    methodName, params, returnType = match.groups()
    parameterTypes = [param.strip() for param in params.split(",")] if params else []
    returnType = returnType if returnType else None
    return MethodSignature(methodName, returnType, parameterTypes)


def parse_interface_spec(spec):
    """
    (\w+): Match and capture one or more word characters (the class/interface name).
    \s*: Match zero or more whitespace characters.
    {: Match the literal opening brace {.
    ([^}]*): Match and capture zero or more characters that are not closing braces } (the body of the interface specification).
    }: Match the literal closing brace }.
    """
    pattern = re.compile(r"(\w+)\s*{([^}]*)}")
    match = pattern.match(spec.strip())
    if not match:
        return None

    className, body = match.groups()
    method_signatures = [
        parse_method_signature(sig.strip()) for sig in body.split("\n") if sig.strip()
    ]
    constructors = [sig for sig in method_signatures if sig.methodName == className]
    methods = [sig for sig in method_signatures if sig.methodName != className]

    return InterfaceSpecification(className, constructors, methods)


def parse_multiple_interface_specs(notation):
    """
    This method can parse multiple interface specifications that are separated by one blank line in between.
    """
    specs = notation.strip().split("\n\n")
    return [parse_interface_spec(spec) for spec in specs]


if __name__ == "__main__":
    spec = """
    Stack {
        Stack()
        push(Object)->Object
        pop(int,float)
    }
    """

    interfaceSpecification = parse_interface_spec(spec)
    print(interfaceSpecification)
