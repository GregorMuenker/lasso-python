import copy
import importlib
import itertools
import math
import random
import types
from collections import Counter

import pandas as pd
from constants import BLUE, CYAN, GREEN, MAGENTA, RED, RESET, YELLOW


class InterfaceSpecification:
    def __init__(self, className, constructors, methods) -> None:
        self.className = className
        self.constructors = constructors
        self.methods = methods

    def __repr__(self):
        return f"InterfaceSpecification(className={self.className}, constructors={self.constructors}, methods={self.methods})"


class MethodSignature:
    def __init__(self, methodName, returnType, parameterTypes) -> None:
        self.methodName = methodName
        self.returnType = returnType
        self.parameterTypes = parameterTypes

    def __repr__(self):
        return f"MethodSignature(methodName={self.methodName}, returnType={self.returnType}, parameterTypes={self.parameterTypes})"


class ModuleUnderTest:
    def __init__(self, moduleName, functions, classes=None) -> None:
        self.moduleName = moduleName
        self.functions = functions  # List of FunctionSignature objects
        self.classes = (
            {}
        )  # This stores class names (keys) and list of their constructors as FunctionSignature objects (values)
        self.constructors = []  # NOTE this is actually unused so far

    def __repr__(self) -> str:
        return (
            f"moduleName='{self.moduleName}',\nfunctions='{self.functions}',\n"
            f"classes={self.classes})"
        )


class FunctionSignature:
    def __init__(
        self, functionName, returnType, parameterTypes, parentClass, firstDefault
    ) -> None:
        self.functionName = functionName
        self.returnType = returnType
        self.parameterTypes = parameterTypes
        self.parentClass = parentClass
        self.firstDefault = firstDefault
        if self.parentClass:
            self.qualName = f"{self.parentClass}.{self.functionName}"
        else:
            self.qualName = self.functionName

    def __repr__(self) -> str:
        return (
            f"FunctionSignature(functionName='{self.functionName}', returnType='{self.returnType}', "
            f"parameterTypes={self.parameterTypes}, parentClass='{self.parentClass}', "
            f"firstDefault={self.firstDefault})"
        )


class AdaptationInstruction:
    def __init__(self, interfaceMethodName, moduleFunctionQualName, iteration) -> None:
        self.identifier = (interfaceMethodName, moduleFunctionQualName, iteration)
        self.nameAdaptation = None
        self.returnTypeAdaptation = None
        self.parameterOrderAdaptation = None
        self.blindParameterOrderAdaptation = None
        self.parameterTypeConversion = None
        self.score = 0

    def areAdaptationsNeeded(self) -> bool:
        return (
            self.nameAdaptation
            or self.returnTypeAdaptation
            or self.parameterOrderAdaptation
            or self.blindParameterOrderAdaptation
            or self.parameterTypeConversion
        )

    def calculateScore(self) -> int:
        return random.randint(1, 10)  # TODO work on score calculation

    def __repr__(self) -> str:
        result = ""
        if self.nameAdaptation:
            result += "Name"
        if self.returnTypeAdaptation:
            result += "Rtrn"
        if self.parameterOrderAdaptation:
            result += "Perm"
        if self.blindParameterOrderAdaptation:
            result += "Perm*"
        if self.parameterTypeConversion:
            result += "Convr"
        return result


class Mapping:
    def __init__(self) -> None:
        self.totalScore = 0
        self.adaptationIds = (
            []
        )  # list of tuples (interfaceMethodName, moduleFunctionQualName, iteration)
        self.adaptationInfo = (
            {}
        )  # dictionary with key = interfaceMethodName and value = (moduleFunctionQualName, adaptationInstruction)
        self.executions = (
            {}
        )  # dictionary with key = stimulus sheet id (counting up from 0) and value = list of ExecutionRecord objects

    def __repr__(self) -> str:
        result = ""
        for key, value in self.adaptationInfo.items():
            result += "[" + key + "->" + value[0] + " via " + str(value[1]) + "]"
        result += f" | score={self.totalScore}"
        return result


