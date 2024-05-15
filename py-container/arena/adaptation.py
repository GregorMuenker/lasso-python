import copy
import pandas as pd
import itertools
from stimulus_sheet_reader import get_stimulus_sheet
from test_data import CALCULATOR_CLASS
from class_parser import parse_class

class InterfaceSpecification:
    def __init__(self, className, constructors, methods) -> None:
        self.className = className
        self.constructors = constructors
        self.methods = methods

class ClassUnderTest:
    def __init__(self, className, codeString, methods) -> None:
        self.className = className
        self.codeString = codeString
        self.className = className
        self.methods = methods # List of MethodSignature objects
        self.classInstance = None
        
        local_namespace = {}
        exec(codeString, globals(), local_namespace)
        self.classInstance = next(iter(local_namespace.values()))()

class MethodSignature:
    def __init__(self, methodName, returnType, parameterTypes) -> None:
        self.methodName = methodName
        self.returnType = returnType
        self.parameterTypes = parameterTypes

class AdaptationHandler:
    def __init__(self, interfaceSpecification, classUnderTest):
        self.interfaceMethods = {}
        for method in interfaceSpecification.methods:
            self.interfaceMethods[method.methodName] = method
        
        self.classMethods = {}
        for method in classUnderTest.methods:
            self.classMethods[method.methodName] = method
        
        self.adaptations = {}

        self.mappings = []

        self.classInstances = []

    def identifyAdaptations(self):
        for interfaceMethodId, interfaceMethod in self.interfaceMethods.items():
            for classMethodId, classMethod in self.classMethods.items():

                self.adaptations[(interfaceMethod.methodName, classMethod.methodName)] = []
                
                if interfaceMethod.parameterTypes.__len__() != classMethod.parameterTypes.__len__():
                    self.adaptations[(interfaceMethod.methodName, classMethod.methodName)] = None
                    continue
                
                if interfaceMethod.methodName != classMethod.methodName:
                    self.adaptations[(interfaceMethod.methodName, classMethod.methodName)].append("Name")

                if interfaceMethod.returnType != classMethod.returnType:
                    self.adaptations[(interfaceMethod.methodName, classMethod.methodName)].append("Return")

                if interfaceMethod.parameterTypes != classMethod.parameterTypes:
                    self.adaptations[(interfaceMethod.methodName, classMethod.methodName)].append("Params")

    def visualizeAdaptations(self) -> None:
        df = pd.DataFrame(columns=list(self.classMethods.keys()), index=list(self.interfaceMethods.keys()))

        for key, value in self.adaptations.items():
            interfaceMethodName, classMethodName = key
            df.at[interfaceMethodName, classMethodName] = value

        print("\n", df, "\n")      

    def generateMappings(self):
        classMethodIds = list(self.classMethods.keys())
        allClassMethodPermutations = itertools.permutations(classMethodIds, self.interfaceMethods.keys().__len__())

        for classMethodPermutation in allClassMethodPermutations:
            potentialMapping = []

            for interfaceMethodId in self.interfaceMethods.keys():
                classMethodId = classMethodPermutation[0]
                classMethodPermutation = classMethodPermutation[1:]
                if (self.adaptations[(interfaceMethodId, classMethodId)] != None):
                    potentialMapping.append((interfaceMethodId, classMethodId))
                else:
                    break
            
            if potentialMapping.__len__() == self.interfaceMethods.keys().__len__():
                self.mappings.append(potentialMapping)
        
        print(f"Generated {self.mappings.__len__()} mappings: {self.mappings}")
    
    def generateClassInstances(self, _classInstance):
        for mapping in self.mappings:
            classInstance = copy.deepcopy(_classInstance)
            for identifier in mapping:
                interfaceMethodId, classMethodId = identifier
                neededAdaptations = self.adaptations[(interfaceMethodId, classMethodId)]
                
                if "Name" in neededAdaptations:
                    adapt_method_name(classInstance, classMethodId, interfaceMethodId)

                if "Return" in neededAdaptations:
                    adapt_return_type(classInstance, interfaceMethodId, self.interfaceMethods[interfaceMethodId].returnType)

                if "Params" in neededAdaptations:
                    pass
            
            self.classInstances.append(classInstance)
        print(f"Generated {self.classInstances.__len__()} class instances")
            

def adapt_method_name(class_instance, existing_method_name, new_method_name):
    original_method = getattr(class_instance, existing_method_name)
    
    if original_method is None:
        raise AttributeError(f"The method '{existing_method_name}' does not exist on the provided object.")
    
    setattr(class_instance, new_method_name, original_method)

def adapt_return_type(class_instance, method_name, new_return_type):
    method = getattr(class_instance, method_name)
    
    if method is None:
        raise AttributeError(f"The method '{method_name}' does not exist on the provided object.")

    def wrapper(*args, **kwargs):
        result = method(*args, **kwargs) 
        if new_return_type == "float":
            # print("Converting return value to float")
            return float(result)
        else:
            # print("Unsupported return type conversion, returning original value.")
            return result

    # Set the wrapper function as the new method of the class instance
    setattr(class_instance, method_name, wrapper)


def execute_test(stimulus_sheet, classInstance):
    results = []
    
    for _, row in stimulus_sheet.iterrows():
        method_name = row['method_name']
        input_params = row['input_params']

        method = getattr(classInstance, method_name)

        instruction = f"{method_name}({input_params})"
        return_value = method(*input_params)
        results.append((instruction, return_value))
    
    print(results)

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
    plus = MethodSignature("iplus", "int", ["Any", "int", "int"])
    minus = MethodSignature("iminus", "float", ["Any", "float", "float"])
    times = MethodSignature("itimes", "float", ["Any", "float", "float", "float"])
    interfaceSpecification = InterfaceSpecification("Calculator", [], [plus, minus, times])
    
    classUnderTest = parse_class(CALCULATOR_CLASS) # analyzer from Zhihang should actually do this

    adaptationHandler = AdaptationHandler(interfaceSpecification, classUnderTest)
    adaptationHandler.identifyAdaptations()
    adaptationHandler.visualizeAdaptations()
    adaptationHandler.generateMappings()
    adaptationHandler.generateClassInstances(classUnderTest.classInstance)

    stimulusSheet = get_stimulus_sheet("calc3.csv")
    for classInstance in adaptationHandler.classInstances:
        execute_test(stimulusSheet, classInstance)
    
    print(adaptationHandler.classInstances[0].itimes(1, 2, 3))


    # adapt_method(class_instance, 'add', 'plus', [1, 0], [float, float])
    # print(class_instance.plus('10', '5'))
