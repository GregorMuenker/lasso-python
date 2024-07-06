import pandas as pd
import itertools
from stimulus_sheet_reader import get_stimulus_sheet
from test_data import CALCULATOR_CLASS, CALCULATOR_MODULE, PARAM_ORDER, code_string
from module_parser import parse_code
from collections import Counter
import types
import importlib
import builtins

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
    def __init__(self, moduleName, functions) -> None:
        self.moduleName = moduleName
        self.functions = functions # List of FunctionSignature objects
        self.classes = {} # This stores class names (keys) and list of their constructors as FunctionSignature objects (values)
        self.constructors = [] # TODO this is actually unused so far

class FunctionSignature:
    def __init__(self, functionName, returnType, parameterTypes, parentClass) -> None:
        self.functionName = functionName
        self.returnType = returnType
        self.parameterTypes = parameterTypes
        self.parentClass = parentClass

class AdaptationHandler:
    def __init__(self, interfaceSpecification, moduleUnderTest, excludeClasses = False):
        self.interfaceMethods = {}
        for method in interfaceSpecification.methods:
            self.interfaceMethods[method.methodName] = method
        
        self.moduleFunctions = {}
        for function in moduleUnderTest.functions:
            if (function.parentClass != None and excludeClasses == True):
                continue
            self.moduleFunctions[function.functionName] = function

        self.classes = {}
        if excludeClasses == False:
            self.classes = moduleUnderTest.classes
        
        self.adaptations = {}

        self.mappings = []

    def identifyAdaptations(self):
        for interfaceMethodName, interfaceMethod in self.interfaceMethods.items():
            for moduleFunctionName, moduleFunction in self.moduleFunctions.items():
                
                self.adaptations[(interfaceMethodName, moduleFunctionName)] = []
                
                if interfaceMethod.parameterTypes.__len__() != moduleFunction.parameterTypes.__len__():
                    self.adaptations[(interfaceMethodName, moduleFunctionName)] = None # no adaptation possible
                    continue
                
                if interfaceMethodName != moduleFunctionName:
                    self.adaptations[(interfaceMethodName, moduleFunctionName)].append("Name")

                if interfaceMethod.returnType != moduleFunction.returnType:
                    self.adaptations[(interfaceMethodName, moduleFunctionName)].append("Return")

                if interfaceMethod.parameterTypes != moduleFunction.parameterTypes:
                    if (Counter(interfaceMethod.parameterTypes) == Counter(moduleFunction.parameterTypes)):
                        self.adaptations[(interfaceMethodName, moduleFunctionName)].append("Param permutation")
                    else:
                        self.adaptations[(interfaceMethodName, moduleFunctionName)].append("Param conversion")

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
        
        print(f"Generated {self.mappings.__len__()} potential mappings:")
        for mapping in self.mappings:
            print(mapping)
    
