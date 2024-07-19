import pandas as pd
import itertools
from stimulus_sheet_reader import get_stimulus_sheet
from test_data import CALCULATOR_CLASS, CALCULATOR_MODULE, PARAM_ORDER, code_string
from module_parser import parse_code
from collections import Counter
import types
import importlib
from collections import defaultdict
import math
import copy

# ANSI escape codes for colored output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"

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
    def __init__(self, functionName, returnType, parameterTypes, parentClass, firstDefault) -> None:
        self.functionName = functionName
        self.returnType = returnType
        self.parameterTypes = parameterTypes
        self.parentClass = parentClass
        self.firstDefault = firstDefault

class AdaptationHandler:
    def __init__(self, interfaceSpecification, moduleUnderTest, excludeClasses = False, useFunctionDefaultValues = False):
        self.interfaceMethods = {}
        for method in interfaceSpecification.methods:
            self.interfaceMethods[method.methodName] = method
        
        self.moduleFunctions = {}
        for function in moduleUnderTest.functions:
            if (function.parentClass != None and excludeClasses == True):
                continue
            self.moduleFunctions[function.functionName] = function
            if useFunctionDefaultValues:
                self.moduleFunctions[function.functionName].parameterTypes = function.parameterTypes[:function.firstDefault]

        self.classes = {}
        if excludeClasses == False:
            self.classes = moduleUnderTest.classes
        
        self.adaptations = {}
        self.adaptationsMetadata = []
        self.mappings = []

    def identifyAdaptations(self, maxParamPermutationTries = 1):
        for interfaceMethodName, interfaceMethod in self.interfaceMethods.items():
            for moduleFunctionName, moduleFunction in self.moduleFunctions.items():
                
                self.adaptations[(interfaceMethodName, moduleFunctionName)] = []
                
                if interfaceMethod.parameterTypes.__len__() != moduleFunction.parameterTypes.__len__():
                    self.adaptations[(interfaceMethodName, moduleFunctionName)] = None # no adaptation possible
                    continue
                
                adaptationCandidate = []

                if interfaceMethodName != moduleFunctionName:
                    adaptationCandidate.append("Name")

                if interfaceMethod.returnType != moduleFunction.returnType:
                        adaptationCandidate.append("Return") # TODO type strictness check

                adaptationCandidateCopy = copy.deepcopy(adaptationCandidate)

                if interfaceMethod.parameterTypes != moduleFunction.parameterTypes:
                    if (Counter(interfaceMethod.parameterTypes) == Counter(moduleFunction.parameterTypes)):
                        adaptationCandidate.append("Permutation")
                    else: # TODO type strictness check
                        adaptationCandidate.append("Conversion")
                
                score = -len(adaptationCandidate) # TODO refine this score, currently this only gives a penalty for each needed adaptation (e.g., name + return = -2)
                self.adaptations[(interfaceMethodName, moduleFunctionName)].append(adaptationCandidate)
                self.adaptationsMetadata.append((interfaceMethodName, moduleFunctionName, 0, score)) # This is needed later to generate the mappings
                
                numOfParamPermutations = math.factorial(moduleFunction.parameterTypes.__len__())
                iterations = min(maxParamPermutationTries, numOfParamPermutations)
                for i in range(1, iterations):
                    self.adaptations[(interfaceMethodName, moduleFunctionName)].append(adaptationCandidateCopy)
                    self.adaptationsMetadata.append((interfaceMethodName, moduleFunctionName, i, score))

    def visualizeAdaptations(self) -> None:
        df = pd.DataFrame(columns=list(self.moduleFunctions.keys()), index=list(self.interfaceMethods.keys()))

        for key, value in self.adaptations.items():
            interfaceMethodName, moduleFunctionName = key
            df.at[interfaceMethodName, moduleFunctionName] = value

        print("\n", df, "\n")      

    def generateMappings(self):
        # Generate all possible permutations (with length = number of interface methods) of all adapters of the module functions
        allFunctionPermutations = itertools.permutations(self.adaptationsMetadata, self.interfaceMethods.keys().__len__())
        
        for functionPermutation in allFunctionPermutations:
            potentialMapping = []
            totalScore = 0

            # Try to adapt each module function in the permutation to the corresponding interface method
            for interfaceMethodName in self.interfaceMethods.keys():
                # Iterate through the permutation by taking the first element and removing it from the functionPermutation list
                (interfaceMethodId, moduleFunctionId, adaptationId, score) = functionPermutation[0]
                functionPermutation = functionPermutation[1:]
                
                if (self.adaptations[(interfaceMethodName, moduleFunctionId)] != None and interfaceMethodName == interfaceMethodId): # TODO is last check needed?
                    # The current module function can be adapted, add it to the potential mapping
                    potentialMapping.append((interfaceMethodName, moduleFunctionId, adaptationId, score))
                    totalScore += score
                else:
                    # At least one module function in the permutation is not adaptable
                    break
            
            # Check if the potential mapping is complete (i.e. length = number of interface methods)
            if potentialMapping.__len__() == self.interfaceMethods.keys().__len__():
                self.mappings.append(potentialMapping)
                # TODO potentially add totalScore to the mapping (sum of scores for interface method/module function pairs)
        
        print(f"Generated {self.mappings.__len__()} potential mappings:")
        for mapping in self.mappings:
            print(mapping)
    
