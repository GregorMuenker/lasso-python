import copy
import importlib
import itertools
import math
import types
from collections import Counter
import pandas as pd
import Levenshtein
from collections.abc import Iterable

import sys

sys.path.insert(1, "../../backend")
from constants import (
    GREEN,
    MAGENTA,
    RESET,
    STANDARD_CONSTRUCTOR_VALUES,
    TYPE_MAPPING,
    POSSIBLE_CONVERSIONS,
    LIST_LIKE_TYPES,
)
from sequence_specification import SequenceSpecification


class MethodSignature:
    def __init__(self, methodName: str, returnType: str, parameterTypes: list) -> None:
        self.methodName = methodName
        self.returnType = returnType
        self.parameterTypes = parameterTypes

    def __repr__(self) -> str:
        return f"MethodSignature(methodName={self.methodName}, returnType={self.returnType}, parameterTypes={self.parameterTypes})"


class InterfaceSpecification:
    def __init__(
        self, className: str, constructor: MethodSignature, methods: list
    ) -> None:
        self.className = className
        self.constructor = constructor
        self.methods = methods

    def __repr__(self):
        return f"InterfaceSpecification(className={self.className}, constructor={self.constructor}, methods={self.methods})"


class ModuleUnderTest:
    def __init__(
        self, moduleName: str, functions: list, classConstructors: dict
    ) -> None:
        self.moduleName = moduleName
        self.functions = functions  # List of FunctionSignature objects
        self.classConstructors = classConstructors  # This stores class names (keys) and their constructor (FunctionSignature object)

    def __repr__(self) -> str:
        return (
            f"moduleName='{self.moduleName}',\nfunctions='{self.functions}',\n"
            f"classConstructors={self.classConstructors})"
        )


