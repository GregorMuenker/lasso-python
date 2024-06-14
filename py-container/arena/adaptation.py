import copy
import pandas as pd
import itertools
from stimulus_sheet_reader import get_stimulus_sheet
from test_data import CALCULATOR_CLASS, CALCULATOR_MODULE, code_string
from class_parser import parse_class
from module_parser import parse_code

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

class ModuleUnderTest:
    def __init__(self, moduleName, codeString, functions) -> None:
        self.moduleName = moduleName
        self.codeString = codeString
        self.moduleName = moduleName
        self.functions = functions # List of FunctionSignature objects
        self.classes = []
        self.constructors = []

class FunctionSignature:
    def __init__(self, functionName, returnType, parameterTypes, parentClass) -> None:
        self.functionName = functionName
        self.returnType = returnType
        self.parameterTypes = parameterTypes
        self.parentClass = parentClass

class AdaptationHandler:
    def __init__(self, interfaceSpecification, moduleUnderTest):
        self.interfaceMethods = {}
        for method in interfaceSpecification.methods:
            self.interfaceMethods[method.methodName] = method
        
        self.moduleFunctions = {}
        for function in moduleUnderTest.functions:
            self.moduleFunctions[function.functionName] = function
        
        self.adaptations = {}

        self.mappings = []

        # self.instances = [] # TODO remove

    def identifyAdaptations(self):
        for interfaceMethodName, interfaceMethod in self.interfaceMethods.items():
            for moduleFunctionName, moduleFunction in self.moduleFunctions.items():
                
                self.adaptations[(interfaceMethodName, moduleFunctionName)] = []
                
                if interfaceMethod.parameterTypes.__len__() != moduleFunction.parameterTypes.__len__():
                    self.adaptations[(interfaceMethodName, moduleFunctionName)] = None
                    continue
                
                if interfaceMethodName != moduleFunctionName:
                    self.adaptations[(interfaceMethodName, moduleFunctionName)].append("Name")

                if interfaceMethod.returnType != moduleFunction.returnType:
                    self.adaptations[(interfaceMethodName, moduleFunctionName)].append("Return")

                if interfaceMethod.parameterTypes != moduleFunction.parameterTypes:
                    self.adaptations[(interfaceMethodName, moduleFunctionName)].append("Params")

    def visualizeAdaptations(self) -> None:
        df = pd.DataFrame(columns=list(self.moduleFunctions.keys()), index=list(self.interfaceMethods.keys()))

        for key, value in self.adaptations.items():
            interfaceMethodName, moduleFunctionName = key
            df.at[interfaceMethodName, moduleFunctionName] = value

        print("\n", df, "\n")      

    def generateMappings(self):
        moduleFunctionIds = list(self.moduleFunctions.keys())
        allFunctionPermutations = itertools.permutations(moduleFunctionIds, self.interfaceMethods.keys().__len__())

        for functionPermutation in allFunctionPermutations:
            potentialMapping = []

            for interfaceMethodId in self.interfaceMethods.keys():
                moduleFunctionId = functionPermutation[0]
                functionPermutation = functionPermutation[1:]
                if (self.adaptations[(interfaceMethodId, moduleFunctionId)] != None):
                    potentialMapping.append((interfaceMethodId, moduleFunctionId))
                else:
                    break
            
            if potentialMapping.__len__() == self.interfaceMethods.keys().__len__():
                self.mappings.append(potentialMapping)
        
        print(f"Generated {self.mappings.__len__()} mappings:")
        for mapping in self.mappings:
            print(mapping)
    
def generate_instances(adaptationHandler, instance):
    instances = []
    for mapping in adaptationHandler.mappings:
        instance = copy.deepcopy(instance)
        function_dict = {}
        for identifier in mapping:
            interfaceMethodName, moduleFunctionName = identifier
            neededAdaptations = adaptationHandler.adaptations[(interfaceMethodName, moduleFunctionName)]
            class_instance = None
            # goal: create dictionary with functions/methods names as keys and the obquect as values

            if (moduleFunctionName.contains('.')):
                class_name, method_name = moduleFunctionName.split('.')
                class_instance = instance[class_name]()

            if "Name" in neededAdaptations:
                adapt_method_name(instance, moduleFunctionName, interfaceMethodName)

            if "Return" in neededAdaptations:
                adapt_return_type(instance, interfaceMethodName, adaptationHandler.interfaceMethods[interfaceMethodName].returnType)

            if "Params" in neededAdaptations:
                pass
        
        instances.append(instance)
    print(f"Generated {instances.__len__()} instances")
            

def adapt_method_name(instance, existing_method_name, new_method_name):
    original_method = getattr(instance, existing_method_name)
    
    if original_method is None:
        raise AttributeError(f"The method '{existing_method_name}' does not exist on the provided object.")
    
    setattr(instance, new_method_name, original_method)

def adapt_return_type(instance, method_name, new_return_type):
    method = getattr(instance, method_name)
    
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

    # Set the wrapper function as the new method of the instance
    setattr(instance, method_name, wrapper)


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

if __name__ == "__main__":
    plus = MethodSignature("iplus", "int", ["int", "int"])
    minus = MethodSignature("iminus", "float", ["float", "float"])
    times = MethodSignature("itimes", "float", ["float", "float", "float"])
    interfaceSpecification = InterfaceSpecification("Calculator", [], [plus, minus, times])
    
    moduleUnderTest = parse_code(code_string)

    adaptationHandler = AdaptationHandler(interfaceSpecification, moduleUnderTest)
    adaptationHandler.identifyAdaptations()
    adaptationHandler.visualizeAdaptations()
    adaptationHandler.generateMappings()
    
    import numpy as np
    method = getattr(np, 'asmatrix')

    
    setattr(np, 'asmatrix', method)
    # generate_instances(adaptationHandler, moduleUnderTest.instance)
    

    # stimulusSheet = get_stimulus_sheet("calc3.csv")
    # for classInstance in adaptationHandler.classInstances:
    #     execute_test(stimulusSheet, classInstance)
    
    # print(adaptationHandler.classInstances[0].itimes(1, 2, 3))


    # adapt_method(class_instance, 'add', 'plus', [1, 0], [float, float])
    # print(class_instance.plus('10', '5'))