def create_adapted_module(adaptationHandler, module_name, use_constructor_default_values = False):
    module = importlib.import_module(module_name)
    # print(module.__file__) # print the path of the module
    
    # TODO import library from file
    # spec = importlib.util.spec_from_file_location(module_name, "/Users/florianruhle/Studium/Master/FSS24/Project/lasso-python/py-container/arena/test_data_file.py")
    # module = importlib.util.module_from_spec(spec)
    # spec.loader.exec_module(module)

    successes = 0
    failed_functions = []
    all_submodules_metadata = []

    for mapping in adaptationHandler.mappings:

        success = True
        print(f"\n-----------------------------\nTRYING ADAPTATION FOR MAPPING {mapping}.\n-----------------------------")
        submodule_name = "adaptation" + str(successes)
        submodule = types.ModuleType(submodule_name)
        setattr(module, submodule_name, submodule)

        submodule_metadata = {}
        instantiated_classes = {}
        for identifier in mapping:
            interfaceMethodName, moduleFunctionName, numOfAdapter, score = identifier
            submodule_metadata[interfaceMethodName] = (moduleFunctionName, numOfAdapter)
            
            if (moduleFunctionName) in failed_functions:
                print(f"Cancelling adaptation for mapping {mapping} as {moduleFunctionName} failed previously.")
                success = False
                break

            neededAdaptations = adaptationHandler.adaptations[(interfaceMethodName, moduleFunctionName)][numOfAdapter]
            
            function = None
            
            try:
                parent_class_name = adaptationHandler.moduleFunctions[moduleFunctionName].parentClass

                # function is a class method that has already been instantiated
                if parent_class_name and parent_class_name in instantiated_classes:
                    print(f"Using already instantiated class {parent_class_name}.")
                    parent_class_instance = instantiated_classes[parent_class_name]
                    
                    # remove the class name from the function name and get the function object
                    parts = moduleFunctionName.split('.', 1)
                    function = getattr(parent_class_instance, parts[1])
                
                # function is a class method that has not been instantiated yet
                elif parent_class_name:
                    successful_instantiation, parent_class_instance = instantiate_class(module, parent_class_name, use_constructor_default_values, adaptationHandler.classes[parent_class_name])
                    if (successful_instantiation):
                        instantiated_classes[parent_class_name] = parent_class_instance
                
                        # remove the class name from the function name and get the function object
                        parts = moduleFunctionName.split('.', 1)
                        function = getattr(parent_class_instance, parts[1])
                    else:
                        failed_functions.append(moduleFunctionName)
                        print(f"Failed to instantiate class {parent_class_name}.")
                        success = False
                        break

                # function is a standalone function
                else:
                    function = getattr(module, moduleFunctionName)

            except Exception as e:
                failed_functions.append(moduleFunctionName)
                print(f"For function '{moduleFunctionName}' there is an error: {e}.")
                success = False
                break
            else:
                # function was found in the module, continue with adaptation: create a submodule that contains the adapted function
                new_function = function
                setattr(submodule, moduleFunctionName, new_function) # Add the new function to the submodule

                if (len(neededAdaptations) > 0):

                    new_return_type = None
                    convert_to_types = None
                    current_param_order= None
                    new_param_order = None

                    if "Return" in neededAdaptations:
                        new_return_type = adaptationHandler.interfaceMethods[interfaceMethodName].returnType
                        print(f"Trying to adapt return type of {new_function} to {new_return_type}.")

                    if "Conversion" in neededAdaptations:
                        convert_to_types = adaptationHandler.moduleFunctions[moduleFunctionName].parameterTypes
                        print(f"Trying to adapt parameter types of {new_function} to {convert_to_types}.")

                    if "Permutation" in neededAdaptations:
                        current_param_order = adaptationHandler.moduleFunctions[moduleFunctionName].parameterTypes
                        new_param_order = adaptationHandler.interfaceMethods[interfaceMethodName].parameterTypes
                        print(f"{RED}Trying to adapt parameter order of {new_function}{RESET}.")
                    
                    new_function = adapt_function(new_function, new_return_type, convert_to_types, current_param_order, new_param_order)

                    if "Name" in neededAdaptations:
                        setattr(submodule, interfaceMethodName, new_function)
                        print(f"Adapted name of function {new_function} to {interfaceMethodName}.")
                    
        if (success):
            print(f"{GREEN}Adaptation with id {successes} successful.{RESET}")
            all_submodules_metadata.append(submodule_metadata)
            successes += 1

       
    print(f"\n{successes}/{adaptationHandler.mappings.__len__()} adapted mappings.")
    return (module, successes, all_submodules_metadata)