class FunctionSignature:
    def __init__(
        self,
        functionName: str,
        returnType: str,
        parameterTypes: list,
        parentClass: str,
        firstDefault: int,
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
    def __init__(
        self, interfaceMethodName: str, moduleFunctionQualName: str, iteration: int
    ) -> None:
        self.identifier = (interfaceMethodName, moduleFunctionQualName, iteration)
        self.nameAdaptation = None
        self.returnTypeAdaptation = None
        self.parameterOrderAdaptation = None
        self.blindParameterOrderAdaptation = None
        self.parameterTypeConversion = None
        self.useStandardConstructorValues = None
        self.useEmptyConstructor = None

    def areAdaptationsNeeded(self) -> bool:
        return (
            self.nameAdaptation != None
            or self.returnTypeAdaptation != None
            or self.parameterOrderAdaptation != None
            or self.blindParameterOrderAdaptation != None
            or self.parameterTypeConversion != None
            or self.useStandardConstructorValues != None
        )

    def calculateDistance(self) -> int:
        """
        Calculates the distance between an interface method and a module function by summing up
        - The Levenshtein distance between the method names
        - The number of adaptations needed
        """

        interfaceMethodName = self.identifier[0]
        moduleFunctionName = self.identifier[1]
        if "." in moduleFunctionName:
            moduleFunctionName = moduleFunctionName.split(".")[1]
        nameDistance = Levenshtein.distance(interfaceMethodName, moduleFunctionName)

        adaptations = [
            self.nameAdaptation,
            self.returnTypeAdaptation,
            self.parameterOrderAdaptation,
            self.blindParameterOrderAdaptation,
            self.parameterTypeConversion,
        ]

        needed_adaptations = [
            adaptation for adaptation in adaptations if adaptation is not None
        ]
        return nameDistance + len(needed_adaptations)

    def __repr__(self) -> str:
        result = ""
        if self.nameAdaptation != None:
            result += "Name"
        if self.returnTypeAdaptation != None:
            result += "Rtrn"
        if self.parameterOrderAdaptation != None:
            result += "Perm"
        if self.blindParameterOrderAdaptation != None:
            result += "Perm*"
        if self.parameterTypeConversion != None:
            result += "Convr"
        if self.useStandardConstructorValues != None:
            result += "StandardConstructorValues"
        if self.useEmptyConstructor != None:
            result += "EmptyConstructor"
        return result


class Mapping:
    def __init__(self) -> None:
        self.totalDistance = 0
        self.adaptationIds = (
            []
        )  # list of tuples (interfaceMethodName, moduleFunctionQualName, iteration)
        self.adaptationInfo = (
            {}
        )  # dictionary with key = interfaceMethodName and value = (moduleFunctionQualName, adaptationInstruction)
        self.constructorAdaptations = (
            {}
        )  # key = className, value = adaptationInstruction
        self.functionSignatures = (
            {}
        )  # key = moduleFunctionName, value = FunctionSignature
        self.classNames = set()  # set of class names that are used in the mapping
        self.identifier = None  # The identifier of the mapping, is only set if creation of a submodule was successful

    def __repr__(self) -> str:
        result = ""
        for key, value in self.adaptationInfo.items():
            result += "[" + key + "->" + value[0] + " via " + str(value[1]) + "]"
        result += f" | distance={self.totalDistance}"
        return result


class AdaptationHandler:
    def __init__(
        self,
        interfaceSpecification: InterfaceSpecification,
        moduleUnderTest: ModuleUnderTest,
        excludeClasses=False,
        useFunctionDefaultValues=False,
        maxParamPermutationTries=1,
        typeStrictness=False,
        onlyKeepTopNMappings=None,
        allowStandardValueConstructorAdaptations=True,
    ) -> None:
        """
        The constructor for AdaptationHandler.

        Parameters:
        interfaceSpecification (InterfaceSpecification): Interface specification provided by the user that mainly comprises a list of MethodSignature objects.
        moduleUnderTest (ModuleUnderTest): The parameterized Python module that will be used to implement the interface methods.
        excludeClasses (bool): If true, all functions in the moduleUnderTest with a parent class will be ignored.
        useFunctionDefaultValues (bool): If true, the adaptationHandler will assume that the default parameters of functions will be used with their default values and won't consider them for adaptation.
        maxParamPermutationTries (int): The maximum number of adaptations for any given interface method/module function pair.
        onlyKeepTopNMappings (int): If set, only the top N mappings with the shortest distance will be kept. If not set, all mappings will be kept.
        """

        self.interfaceMethods = {}
        for method in interfaceSpecification.methods:
            self.interfaceMethods[method.methodName] = method

        self.interfaceConstructor = interfaceSpecification.constructor
        if self.interfaceConstructor == None:
            # If no constructor has been specified, use a default constructor with no parameters
            self.interfaceConstructor = MethodSignature("create", "None", [])

        self.moduleFunctions = {}
        for function in moduleUnderTest.functions:
            if function.parentClass != None and excludeClasses == True:
                continue
            self.moduleFunctions[function.qualName] = function
            if useFunctionDefaultValues:
                self.moduleFunctions[function.qualName].parameterTypes = (
                    function.parameterTypes[: function.firstDefault]
                )

        self.classConstructors = {}
        if excludeClasses == False:
            self.classConstructors = moduleUnderTest.classConstructors

        self.adaptations = (
            {}
        )  # key = (interfaceMethodName, moduleFunctionQualName), value = list of adaptationInstruction objects

        self.adaptationsList = (
            []
        )  # List of adaptations is needed to generate mappings later, contains the same adaptationInstruction objects as the adaptations dict

        self.constructorAdaptations = (
            {}
        )  # key = className, value = adaptationInstruction

        self.mappings = (
            []
        )  # list of Mapping objects that is populated by generateMappings()

        self.maxParamPermutationTries = maxParamPermutationTries
        self.typeStrictness = typeStrictness
        self.onlyKeepTopNMappigns = onlyKeepTopNMappings
        self.allowStandardValueConstructorAdaptations = (
            allowStandardValueConstructorAdaptations
        )

    def identifyAdaptations(self) -> None:
        """
        Identifies all possible adaptations between all interface method/module function pairs.
        """
        print(
            f"\n{MAGENTA}--------------------\nIDENTIFY ADAPTATIONS\n--------------------{RESET}"
        )
        for interfaceMethodName, interfaceMethod in self.interfaceMethods.items():
            for moduleFunctionQualName, moduleFunction in self.moduleFunctions.items():

                self.adaptations[(interfaceMethodName, moduleFunctionQualName)] = []

                if (
                    interfaceMethod.parameterTypes.__len__()
                    != moduleFunction.parameterTypes.__len__()
                ):
                    # No adaptation possible as the number of params do not match
                    self.adaptations[(interfaceMethodName, moduleFunctionQualName)] = (
                        None
                    )
                    continue

                adaptationInstruction = AdaptationInstruction(
                    interfaceMethodName, moduleFunctionQualName, 0
                )

                if interfaceMethodName != moduleFunctionQualName:
                    adaptationInstruction.nameAdaptation = interfaceMethodName

                if interfaceMethod.returnType != moduleFunction.returnType:
                    if self.typeStrictness and not can_convert_type(
                        moduleFunction.returnType, interfaceMethod.returnType
                    ):
                        # No adaptation possible as the return types cannot be converted
                        self.adaptations[
                            (interfaceMethodName, moduleFunctionQualName)
                        ] = None
                        continue

                    adaptationInstruction.returnTypeAdaptation = (
                        interfaceMethod.returnType
                    )

                # Create a copy that can be used as a base for blind parameter permutations
                adaptationInstructionCopy = copy.deepcopy(adaptationInstruction)

                if interfaceMethod.parameterTypes != moduleFunction.parameterTypes:
                    if Counter(interfaceMethod.parameterTypes) == Counter(
                        moduleFunction.parameterTypes
                    ):
                        # The number of the parameters is the same, but the order is different => "smart" permutation
                        adaptationInstruction.parameterOrderAdaptation = (
                            find_permutation(
                                interfaceMethod.parameterTypes,
                                moduleFunction.parameterTypes,
                            )
                        )

                    else:
                        if self.typeStrictness and not can_convert_params(
                            interfaceMethod.parameterTypes,
                            moduleFunction.parameterTypes,
                        ):
                            # No adaptation possible as the parameter types cannot be converted
                            self.adaptations[
                                (interfaceMethodName, moduleFunctionQualName)
                            ] = None
                            continue

                        # Store the instruction that types should be converted
                        adaptationInstruction.parameterTypeConversion = (
                            moduleFunction.parameterTypes
                        )

                # Store the adaptationInstruction in the adaptations dict and list
                self.adaptations[(interfaceMethodName, moduleFunctionQualName)].append(
                    adaptationInstruction
                )
                self.adaptationsList.append(adaptationInstruction)

                # Try further permutations without caring about matching types => "blind" parameter permutations
                numOfParamPermutations = math.factorial(
                    moduleFunction.parameterTypes.__len__()
                )
                iterations = min(self.maxParamPermutationTries, numOfParamPermutations)
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

                    # Pick the current permutation and turn it into a list
                    blindPermutation = list(allPermutations[i])

                    # Check if the blind permutation is the same as in iteration 0 (the "smart permutation" that matches param types)
                    if (
                        blindPermutation
                        == adaptationInstruction.parameterOrderAdaptation
                    ):
                        print(
                            f"Blind permutation {blindPermutation} for {interfaceMethodName}->{moduleFunctionQualName} would be a duplicate, skipping it"
                        )

                        # Check if it is possible to use another permutation instead
                        if iterations < numOfParamPermutations:
                            iterations += 1
                            print(f"Trying an additional blind permutation instead")

                        # Don't use this permutation variant and continue with the next iteration
                        continue

                    # The blind permutation is not a duplicate, generate a new adaptation instruction
                    adaptationInstructionBlindPermutation.blindParameterOrderAdaptation = (
                        blindPermutation
                    )

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

        constructorParamsString = ", ".join(
            map(str, self.interfaceConstructor.parameterTypes)
        )
        print(
            f"Constructor adaptations for {self.interfaceConstructor.methodName}({constructorParamsString}):"
        )
        for key, value in self.constructorAdaptations.items():
            print(f"\t{key}: {value}")
        print("")

    def identifyConstructorAdaptations(self) -> bool:
        for className, moduleConstructor in self.classConstructors.items():

            # Class has no constructor, use the empty constructor adaptation strategy
            if moduleConstructor == None:
                adaptationInstruction = AdaptationInstruction(
                    "create", f"None.{className}", 0
                )
                adaptationInstruction.useEmptyConstructor = True
                self.constructorAdaptations[className] = adaptationInstruction
                continue

            adaptationInstruction = AdaptationInstruction(
                "create", moduleConstructor.qualName, 0
            )

            # Set the adaptation strategy to "no adaptations needed, constructors are compatible" by default
            self.constructorAdaptations[className] = "V"

            if (
                self.interfaceConstructor.parameterTypes.__len__()
                != moduleConstructor.parameterTypes.__len__()
            ):
                if not self.allowStandardValueConstructorAdaptations:
                    # No adaptation possible as the parameter types cannot be converted
                    self.constructorAdaptations[className] = None
                else:
                    adaptationInstruction.useStandardConstructorValues = (
                        moduleConstructor.parameterTypes
                    )
                    self.constructorAdaptations[className] = adaptationInstruction

                # Adaptation strategy was either set successfully or constructor is not adaptable, continue with next constructor
                continue

            if (
                self.interfaceConstructor.parameterTypes
                != moduleConstructor.parameterTypes
            ):
                if Counter(self.interfaceConstructor.parameterTypes) == Counter(
                    moduleConstructor.parameterTypes
                ):
                    # The number of the parameters is the same, but the order is different => "smart" permutation
                    adaptationInstruction.parameterOrderAdaptation = find_permutation(
                        self.interfaceConstructor.parameterTypes,
                        moduleConstructor.parameterTypes,
                    )
                    self.constructorAdaptations[className] = adaptationInstruction

                else:
                    if self.typeStrictness and not can_convert_params(
                        self.interfaceConstructor.parameterTypes,
                        moduleConstructor.parameterTypes,
                    ):
                        # No adaptation possible as the parameter types cannot be converted
                        self.constructorAdaptations[className] = None

                    else:
                        # Store the instruction that types should be converted
                        adaptationInstruction.parameterTypeConversion = (
                            moduleConstructor.parameterTypes
                        )
                        self.constructorAdaptations[className] = adaptationInstruction

    def generateMappings(self) -> None:
        """
        Generates all possibilities of implementing the interface methods with the adapted module functions, will only work after using identifyAdaptations() first.
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
                    potentialMapping.totalDistance += self.adaptations[
                        (interfaceMethodId, moduleFunctionId)
                    ][iteration].calculateDistance()
                    potentialMapping.functionSignatures[moduleFunctionId] = (
                        self.moduleFunctions[moduleFunctionId]
                    )

                    # Store class names of classes that are used in this mapping
                    className = self.moduleFunctions[moduleFunctionId].parentClass
                    if className:
                        potentialMapping.classNames.add(className)
                        if self.classConstructors[className] == None:
                            # The constructor of a class that is used in this mapping is not adaptable, break
                            break
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
            self.mappings, key=lambda mapping: mapping.totalDistance, reverse=False
        )

        if self.onlyKeepTopNMappigns and self.onlyKeepTopNMappigns <= len(
            self.mappings
        ):
            print(f"Keeping only the top {self.onlyKeepTopNMappigns} mappings.")
            self.mappings = self.mappings[: self.onlyKeepTopNMappigns]

        for mapping in self.mappings:
            print(mapping)


def create_adapted_module(
    adaptation_handler: AdaptationHandler,
    module_name: str,
    sequence_specification: SequenceSpecification,
    testing_mode: bool = False,
) -> tuple:
    """
    Creates an adapted module using information provided by the AdaptationHandler object. The adapted module can be used to execute stimulus sheets.
    The adapted module comprises multiple submodules (mapping0, mapping1, ...) that contain different sets of adapted functions (terminology: one submodule contains one "mapping").

    Parameters:
    adaptation_handler (AdaptationHandler): The AdaptationHandler object containing all necessary information on how to adapt functions/how many submodules to create.
    module_name (str): The name of the module that is used for importing the module via importlib.
    sequence_specification (SequenceSpecification): The SequenceSpecification object that represents the sequence sheet to be executed using this module.

    Returns:
    (module: module, successful_mappings: List[Mapping]): A tuple containing the adapted module, and a list of successful Mapping objects.
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

    class_instantiation_params = sequence_specification.statements[0].inputParams

    for mapping in adaptation_handler.mappings:

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

            adaptationInstruction = adaptation_handler.adaptations[
                (interfaceMethodName, moduleFunctionQualName)
            ][iteration]

            function = None

            try:
                parent_class_name = adaptation_handler.moduleFunctions[
                    moduleFunctionQualName
                ].parentClass

                # function is a class method that has already been instantiated
                if parent_class_name and parent_class_name in instantiated_classes:
                    print(f"Using already instantiated class {parent_class_name}.")
                    parent_class_instance = instantiated_classes[parent_class_name]

                    # use the simple function name (without the class as prefix) to get the function object
                    simple_function_name = adaptation_handler.moduleFunctions[
                        moduleFunctionQualName
                    ].functionName
                    function = getattr(parent_class_instance, simple_function_name)

                # function is a class method that has not been instantiated yet
                elif parent_class_name:
                    successful_instantiation, parent_class_instance = instantiate_class(
                        module,
                        parent_class_name,
                        class_instantiation_params,
                        adaptation_handler.constructorAdaptations[parent_class_name],
                        adaptation_handler.classConstructors[parent_class_name],
                    )
                    if successful_instantiation:
                        instantiated_classes[parent_class_name] = parent_class_instance

                        # use the simple function name (without the class as prefix) to get the function object
                        simple_function_name = adaptation_handler.moduleFunctions[
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
            mapping.identifier = successes
            successful_mappings.append(mapping)
            successes += 1

    print(f"\n{successes}/{adaptation_handler.mappings.__len__()} adapted mappings.")
    return (module, successful_mappings)


def instantiate_class(
    module: object,
    parent_class_name: str,
    class_instantiation_params: list,
    adaptation_instruction: AdaptationInstruction,
    constructor: FunctionSignature,
) -> tuple:
    """
    Instantiates a class from a given module.

    Parameters:
    module (module): The module that contains the class to be instantiated, e.g., numpy.
    parent_class_name (str): The name of the class that the function tries to instantiate.
    adaptation_instruction (AdaptationInstruction): Instructions on how to adapt the parameters for the constructor call.
    constructors (dict): A dictionary with key = class name and value = FunctionSignature object that represents the constructor of the class.

    Returns:
    (successful_instantiation: bool, parent_class_instance: object): A tuple containing a boolean indicating whether the instantiation was successful and the instance of the parent class.
    """
    print(f"Trying to instantiate class {parent_class_name}.")
    parent_class = getattr(module, parent_class_name)
    parent_class_instance = None
    successful_instantiation = False

    use_empty_constructor = adaptation_instruction.useEmptyConstructor
    new_param_order = adaptation_instruction.parameterOrderAdaptation
    convert_to_types = adaptation_instruction.parameterTypeConversion
    use_standard_constructor_values = (
        adaptation_instruction.useStandardConstructorValues
    )

    # Create a copy to possibly use the original parameters later
    class_instantiation_params_copy = copy.deepcopy(class_instantiation_params)

    if use_empty_constructor:
        class_instantiation_params = []

    if new_param_order != None:
        class_instantiation_params = [
            class_instantiation_params[i] for i in new_param_order
        ]

    if convert_to_types != None:
        for index, type_name in enumerate(convert_to_types):
            if type_name == "Any":
                continue

            target_type = TYPE_MAPPING.get(type_name, None)

            if target_type == None:
                raise TypeError(
                    f"Parameter type conversion: the type '{type_name}' is unknown"
                )

            if (
                not isinstance(class_instantiation_params[index], Iterable)
                and target_type in LIST_LIKE_TYPES
            ):
                class_instantiation_params[index] = target_type(
                    [class_instantiation_params[index]]
                )
            else:
                class_instantiation_params[index] = target_type(
                    class_instantiation_params[index]
                )

    if use_standard_constructor_values != None:
        parameterTypes = constructor.parameterTypes
        print(f"Constructor signature: {constructor.functionName}({parameterTypes}).")

        parameterTypes = parameterTypes[: constructor.firstDefault]
        print(
            f"Using default values for constructor parameters, last {len(constructor.parameterTypes) - len(parameterTypes)} parameters were dropped."
        )

        # Strategy: get standard values for each data type (standard_constructor_values dict) and try to instantiate the class with them, if datatype is unknown use value 1
        class_instantiation_params = tuple(
            STANDARD_CONSTRUCTOR_VALUES.get(parameterType, 1)
            for parameterType in parameterTypes
        )

    # Try to call the instructor with the adapted parameters
    try:
        if class_instantiation_params.__len__() > 0:
            print(
                f"Trying instantiation call: {parent_class_name}({class_instantiation_params})."
            )
            parent_class_instance = parent_class(*class_instantiation_params)
        else:
            print(f"Trying instantiation call: {parent_class_name}().")
            parent_class_instance = parent_class()

    except Exception as e:
        print(f"Constructor {constructor.functionName} failed: {e}.")

    else:
        print(f"Successfully instantiated class: {parent_class_instance}.")
        successful_instantiation = True

    # If nothing succeeded, try to instantiate the class without adaptations
    if not successful_instantiation:
        try:
            if class_instantiation_params.__len__() > 0:
                print(
                    f"Trying instantiation call without adaptations: {parent_class_name}({class_instantiation_params_copy})."
                )
                parent_class_instance = parent_class(*class_instantiation_params_copy)
            else:
                print(
                    f"Trying instantiation call without adaptations: {parent_class_name}()."
                )
                parent_class_instance = parent_class()
        except Exception as e:
            print(f"Constructor without adaptations failed: {e}.")
        else:
            successful_instantiation = True

    return successful_instantiation, parent_class_instance


def adapt_function(
    function: object,
    new_return_type=None,
    convert_to_types=None,
    new_param_order=None,
    blind_new_param_order=None,
) -> object:
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
            adapted_args = list(copy.deepcopy(args))

            # Adapt parameter order in a smart way by matching the parameter types
            if new_param_order != None:
                adapted_args = [adapted_args[i] for i in new_param_order]

            # Adapt parameter order blindly by using a given order
            if blind_new_param_order != None:
                adapted_args = [adapted_args[i] for i in blind_new_param_order]

            # Adapt parameter types
            if convert_to_types != None:
                for index, type_name in enumerate(convert_to_types):
                    if type_name == "Any":
                        continue

                    target_type = TYPE_MAPPING.get(type_name, None)

                    if target_type == None:
                        raise TypeError(
                            f"Parameter type conversion: the type '{type_name}' is unknown"
                        )

                    if (
                        not isinstance(adapted_args[index], Iterable)  # TODO fix this
                        and target_type in LIST_LIKE_TYPES
                    ):
                        adapted_args[index] = target_type([adapted_args[index]])
                    else:
                        adapted_args[index] = target_type(adapted_args[index])

            # Execute the function with potentially adapted parameters
            result = func(*adapted_args, **kwargs)

            # Adapt return type
            if new_return_type != None and new_return_type != "Any":
                conversion_type = TYPE_MAPPING.get(new_return_type, None)

                if conversion_type == None:
                    raise TypeError(f"The return type '{new_return_type}' is unknown")

                if (
                    not isinstance(result, Iterable)
                    and conversion_type in LIST_LIKE_TYPES
                ):
                    result = conversion_type([result])
                else:
                    result = conversion_type(result)

            return result

        return wrapper

    print("Created adapted wrapper function.")
    return decorator(function)


def find_permutation(source: list, target: list) -> list:
    """
    Finds a permutation of a source list, such that the order of the types exactly matches the target list.

    Returns:
    list: A list that represents the permutation instruction to adapt the source list to the target list.
    """
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


def can_convert_params(source_types: list, target_types: list) -> bool:
    if len(source_types) != len(target_types):
        return False

    for source, target in zip(source_types, target_types):
        # Check if conversion is possible
        if target not in POSSIBLE_CONVERSIONS.get(source, []):
            return False

    return True


def can_convert_type(source_type: str, target_type: str) -> bool:
    return target_type in POSSIBLE_CONVERSIONS.get(source_type, [])


if __name__ == "__main__":
    from execution import execute_test
    from module_parser import parse_code
    from sequence_specification import SequenceSpecification

    icubed = MethodSignature("icubed", "Any", ["list"])
    iminus = MethodSignature("iminus", "float", ["float", "int"])
    iconstructor = MethodSignature("create", "None", ["int", "int"])

    interfaceSpecification = InterfaceSpecification(
        "Calculator", iconstructor, [icubed, iminus]
    )

    sequenceSpecification = SequenceSpecification("calc3_adaptation.xlsx")
    print(sequenceSpecification.sequenceSheet)

    # NOTE adjust this path
    # path = "/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages/numpy/lib/scimath.py"  # function_base #user_array #scimath
    # path = "/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages/numpy/matrixlib/defmatrix.py"
    # path = "/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages/numpy/array_api/_array_object.py"
    path = "./test_data_file.py"  # <-- for testing with handcrafted python file
    with open(path, "r") as file:
        file_content = file.read()  # Read the entire content of the file
        moduleUnderTest = parse_code(file_content, "numpy.lib.scimath")

    adaptationHandler = AdaptationHandler(
        interfaceSpecification,
        moduleUnderTest,
        excludeClasses=False,
        useFunctionDefaultValues=False,
        maxParamPermutationTries=2,
        typeStrictness=False,
        onlyKeepTopNMappings=10,
        allowStandardValueConstructorAdaptations=True,
    )
    adaptationHandler.identifyAdaptations()
    adaptationHandler.identifyConstructorAdaptations()
    adaptationHandler.visualizeAdaptations()
    adaptationHandler.generateMappings()

    (adapted_module, successful_mappings) = create_adapted_module(
        adaptationHandler,
        moduleUnderTest.moduleName,
        sequenceSpecification,
        testing_mode=True,
    )

    allSequenceExecutionRecords = execute_test(
        sequenceSpecification,
        adapted_module,
        successful_mappings,
        interfaceSpecification,
    )
    for sequenceExecutionRecord in allSequenceExecutionRecords:
        print(sequenceExecutionRecord)