def create_adapted_module(adaptationHandler, module_name):    
    module = importlib.import_module(module_name)
    # print(module.__file__) # print the path of the module

    successes = 0
    failed_functions = []
    all_submodules_metadata = []
    for mapping in adaptationHandler.mappings:
        success = True
        print(f"\n----------------------\nTRYING ADAPTATION FOR MAPPING {mapping}.\n----------------------")
        submodule_name = "adaptation" + str(successes)
        submodule = types.ModuleType(submodule_name)
        setattr(module, submodule_name, submodule)

        submodule_metadata = {}
        instantiated_classes = {}
        for identifier in mapping:
            interfaceMethodName, moduleFunctionName = identifier
            submodule_metadata[interfaceMethodName] = moduleFunctionName
            
            if (moduleFunctionName) in failed_functions:
                print(f"Cancelling adaptation for mapping {mapping} as {moduleFunctionName} failed previously.")
                success = False
                break

            neededAdaptations = adaptationHandler.adaptations[(interfaceMethodName, moduleFunctionName)]
            
            function = None
            
            try:
                parent_class_name = adaptationHandler.moduleFunctions[moduleFunctionName].parentClass

                # function is a class method => instantiate the class
                if parent_class_name:
                    
                    if parent_class_name in instantiated_classes:
                        print(f"Using already instantiated class {parent_class_name}.")
                        parent_class_instance = instantiated_classes[parent_class_name]
                    else:
                        print(f"Trying to instantiate class {parent_class_name}.")
                        if adaptationHandler.classes[parent_class_name].__len__() == 0:
                            print(f"No constructors found for class {parent_class_name}.")
                        else:
                            print(f"Contructor(s) found for class {parent_class_name}.")
                        
                        parent_class = getattr(module, parent_class_name)
                        parent_class_instance = parent_class()
                        instantiated_classes[parent_class_name] = parent_class_instance
                    
                    # Remove the class name from the function name and get the function object
                    parts = moduleFunctionName.split('.', 1)
                    function = getattr(parent_class_instance, parts[1])

                # function is a standalone function
                else:
                    function = getattr(module, moduleFunctionName)

            except (TypeError, AttributeError) as e:
                failed_functions.append(moduleFunctionName)
                print(f"The function '{moduleFunctionName}' throws an error: {e}.")
                success = False
                break
            else:
                # function was found in the module, continue with adaptation
                # strategy: create a submodule that contains the adapted function
                new_function = function
                setattr(submodule, moduleFunctionName, new_function) # Add the new function to the submodule

                if "Name" in neededAdaptations:
                    adapt_function_name(submodule, new_function, interfaceMethodName)

                if "Return" in neededAdaptations:
                    adapt_return_type(submodule, new_function, interfaceMethodName, adaptationHandler.interfaceMethods[interfaceMethodName].returnType)

                if "Param" in neededAdaptations:
                    pass
                    
        if (success):
            print(f"\033[92mAdaptation with id {successes} successful.\033[0m")
            all_submodules_metadata.append(submodule_metadata)
            successes += 1

       
    print(f"\n{successes}/{adaptationHandler.mappings.__len__()} adapted mappings.")
    return (module, successes, all_submodules_metadata)

def adapt_function_name(module, function, new_function_name):
    setattr(module, new_function_name, function)
    print(f"Adapted name of {function} to {new_function_name}.")

def adapt_return_type(module, function, function_name, new_return_type):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = None
            try:
                result = func(*args, **kwargs)
                return getattr(builtins, new_return_type)(result)
            except (AttributeError, ValueError, TypeError) as e:
                #print(f"Error when trying to adapt return type: {e}. Returning original result.")
                return result 
        return wrapper
    
    setattr(module, function_name, decorator(function))
    print(f"Adapted return type of {function} to {new_return_type}.")


def execute_test(stimulus_sheet, adapted_module, number_of_submodules, submodules_metadata):
    all_results = []
    for i in range(number_of_submodules):
        results = []
        results.append(f"{i}")
        results.append(f"{submodules_metadata[i]}\t\t")
        submodule = getattr(adapted_module, "adaptation" + str(i))

        for _, row in stimulus_sheet.iterrows():
            method_name = row['method_name']
            input_params = row['input_params']

            method = getattr(submodule, method_name)

            input_params_string = ', '.join(map(str, input_params))

            instruction = f"{method_name}({input_params_string})"
            return_value = method(*input_params)

            results.append((instruction, return_value))
        all_results.append(results)
    
    print("\n\nResults from executing stimulus sheet:")

    for results in all_results:
        print(' '.join(map(str, results)))

if __name__ == "__main__":
    icubed = MethodSignature("icubed", "int", ["int"])
    iminus = MethodSignature("iminus", "float", ["float", "float"])

    interfaceSpecification = InterfaceSpecification("Calculator", [], [icubed, iminus])

    # TODO adjust this path
    path = "/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages/numpy/lib/scimath.py" #function_base #user_array #numpy/matrixlib/defmatrix.py
    with open(path, 'r') as file:
        file_content = file.read()  # Read the entire content of the file
        moduleUnderTest = parse_code(file_content)

    adaptationHandler = AdaptationHandler(interfaceSpecification, moduleUnderTest, excludeClasses=True)
    adaptationHandler.identifyAdaptations()
    adaptationHandler.visualizeAdaptations()
    adaptationHandler.generateMappings()
        
    (adapted_module, number_of_submodules, submodules_metadata)  = create_adapted_module(adaptationHandler, 'numpy')

    stimulus_sheet = get_stimulus_sheet("calc3.csv")
    execute_test(stimulus_sheet, adapted_module, number_of_submodules, submodules_metadata)

    # TESTING STUFF
    # print(adapted_module.adaptation0.sqrt(2))
    # test = getattr(adapted_module, "adaptation6")
    # print(inspect.getmembers(test, inspect.isfunction))