def instantiate_class(module, parent_class_name, use_constructor_default_values, constructors):
    print(f"Trying to instantiate class {parent_class_name}.")
    parent_class = getattr(module, parent_class_name)
    parent_class_instance = None
    successful_instantiation = False

    if constructors.__len__() == 0:
        print(f"No constructors found for class {parent_class_name}, trying instantiation call: {parent_class_name}().")
        parent_class_instance = parent_class()
    else:
        print(f"{constructors.__len__()} constructor(s) found for class {parent_class_name}.")
        for constructor in constructors: # TODO make sure that __new__ is used before __init__
            
            parameterTypes = constructor.parameterTypes
            print(f"Trying constructor {constructor.functionName}, parameter types: {parameterTypes}.")
            
            try:
                if use_constructor_default_values:
                    parameterTypes = parameterTypes[:constructor.firstDefault]
                    print(f"Using default values for constructor parameters, last {len(constructor.parameterTypes) - len(parameterTypes)} parameters were dropped.")

                # Strategy: get standard values for each data type (defined somewhere below) and try to instantiate the class with them, if datatype is unknown use value 1
                parameters = tuple(standard_constructor_values.get(parameterType, 1) for parameterType in parameterTypes)

                if parameters.__len__() > 0:
                    print(f"Trying instantiation call: {parent_class_name}({parameters}).")
                    parent_class_instance = parent_class(parameters)
                    print(f"Produced class instance: {parent_class_instance}.")
                else:
                    print(f"Trying instantiation call: {parent_class_name}().")
                    parent_class_instance = parent_class()
                    print(f"Produced class instance: {parent_class_instance}.")

            except (TypeError, ValueError) as e:
                print(f"Constructor {constructor.functionName} failed: {e}.")
                continue
            
            else:
                successful_instantiation = True
                break # using the constructor was successful, break the loop
    
    return successful_instantiation, parent_class_instance

