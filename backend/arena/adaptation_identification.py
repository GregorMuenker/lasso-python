import copy
import itertools
import math
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
        if self.areAdaptationsNeeded():
            result = ""
            if self.nameAdaptation != None:
                result += "Name"
            if self.returnTypeAdaptation != None:
                result += "Return"
            if self.parameterOrderAdaptation != None:
                result += "Perm"
            if self.blindParameterOrderAdaptation != None:
                result += "Perm*"
            if self.parameterTypeConversion != None:
                result += "Paramconvert"
            if self.useStandardConstructorValues != None:
                result += "StandardConstructorValues"
            if self.useEmptyConstructor != None:
                result += "EmptyConstructor"
            return result
        else:
            return "NoAdapter"


class Mapping:
    def __init__(self) -> None:
        """
        Creates an empty Mapping object that can be populated with adaptation information.
        """
        
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
        self.identifier = None  # The identifier of the mapping
        self.successful = False # Whether a submodule was successfully created for this mapping using 

    def __repr__(self) -> str:
        result = ""
        for key, value in self.adaptationInfo.items():
            result += "[" + key + "->" + value[0] + " via " + str(value[1]) + "]"
        for key, value in self.constructorAdaptations.items():
            result += "[create " + key + " via " + str(value) + "]"
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
        The constructor for creating an AdaptationHandler object.

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
                    # It is important to compare the qualName, not just the simple function name
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

            # Set the adaptation strategy to empty instructions (i.e., no adaptations needed, constructors are compatible) by default
            self.constructorAdaptations[className] = adaptationInstruction

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

                    # Check if the function has a parent class, if so, check if the class is adaptable
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
                # Add constructor adaptations to the potential mapping
                for className in potentialMapping.classNames:
                    potentialMapping.constructorAdaptations[className] = self.constructorAdaptations[className]
                
                # Add the mapping to the list of mappings
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

        for index, mapping in enumerate(self.mappings):
            mapping.identifier = index
            print(mapping)


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
    from execution import execute_test, ExecutionEnvironment
    from module_parser import parse_code
    from sequence_specification import SequenceSpecification
    from adaptation_implementation import create_adapted_module

    icubed = MethodSignature("icubed", "set", ["int"])
    iminus = MethodSignature("iminus", "float", ["float", "int"])
    iconstructor = MethodSignature("create", "None", [])

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

    executionEnvironment = ExecutionEnvironment(adaptationHandler.mappings, sequenceSpecification, interfaceSpecification)

    adapted_module = create_adapted_module(
        adaptationHandler,
        moduleUnderTest.moduleName,
        executionEnvironment,
        testing_mode=True,
    )

    execute_test(
        adapted_module,
        executionEnvironment
    )

    executionEnvironment.printResults()
    