class AdaptationHandler:
    def __init__(
        self,
        interfaceSpecification,
        moduleUnderTest,
        excludeClasses=False,
        useFunctionDefaultValues=False,
    ):
        """
        The constructor for AdaptationHandler.

        Parameters:
        interfaceSpecification (InterfaceSpecification): Interface specification provided by the user that mainly comprises a list of MethodSignature objects.
        moduleUnderTest (ModuleUnderTest): The parameterized Python module that will be used to implement the interface methods.
        excludeClasses (bool): If true, all functions in the moduleUnderTest with a parent class will be ignored.
        useFunctionDefaultValues (bool): If true, the adaptationHandler will assume that the default parameters of functions will be used with their default values and won't consider them for adaptation.
        """

        self.interfaceMethods = {}
        for method in interfaceSpecification.methods:
            self.interfaceMethods[method.methodName] = method

        self.moduleFunctions = {}
        for function in moduleUnderTest.functions:
            if function.parentClass != None and excludeClasses == True:
                continue
            self.moduleFunctions[function.qualName] = function
            if useFunctionDefaultValues:
                self.moduleFunctions[function.qualName].parameterTypes = (
                    function.parameterTypes[: function.firstDefault]
                )

        self.classes = {}
        if excludeClasses == False:
            self.classes = moduleUnderTest.classes

        self.adaptations = {}
        self.adaptationsList = (
            []
        )  # needed to generate mappings later, contains the same adaptationInstruction objects as the adaptations dict
        self.mappings = []

    def identifyAdaptations(self, maxParamPermutationTries=1):
        """
        Identifies all possible adaptations between all interface method/module function pairs.

        Parameters:
        maxParamPermutationTries (int): The maximum number of adaptations for any given interface method/module function pair.
        """
        print(
            f"\n{MAGENTA}-----------------\nIDENTIFY MAPPINGS\n-----------------{RESET}"
        )
        for interfaceMethodName, interfaceMethod in self.interfaceMethods.items():
            for moduleFunctionQualName, moduleFunction in self.moduleFunctions.items():

                self.adaptations[(interfaceMethodName, moduleFunctionQualName)] = []

                if (
                    interfaceMethod.parameterTypes.__len__()
                    != moduleFunction.parameterTypes.__len__()
                ):
                    self.adaptations[(interfaceMethodName, moduleFunctionQualName)] = (
                        None  # no adaptation possible
                    )
                    continue

                adaptationInstruction = AdaptationInstruction(
                    interfaceMethodName, moduleFunctionQualName, 0
                )

                if interfaceMethodName != moduleFunctionQualName:
                    adaptationInstruction.nameAdaptation = interfaceMethodName

                if interfaceMethod.returnType != moduleFunction.returnType:
                    adaptationInstruction.returnTypeAdaptation = (
                        interfaceMethod.returnType
                    )

                adaptationInstructionCopy = copy.deepcopy(
                    adaptationInstruction
                )  # create copy that can be used for blind parameter permutations

                if interfaceMethod.parameterTypes != moduleFunction.parameterTypes:
                    if Counter(interfaceMethod.parameterTypes) == Counter(
                        moduleFunction.parameterTypes
                    ):
                        adaptationInstruction.parameterOrderAdaptation = (
                            find_permutation(
                                moduleFunction.parameterTypes,
                                interfaceMethod.parameterTypes,
                            )
                        )

                    else:  # TODO type strictness check
                        adaptationInstruction.parameterTypeConversion = (
                            moduleFunction.parameterTypes
                        )

                self.adaptations[(interfaceMethodName, moduleFunctionQualName)].append(
                    adaptationInstruction
                )
                self.adaptationsList.append(adaptationInstruction)

                # Blind parameter permutations, i.e. just permutate them without caring about types
                numOfParamPermutations = math.factorial(
                    moduleFunction.parameterTypes.__len__()
                )
                iterations = min(maxParamPermutationTries, numOfParamPermutations)
                orderedList = list(range(moduleFunction.parameterTypes.__len__()))
                allPermutations = list(itertools.permutations(orderedList))

                for i in range(1, iterations):
                    adaptationInstructionBlindPermutation = copy.deepcopy(
                        adaptationInstructionCopy
                    )
                    adaptationInstructionBlindPermutation.identifier = (
                        interfaceMethodName,
                        moduleFunctionQualName,
                        i,
                    )

                    # TODO handling of the case that the same permuation is used as in iteration 0
                    adaptationInstructionBlindPermutation.blindParameterOrderAdaptation = allPermutations[
                        i
                    ]

                    self.adaptations[
                        (interfaceMethodName, moduleFunctionQualName)
                    ].append(adaptationInstructionBlindPermutation)
                    self.adaptationsList.append(adaptationInstructionBlindPermutation)

    def visualizeAdaptations(self) -> None:
        """
        Visualizes all adaptations between the interface methods and the module functions, will only show values after using identifyAdaptations first.
        """
        df = pd.DataFrame(
            columns=list(self.moduleFunctions.keys()),
            index=list(self.interfaceMethods.keys()),
        )

        for key, value in self.adaptations.items():
            interfaceMethodName, moduleFunctionQualName = key
            df.at[interfaceMethodName, moduleFunctionQualName] = value

        print("\n", df, "\n")

    def generateMappings(self, onlyKeepTopN=None):
        """
        Generates all possibilities of implementing the interface methods with the adapted module functions, will only work after using identifyAdaptations first.
        """
        # Generate all possible permutations (with length = number of interface methods) of all adapters of the module functions
        adaptationIdentifiers = (
            adaptationInstruction.identifier
            for adaptationInstruction in self.adaptationsList
        )
        allFunctionPermutations = itertools.permutations(
            adaptationIdentifiers, self.interfaceMethods.keys().__len__()
        )

        for functionPermutation in allFunctionPermutations:
            potentialMapping = Mapping()

            # Try to adapt each module function in the permutation to the corresponding interface method
            for interfaceMethodName in self.interfaceMethods.keys():
                # Iterate through the permutation by taking the first element and removing it from the functionPermutation list
                (interfaceMethodId, moduleFunctionId, iteration) = functionPermutation[
                    0
                ]
                functionPermutation = functionPermutation[1:]

                if (
                    self.adaptations[(interfaceMethodName, moduleFunctionId)] != None
                    and interfaceMethodName == interfaceMethodId
                ):  # NOTE last check ensures that adapter is actually intended for the interfaceMethod
                    # The current module function can be adapted, add it to the potential mapping
                    potentialMapping.adaptationIds.append(
                        (interfaceMethodName, moduleFunctionId, iteration)
                    )
                    potentialMapping.adaptationInfo[interfaceMethodName] = (
                        moduleFunctionId,
                        self.adaptations[(interfaceMethodName, moduleFunctionId)][
                            iteration
                        ],
                    )
                    potentialMapping.totalScore += self.adaptations[
                        (interfaceMethodId, moduleFunctionId)
                    ][iteration].calculateScore()
                else:
                    # At least one module function in the permutation is not adaptable
                    break

            # Check if the potential mapping is complete (i.e. length = number of interface methods)
            if (
                potentialMapping.adaptationIds.__len__()
                == self.interfaceMethods.keys().__len__()
            ):
                self.mappings.append(potentialMapping)

        print(f"Generated {self.mappings.__len__()} potential mappings.")

        self.mappings = sorted(
            self.mappings, key=lambda mapping: mapping.totalScore, reverse=True
        )

        if onlyKeepTopN and onlyKeepTopN <= len(self.mappings):
            print(f"Keeping only the top {onlyKeepTopN} mappings.")
            self.mappings = self.mappings[:onlyKeepTopN]

        for mapping in self.mappings:
            print(mapping)


