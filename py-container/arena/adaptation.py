from test_data import CALCULATOR_CLASS, CALCULATOR_FUNCTIONS, CALCULATOR_LAMBDAS
import copy

class InterfaceSpecification:
    def __init__(self, className, constructors, methods) -> None:
        self.className = className
        self.constructors = constructors
        self.methods = methods

class MethodSignature:
    def __init__(self, methodName, returnType, parameterTypes) -> None:
        self.methodName = methodName
        self.returnType = returnType
        self.parameterTypes = parameterTypes

class ClassUnderTest:
    def __init__(self, className, code, methods) -> None:
        self.className = className
        self.code = code
        self.className = className
        self.methods = methods
        self.classInstance = None
        
        local_namespace = {}
        exec(code, globals(), local_namespace)
        for name, obj in local_namespace.items():
            if isinstance(obj, type):
                self.classInstance = obj()

def create_permutations(interfaceSpecification, classUnderTest):
    permutations = []

    adaptedMethod = False
    classInstance = copy.deepcopy(classUnderTest.classInstance)

    for classMethod in classUnderTest.methods:
        
        for interfaceMethod in interfaceSpecification.methods:
            
            if interfaceMethod.methodName != classMethod.methodName and not (hasattr(classInstance, interfaceMethod.methodName)):
                print(f"Adaptating {classMethod.methodName} to {interfaceMethod.methodName}")
                adaptedMethod = True
                classInstance = adapt_method_name(classInstance, classMethod.methodName, interfaceMethod.methodName)
                break
            
            # if interfaceMethod.returnType != classMethod.returnType:
            #     adaptationNeeded = True
            
            # if interfaceMethod.parameterTypes != classMethod.parameterTypes:
            #     adaptationNeeded = True
            
    if (adaptedMethod):
        permutations.append(classInstance)
            
    return permutations

def adapt_method_name(class_instance, existing_method_name, new_method_name):
    original_method = getattr(class_instance, existing_method_name)
    
    if original_method is None:
        raise AttributeError(f"The method '{existing_method_name}' does not exist on the provided object.")
    
    setattr(class_instance, new_method_name, original_method)
    return class_instance


def adapt_method(class_instance, original_method_name, adapted_method_name, param_order, param_types=None):
    # Get the original method from the object
    original_method = getattr(class_instance, original_method_name)

    if not original_method:
        raise AttributeError(f"Method '{original_method_name}' not found.")

    def wrapper(*args):
        # Reorder arguments and optionally convert their types
        new_args = []
        for index, type_ in zip(param_order, param_types):
            new_arg = args[index]
            if type_:
                new_arg = type_(new_arg)
            new_args.append(new_arg)

        # Call the original method with new arguments
        return original_method(*new_args)

    # Attach the new method to the object under the new name
    setattr(class_instance, adapted_method_name, wrapper)

if __name__ == "__main__":
    plus = MethodSignature("plus", "float", ["int", "float"])
    minus = MethodSignature("minus", "float", ["float", "int"])
    interfaceSpecification = InterfaceSpecification("Calculator", [], [plus, minus])

    add = MethodSignature("add", "int", ["int", "int"])
    subtract = MethodSignature("subtract", "int", ["int", "int"])
    classUnderTest = ClassUnderTest("Calculator", CALCULATOR_CLASS, [add, subtract])

    permutations = create_permutations(interfaceSpecification, classUnderTest)
    print(permutations)

    print(permutations[0].minus(1, 2))

    # adapt_method(class_instance, 'add', 'plus', [1, 0], [float, float])
    # print(class_instance.plus('10', '5'))
