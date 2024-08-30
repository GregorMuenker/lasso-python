from adaptation_identification import (
    AdaptationHandler,
    AdaptationInstruction,
    FunctionSignature,
)
from execution import ExecutionEnvironment, SequenceExecutionRecord, RowRecord, Metrics
import copy
import importlib
import types
from collections.abc import Iterable
import coverage
import inspect
import os
import time
import io
import json
import sys
sys.path.insert(1, "../../backend")
from constants import (
    GREEN,
    RESET,
    STANDARD_CONSTRUCTOR_VALUES,
    TYPE_MAPPING,
    LIST_LIKE_TYPES,
)


def create_adapted_module(
    adaptation_handler: AdaptationHandler,
    module_name: str,
    execution_environment: ExecutionEnvironment,
    testing_mode: bool = False,
) -> tuple:
    """
    Creates an adapted module using information provided by the AdaptationHandler object. The adapted module can be used to execute stimulus sheets.
    The adapted module comprises multiple submodules (mapping0, mapping1, ...) that contain different sets of adapted functions (terminology: one submodule contains one "mapping").

    Parameters:
    adaptation_handler (AdaptationHandler): The AdaptationHandler object containing all necessary information on how to adapt functions/how many submodules to create.
    module_name (str): The name of the module that is used for importing the module via importlib.
    execution_environment (ExecutionEnvironment): The ExecutionEnvironment object that configures this execution.
    testing_mode (bool): A flag that indicates whether the module should be imported from a single file for testing purposes.

    Returns:
    module (object): The adapted module.
    """
    # TODO: Auslagern?
    module = importlib.import_module(module_name)

    record_metrics = True # TODO put this as configuration variable in ExecutionEnvironment

    if testing_mode:
        # Import module from a single file, only for testing
        spec = importlib.util.spec_from_file_location(
            module_name, "./test_data_file.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

    successes = 0
    failed_functions = []

    class_instantiation_params = execution_environment.sequenceSpecification.statements[0].inputParams

    for index, mapping in enumerate(adaptation_handler.mappings):
        
        # Keep track if there occurs an error => if yes, the mapping is not successful
        no_error = True
        print(
            f"\n-----------------------------\nTRYING ADAPTATION FOR MAPPING\n-----------------------------\n{mapping}."
        )
        submodule_name = "mapping" + str(index)
        submodule = types.ModuleType(submodule_name)
        setattr(module, submodule_name, submodule)

        instantiated_classes = {}
        for adaptationId in mapping.adaptationIds:
            interfaceMethodName, moduleFunctionQualName, iteration = adaptationId

            if (moduleFunctionQualName) in failed_functions:
                print(
                    f"Cancelling adaptation for mapping {mapping} as {moduleFunctionQualName} failed previously."
                )
                no_error = False
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
                    if adaptation_handler.classConstructors[parent_class_name]:
                        class_constructor = adaptation_handler.classConstructors[parent_class_name]
                    else:
                        # Generate a dummy constructor if the class has no constructor
                        class_constructor = FunctionSignature(
                            functionName="None",
                            returnType="Any",
                            parameterTypes=[],
                            parentClass=parent_class_name,
                            firstDefault=0,
                        )

                    successful_instantiation, parent_class_instance = instantiate_class(
                        module,
                        parent_class_name,
                        class_instantiation_params,
                        adaptation_handler.constructorAdaptations[parent_class_name],
                        class_constructor,
                        execution_environment.getSequenceExecutionRecord(mapping),
                        record_metrics
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
                        no_error = False
                        break

                # function is a standalone function
                else:
                    function = getattr(module, moduleFunctionQualName)

            except Exception as e:
                failed_functions.append(moduleFunctionQualName)
                print(
                    f"For function '{moduleFunctionQualName}' there is an error: {e}."
                )
                no_error = False
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

        if no_error:
            print(
                f"{GREEN}Successful creation of submodule {index} for this mapping.{RESET}"
            )
            mapping.successful = True
            successes += 1

    print(f"\n{successes}/{adaptation_handler.mappings.__len__()} adapted mappings.")
    return module


def instantiate_class(
    module: object,
    parent_class_name: str,
    class_instantiation_params: list,
    adaptation_instruction: AdaptationInstruction,
    constructor: FunctionSignature,
    sequence_execution_record: SequenceExecutionRecord,
    record_metrics: bool,
) -> tuple:
    """
    Instantiates a class from a given module.

    Parameters:
    module (module): The module that contains the class to be instantiated, e.g., numpy.
    parent_class_name (str): The name of the class that the function tries to instantiate.
    adaptation_instruction (AdaptationInstruction): Instructions on how to adapt the parameters for the constructor call.
    constructor (FunctionSignature): FunctionSignature object that represents the constructor of the class.
    sequence_execution_record (SequenceExecutionRecord): The sequence execution record that is used to store the results of the constructor call.

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
    original_class_instantiation_params = list(copy.deepcopy(class_instantiation_params))

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
    
    # Instantiate empty Metrics object
    metrics = Metrics()

    # Try to call the instructor with the potentially adapted parameters
    try:
        if not record_metrics or use_empty_constructor:
            print(
                f"Trying instantiation call (no metrics): {parent_class_name}({class_instantiation_params})."
            )
            parent_class_instance = parent_class(*class_instantiation_params)
        else:
            print(
                f"Trying instantiation call with metrics: {parent_class_name}({class_instantiation_params})."
            )

            filename = inspect.getfile(module)
            filename = os.path.abspath(filename) # NOTE: Using the absolute path is neccessary as a relative path will mess up the coverage report
            
            cov = coverage.Coverage(source=[module.__name__], branch=True)
            
            parent_class_instance, metrics = run_constructor_with_metrics(
                parent_class,
                class_instantiation_params,
                filename,
                cov,
                constructor.qualName,
            )

    except Exception as e:
        print(f"Constructor {constructor} failed: {e}.")

    else:
        print(f"Successfully instantiated class: {parent_class_instance}.")
        successful_instantiation = True

    # If nothing succeeded, try to instantiate the class without adaptations
    if not successful_instantiation:
        try:
            print(
                f"Trying instantiation call without adaptations (no metrics): {parent_class_name}({original_class_instantiation_params})."
            )
            parent_class_instance = parent_class(*original_class_instantiation_params)
        except Exception as e:
            print(f"Constructor without adaptations failed: {e}.")
        else:
            adaptation_instruction.clear()
            successful_instantiation = True

    # Generate RowRecord for the constructor call
    constructor_name = constructor.qualName if constructor else f"{parent_class_name}.None" # Account for the situation that the class has no constructor, i.e. the constructor is None
    row_record = RowRecord(position=0, methodName="create", originalFunctionName=constructor_name, inputParams=original_class_instantiation_params)
    row_record.metrics = metrics

    if successful_instantiation:
        row_record.returnValue = str(parent_class_instance)
    else:
        row_record.returnValue = "Error"
    sequence_execution_record.rowRecords.append(row_record)

    return successful_instantiation, parent_class_instance


def run_constructor_with_metrics(
    parent_class: object,
    args: list,
    filename: str,
    cov: object,
    original_function_name: str,
):
    metrics = Metrics()

    cov.start()
    start_time = time.time()
    result = parent_class(*args)
    end_time = time.time()
    cov.stop()

    execution_time = int((end_time - start_time) * 1_000_000)  # Convert to microseconds
    metrics.executionTime = execution_time

    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout

    # Get the coverage report (outfile="-" -> report is written to stdout)
    cov.json_report(outfile="-")

    # Capture the output and reset stdout
    output = new_stdout.getvalue()
    sys.stdout = old_stdout

    json_output = None
    try:
        json_output = json.loads(output)
    except Exception as e:
        print("Error when trying to parse coverage report, skipping further metrics", e)
        return (result, metrics)

    # Some logic for finding coverage data in the json output
    file_data = None
    file_data_found = False
    try:
        file_data = json_output["files"][filename]
    except:
        print(f"Coverage.py file data not found for {filename}, trying file name only")
    else:
        file_data_found = True

    if not file_data_found:
        try:
            file_data = json_output["files"][os.path.basename(filename)]
        except:
            # If the file data is still not found, return the result and the metrics object with only the execution time
            print(
                f"Coverage.py file data not found for {filename}, skipping further metrics"
            )
            return (result, metrics)
        else:
            print("Coverage.py file data found for file name only")
            file_data_found = True

    metrics.allLinesInFile = file_data["summary"]["num_statements"]
    metrics.coveredLinesInFile = file_data["summary"]["covered_lines"]

    metrics.allLinesInFunction = file_data["functions"][original_function_name]["summary"]["num_statements"]
    metrics.coveredLinesInFunction = file_data["functions"][original_function_name]["summary"]["covered_lines"]
    metrics.coveredLinesInFunctionRatio = file_data["functions"][original_function_name]["summary"]["percent_covered"]

    metrics.allBranchesInFile = file_data["summary"]["num_branches"]
    metrics.coveredBranchesInFile = file_data["summary"]["covered_branches"]

    metrics.allBranchesInFunction = file_data["functions"][original_function_name]["summary"]["num_branches"]
    metrics.coveredBranchesInFunction = file_data["functions"][original_function_name]["summary"]["covered_branches"]

    return (result, metrics)


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
                        not isinstance(adapted_args[index], Iterable)
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

    print(
        f"Created adapted wrapper function for {function}: New param order: {new_param_order}, New blind param order: {blind_new_param_order}, Param conversion: {convert_to_types}, Return conversion: {new_return_type}"
    )
    return decorator(function)