def adapt_function(function, new_return_type = None, convert_to_types = None, current_param_order= None, new_param_order = None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = None
            try:
                # Adapt parameter order
                if (current_param_order and new_param_order):
                    type_value_dict = defaultdict(list)
                    for data_type, value in zip(current_param_order, args):
                        type_value_dict[data_type].append(value)
                    
                    reordered_args = []
                    for data_type in new_param_order:
                        if type_value_dict[data_type]:
                            reordered_args.append(type_value_dict[data_type].pop(0))
                    
                    args = reordered_args

                # Adapt parameter types
                if (convert_to_types):
                    target_types = [type_mapping.get(type_name, int) for type_name in convert_to_types]
                    args = [target_type(arg) for arg, target_type in zip(args, target_types)]

                result = func(*args, **kwargs)
                
                # Adapt return type
                if (new_return_type):
                    result = type_mapping.get(new_return_type, int)(result) # TODO handling of unknown types, alternative without type_mapping dict: getattr(builtins, new_return_type)(result)
                
                return result
            except Exception as e:
                print(f"Error when trying to adapt function {function} (result without adaptations will be returned): {e}.")
                return result
        return wrapper
    
    print("Created adapted wrapper function.")
    return decorator(function)

def execute_test(stimulus_sheet, adapted_module, number_of_submodules, submodules_metadata):
    print(f"\nExecuting stimulus sheet on {adapted_module.__name__}")
    all_results = []
    for i in range(number_of_submodules):
        results = []
        results.append(f"{i}")
        results.append(f"{submodules_metadata[i]}\t\t")
        submodule = getattr(adapted_module, "adaptation" + str(i))

        for _, row in stimulus_sheet.iterrows():
            method_name = row['method_name']
            input_params = row['input_params']

            input_params_string = ', '.join(map(str, input_params))
            instruction = f"{method_name}({input_params_string})"

            method = None
            try:
                method = getattr(submodule, method_name)
            except AttributeError as e:
                print(f"Error when trying to get method {method_name} from submodule {submodule}. Error: {e}")
                results.append((instruction, "Error"))
                continue

            return_value = "Error"
            try:
                return_value = method(*input_params)
            except Exception as e:
                print(f"Error when executing instruction: {instruction}: {e}")

            results.append((instruction, return_value))
        all_results.append(results)
    
    print("\n\nResults from executing stimulus sheet:")

    for results in all_results:
        print(' '.join(map(str, results)))

standard_constructor_values = {
    'str': "",
    'int': 1,
    'float': 1.0,
    'complex': 1 + 1j,
    'list': [],
    'tuple': (),
    'range': range(1),
    'dict': {},
    'set': set(),
    'fronzenset': frozenset(),
    'bool': True,
    'bytes': b'',
    'bytearray': bytearray(b''),
    'memoryview': memoryview(b''),
    'None': None,     
}

type_mapping = {
    'str': str,
    'int': int,
    'float': float,
    'complex': complex,
    'list': list,
    'tuple': tuple,
    'range': range,
    'dict': dict,
    'set': set,
    'fronzenset': frozenset,
    'bool': bool,
    'bytes': bytes,
    'bytearray': bytearray,
    'memoryview': memoryview
}

possible_conversions = {
    'bool': ['bool', 'str', 'int', 'float', 'complex', 'range', 'bytes', 'bytearray'],
    'bytearray': ['bytearray', 'str', 'list', 'tuple', 'dict', 'set', 'frozenset', 'bool', 'bytes', 'memoryview'],
    'bytes': ['bytes', 'str', 'list', 'tuple', 'dict', 'set', 'frozenset', 'bool', 'bytearray', 'memoryview'],
    'complex': ['complex', 'str', 'bool'],
    'dict': ['dict', 'str', 'list', 'tuple', 'set', 'frozenset', 'bool', 'bytes', 'bytearray'],
    'float': ['float', 'str', 'int', 'complex', 'bool'],
    'frozenset': ['frozenset', 'str', 'list', 'tuple', 'dict', 'set', 'bool', 'bytes', 'bytearray'],
    'int': ['int', 'str', 'float', 'complex', 'range', 'bool', 'bytes', 'bytearray'],
    'list': ['list', 'str', 'tuple', 'dict', 'set', 'frozenset', 'bool', 'bytes', 'bytearray'],
    'memoryview': ['memoryview'],
    'range': ['range'],
    'set': ['set', 'str', 'list', 'tuple', 'dict', 'frozenset', 'bool', 'bytes', 'bytearray'],
    'str': ['str', 'list', 'tuple', 'dict', 'set', 'frozenset', 'bool'],
    'tuple': ['tuple', 'str', 'list', 'dict', 'set', 'frozenset', 'bool', 'bytes', 'bytearray']
}

def can_convert_params(source_types, target_types):
    if len(source_types) != len(target_types):
        return False
    
    for source, target in zip(source_types, target_types):
        # Check if conversion is possible
        if target not in possible_conversions.get(source, []):
            return False

    return True

def can_convert_type(source_type, target_type):
    return target_type in possible_conversions.get(source_type, [])

if __name__ == "__main__":
    icubed = MethodSignature("icubed", "str", ["int"])
    iminus = MethodSignature("iminus", "str", ["str", "int"])

    interfaceSpecification = InterfaceSpecification("Calculator", [], [icubed, iminus])

    # TODO adjust this path
    path = "/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages/numpy/lib/scimath.py" #function_base #user_array #scimath
    # path = "/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages/numpy/matrixlib/defmatrix.py"
    # path = "/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages/numpy/array_api/_array_object.py"
    # path = "/Users/florianruhle/Studium/Master/FSS24/Project/lasso-python/py-container/arena/test_data_file.py"
    with open(path, 'r') as file:
        file_content = file.read()  # Read the entire content of the file
        moduleUnderTest = parse_code(file_content)

    adaptationHandler = AdaptationHandler(interfaceSpecification, moduleUnderTest, excludeClasses=False, useFunctionDefaultValues=True)
    adaptationHandler.identifyAdaptations(maxParamPermutationTries=2)
    adaptationHandler.visualizeAdaptations()
    adaptationHandler.generateMappings()
        
    (adapted_module, number_of_submodules, submodules_metadata)  = create_adapted_module(adaptationHandler, 'numpy.lib.scimath', use_constructor_default_values=True)

    stimulus_sheet = get_stimulus_sheet("calc3.csv")
    execute_test(stimulus_sheet, adapted_module, number_of_submodules, submodules_metadata)