def create_adapted_module(
    adaptationHandler,
    module_name,
    class_instantiation_params=None,
    use_constructor_default_values=False,
    testing_mode=False,
):
    """
    Creates an adapted module using information provided by the adaptationHandler object. The adapted module can be used to execute stimulus sheets.
    The adapted module comprises multiple submodules (mapping0, mapping1, ...) that contain different sets of adapted functions (terminology: one submodule contains one "mapping").

    Parameters:
    adaptationHandler (AdaptationHandler): The AdaptationHandler object containing all necessary information on how to adapt functions/how many submodules to create.
    module_name (str): The name of the module that is used for importing the module via importlib.
    use_constructor_default_values (bool): If true, the constructor of a class will be instantiated with all available default values instead of explicitly providing these constructor parameters.

    Returns:
    (module: module, successful_mappings: list): A tuple containing the adapted module, and a list of successful Mapping objects.
    """
    # TODO: Auslagern?
    module = importlib.import_module(module_name)
    # print(module.__file__) # print the path of the module

    if testing_mode:
        # Import module from a single file, only for testing
        spec = importlib.util.spec_from_file_location(
            module_name, "./test_data_file.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

    successes = 0
    failed_functions = []
    successful_mappings = []

    for mapping in adaptationHandler.mappings:

        success = True
        print(
            f"\n-----------------------------\nTRYING ADAPTATION FOR MAPPING {mapping}.\n-----------------------------"
        )
        submodule_name = "mapping" + str(successes)
        submodule = types.ModuleType(submodule_name)
        setattr(module, submodule_name, submodule)

        instantiated_classes = {}
        for adaptationId in mapping.adaptationIds:
            interfaceMethodName, moduleFunctionQualName, iteration = adaptationId

            if (moduleFunctionQualName) in failed_functions:
                print(
                    f"Cancelling adaptation for mapping {mapping} as {moduleFunctionQualName} failed previously."
                )
                success = False
                break

            adaptationInstruction = adaptationHandler.adaptations[
                (interfaceMethodName, moduleFunctionQualName)
            ][iteration]

            function = None

            try:
                parent_class_name = adaptationHandler.moduleFunctions[
                    moduleFunctionQualName
                ].parentClass

                # function is a class method that has already been instantiated
                if parent_class_name and parent_class_name in instantiated_classes:
                    print(f"Using already instantiated class {parent_class_name}.")
                    parent_class_instance = instantiated_classes[parent_class_name]

                    # use the simple function name (without the class as prefix) to get the function object
                    simple_function_name = adaptationHandler.moduleFunctions[
                        moduleFunctionQualName
                    ].functionName
                    function = getattr(parent_class_instance, simple_function_name)

                # function is a class method that has not been instantiated yet
                elif parent_class_name:
                    successful_instantiation, parent_class_instance = instantiate_class(
                        module,
                        parent_class_name,
                        class_instantiation_params,
                        use_constructor_default_values,
                        adaptationHandler.classes[parent_class_name],
                    )
                    if successful_instantiation:
                        instantiated_classes[parent_class_name] = parent_class_instance

                        # use the simple function name (without the class as prefix) to get the function object
                        simple_function_name = adaptationHandler.moduleFunctions[
                            moduleFunctionQualName
                        ].functionName
                        function = getattr(parent_class_instance, simple_function_name)
                    else:
                        failed_functions.append(moduleFunctionQualName)
                        print(f"Failed to instantiate class {parent_class_name}.")
                        success = False
                        break

                # function is a standalone function
                else:
                    function = getattr(module, moduleFunctionQualName)

            except Exception as e:
                failed_functions.append(moduleFunctionQualName)
                print(
                    f"For function '{moduleFunctionQualName}' there is an error: {e}."
                )
                success = False
                break
            else:
                # function was found in the module, continue with adaptation: create a submodule that contains the adapted function
                new_function = function
                setattr(
                    submodule, moduleFunctionQualName, new_function
                )  # Add the new function to the submodule

                if adaptationInstruction.areAdaptationsNeeded():

                    new_return_type = None
                    convert_to_types = None
                    new_param_order = None
                    blind_new_param_order = None

                    if adaptationInstruction.returnTypeAdaptation:
                        new_return_type = adaptationInstruction.returnTypeAdaptation
                        print(
                            f"Trying to adapt return type of {new_function} to {new_return_type}."
                        )

                    if adaptationInstruction.parameterTypeConversion:
                        convert_to_types = adaptationInstruction.parameterTypeConversion
                        print(
                            f"Trying to adapt parameter types of {new_function} to {convert_to_types}."
                        )

                    if adaptationInstruction.parameterOrderAdaptation:
                        new_param_order = adaptationInstruction.parameterOrderAdaptation
                        print(f"Trying to adapt parameter order of {new_function}.")

                    if adaptationInstruction.blindParameterOrderAdaptation:
                        blind_new_param_order = (
                            adaptationInstruction.blindParameterOrderAdaptation
                        )
                        print(
                            f"Trying to blindly adapt parameter order of {new_function}."
                        )

                    new_function = adapt_function(
                        new_function,
                        new_return_type,
                        convert_to_types,
                        new_param_order,
                        blind_new_param_order,
                    )

                    if adaptationInstruction.nameAdaptation:
                        setattr(submodule, interfaceMethodName, new_function)
                        print(
                            f"Adapted name of function {new_function} to {interfaceMethodName}."
                        )

        if success:
            print(
                f"{GREEN}Successful creation of submodule {successes} for this mapping.{RESET}"
            )
            successful_mappings.append(mapping)
            successes += 1

    print(f"\n{successes}/{adaptationHandler.mappings.__len__()} adapted mappings.")
    return (module, successful_mappings)


def instantiate_class(
    module, parent_class_name, class_instantiation_params, use_constructor_default_values, constructors
):
    """
    Instantiates a class from a given module.

    Parameters:
    module (module): The module that contains the class to be instantiated, e.g., numpy.
    parent_class_name (str): The name of the class that the function tries to instantiate.
    use_constructor_default_values (bool): If true, the constructor of a class will be instantiated with all available default values instead of explicitly providing these constructor parameters.
    constructors (dict): A dictionary with key = class name and values = list of FunctionSignature objects that represent the constructors of the class.

    Returns:
    (successful_instantiation: bool, parent_class_instance: object): A tuple containing a boolean indicating whether the instantiation was successful and the instance of the parent class.
    """
    print(f"Trying to instantiate class {parent_class_name}.")
    parent_class = getattr(module, parent_class_name)
    parent_class_instance = None
    successful_instantiation = False

    # Try to instantiate the class with user-defined parameters
    if class_instantiation_params:
        print(f"Try instantiation of class {parent_class_name} with user-defined params {class_instantiation_params}.")
        try:
            parent_class_instance = parent_class(*class_instantiation_params)
        except Exception as e:
            print(f"Instantiation of class {parent_class_name} with user-defined params {class_instantiation_params} failed: {e}.")
        else:
            print(f"Successfully instantiated class: {parent_class_instance}.")
            successful_instantiation = True
            return successful_instantiation, parent_class_instance

    # Try to instantiate the class without any parameters
    if constructors.__len__() == 0:
        print(
            f"No constructors found for class {parent_class_name}, trying instantiation call: {parent_class_name}()."
        )
        try:
            parent_class_instance = parent_class()
        except Exception as e:
            print("Standard constructor without params failed: {e}.")
        else:
            print(f"Successfully instantiated class: {parent_class_instance}.")
            successful_instantiation = True
            return successful_instantiation, parent_class_instance

    # Try to instantiate the class with pre-defined values depending on the constructor parameter types
    if constructors.__len__() > 0:
        print(
            f"{constructors.__len__()} constructor(s) found for class {parent_class_name}, try to instantiate with pre-defined values."
        )
        for (
            constructor
        ) in constructors:  # TODO make sure that __new__ is used before __init__

            parameterTypes = constructor.parameterTypes
            print(
                f"Trying constructor {constructor.functionName}, parameter types: {parameterTypes}."
            )

            try:
                if use_constructor_default_values:
                    parameterTypes = parameterTypes[: constructor.firstDefault]
                    print(
                        f"Using default values for constructor parameters, last {len(constructor.parameterTypes) - len(parameterTypes)} parameters were dropped."
                    )

                # Strategy: get standard values for each data type (standard_constructor_values dict) and try to instantiate the class with them, if datatype is unknown use value 1
                parameters = tuple(
                    standard_constructor_values.get(parameterType, 1)
                    for parameterType in parameterTypes
                )

                if parameters.__len__() > 0:
                    print(
                        f"Trying instantiation call: {parent_class_name}({parameters})."
                    )
                    parent_class_instance = parent_class(parameters)
                else:
                    print(f"Trying instantiation call: {parent_class_name}().")
                    parent_class_instance = parent_class()

            except Exception as e:
                print(f"Constructor {constructor.functionName} failed: {e}.")
                continue

            else:
                print(f"Successfully instantiated class: {parent_class_instance}.")
                successful_instantiation = True
                return successful_instantiation, parent_class_instance

    return successful_instantiation, parent_class_instance


def adapt_function(
    function,
    new_return_type=None,
    convert_to_types=None,
    new_param_order=None,
    blind_new_param_order=None,
):
    """
    Adapts a function by using a decorator and wrapper.

    Parameters:
    function (object): The function object to adapt.
    new_return_type (str): A string that represents the new return type of the function.
    convert_to_types (list): A list of strings that represent the target types of the parameters, e.g., ["int", "str", "float"]
    new_param_order (list): A list of strings that represent the new order of parameters, e.g., [1, 2, 0]

    Returns:
    object: The adapted function object.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            result = None
            adapted_args = copy.deepcopy(args)

            # Adapt parameter order in a smart way by matching the parameter types
            if new_param_order:
                try:
                    adapted_args = [adapted_args[i] for i in new_param_order]
                except Exception as e:
                    print(f"Error when adapting parameter order of {function}: {e}.")

            # Adapt parameter order blindly by using a given order TODO this could be merged with the previous step
            if blind_new_param_order:
                try:
                    adapted_args = [adapted_args[i] for i in blind_new_param_order]
                except Exception as e:
                    print(
                        f"Error when blindly adapting parameter order of {function}: {e}."
                    )

            # Adapt parameter types
            if convert_to_types:
                try:
                    target_types = [
                        type_mapping.get(type_name, int)
                        for type_name in convert_to_types
                    ]
                    adapted_args = [
                        target_type(arg)
                        for arg, target_type in zip(adapted_args, target_types)
                    ]
                except Exception as e:
                    print(f"Error when adapting parameter types of {function}: {e}.")

            # Execute the function with potentially adapted parameters
            try:
                result = func(*adapted_args, **kwargs)
            except Exception as e:
                print(f"Executing {function} with adapted args threw an error: {e}.")
                result = func(*args, **kwargs)

            # Adapt return type
            if new_return_type:
                try:
                    result = type_mapping.get(new_return_type, int)(
                        result
                    )  # TODO handling of unknown types, NOTE alternative without type_mapping dict: getattr(builtins, new_return_type)(result)
                except Exception as e:
                    print(f"Error when adapting return type of {function}: {e}.")

            return result

        return wrapper

    print("Created adapted wrapper function.")
    return decorator(function)


standard_constructor_values = {
    "str": "",
    "int": 1,
    "float": 1.0,
    "complex": 1 + 1j,
    "list": [],
    "tuple": (),
    "range": range(1),
    "dict": {},
    "set": set(),
    "fronzenset": frozenset(),
    "bool": True,
    "bytes": b"",
    "bytearray": bytearray(b""),
    "memoryview": memoryview(b""),
    "None": None,
}

type_mapping = {
    "str": str,
    "int": int,
    "float": float,
    "complex": complex,
    "list": list,
    "tuple": tuple,
    "range": range,
    "dict": dict,
    "set": set,
    "fronzenset": frozenset,
    "bool": bool,
    "bytes": bytes,
    "bytearray": bytearray,
    "memoryview": memoryview,
}

possible_conversions = {
    "bool": ["bool", "str", "int", "float", "complex", "range", "bytes", "bytearray"],
    "bytearray": [
        "bytearray",
        "str",
        "list",
        "tuple",
        "dict",
        "set",
        "frozenset",
        "bool",
        "bytes",
        "memoryview",
    ],
    "bytes": [
        "bytes",
        "str",
        "list",
        "tuple",
        "dict",
        "set",
        "frozenset",
        "bool",
        "bytearray",
        "memoryview",
    ],
    "complex": ["complex", "str", "bool"],
    "dict": [
        "dict",
        "str",
        "list",
        "tuple",
        "set",
        "frozenset",
        "bool",
        "bytes",
        "bytearray",
    ],
    "float": ["float", "str", "int", "complex", "bool"],
    "frozenset": [
        "frozenset",
        "str",
        "list",
        "tuple",
        "dict",
        "set",
        "bool",
        "bytes",
        "bytearray",
    ],
    "int": ["int", "str", "float", "complex", "range", "bool", "bytes", "bytearray"],
    "list": [
        "list",
        "str",
        "tuple",
        "dict",
        "set",
        "frozenset",
        "bool",
        "bytes",
        "bytearray",
    ],
    "memoryview": ["memoryview"],
    "range": ["range"],
    "set": [
        "set",
        "str",
        "list",
        "tuple",
        "dict",
        "frozenset",
        "bool",
        "bytes",
        "bytearray",
    ],
    "str": ["str", "list", "tuple", "dict", "set", "frozenset", "bool"],
    "tuple": [
        "tuple",
        "str",
        "list",
        "dict",
        "set",
        "frozenset",
        "bool",
        "bytes",
        "bytearray",
    ],
}


def find_permutation(source, target):
    # Create a dictionary to map each type in the target list to its indices
    target_indices = {}
    for i, t in enumerate(target):
        if t in target_indices:
            target_indices[t].append(i)
        else:
            target_indices[t] = [i]

    # Create the permutation list
    permutation = [0] * len(source)

    # Iterate through the source list and find the corresponding indices
    for i, s in enumerate(source):
        if s in target_indices and target_indices[s]:
            permutation[i] = target_indices[s].pop(0)
        else:
            raise ValueError(f"No matching target type for source type '{s}'")

    return permutation


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
    from execution import execute_test
    from module_parser import parse_code
    from stimulus_sheet_reader import get_stimulus_sheet

    icubed = MethodSignature("icubed", "str", ["int"])
    iminus = MethodSignature("iminus", "str", ["float", "int"])

    interfaceSpecification = InterfaceSpecification("Calculator", [], [icubed, iminus])

    # NOTE adjust this path
    # path = "/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages/numpy/lib/scimath.py" #function_base #user_array #scimath
    # path = "/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages/numpy/matrixlib/defmatrix.py"
    # path = "/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages/numpy/array_api/_array_object.py"
    path = "./test_data_file.py"  # <-- for testing with handcrafted python file
    with open(path, "r") as file:
        file_content = file.read()  # Read the entire content of the file
        moduleUnderTest = parse_code(file_content, "numpy.matrixlib.defmatrix")

    adaptationHandler = AdaptationHandler(
        interfaceSpecification,
        moduleUnderTest,
        excludeClasses=False,
        useFunctionDefaultValues=False,
    )
    adaptationHandler.identifyAdaptations(maxParamPermutationTries=2)
    adaptationHandler.visualizeAdaptations()
    adaptationHandler.generateMappings(onlyKeepTopN=10)

    (adapted_module, successful_mappings) = create_adapted_module(
        adaptationHandler,
        moduleUnderTest.moduleName,
        class_instantiation_params=["1 2; 3 4"],
        use_constructor_default_values=True,
        testing_mode=True,
    )

    stimulus_sheet = get_stimulus_sheet("calc3.csv")
    execute_test(stimulus_sheet, adapted_module, successful_mappings)
