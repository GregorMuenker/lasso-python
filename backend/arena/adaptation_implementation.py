import copy
import types
from collections.abc import Iterable
import coverage
import inspect
import os
import time
import io
import json
import warnings

import sys
import git
repo = git.Repo(search_parent_directories=True)
sys.path.insert(0, repo.working_tree_dir)
from backend.constants import (
    GREEN,
    RESET,
    STANDARD_CONSTRUCTOR_VALUES,
    TYPE_MAPPING,
    LIST_LIKE_TYPES,
)
from backend.arena.adaptation_identification import (
    AdaptationHandler,
    AdaptationInstruction,
    FunctionSignature,
)
from backend.arena.execution import (
    ExecutionEnvironment,
    SequenceExecutionRecord,
    RowRecord,
    Metrics,
)
from backend.arena.sequence_specification import Statement


def create_adapted_submodule(
    adaptation_handler: AdaptationHandler,
    module: object,
    execution_environment: ExecutionEnvironment,
    submodule_id: int,
    statement: Statement,
) -> tuple:
    """
    Creates an adapted submodule using information provided by the AdaptationHandler object. The adapted module can be used to execute stimulus sheets.
    The adapted submodule contains a set of adapted functions.

    Parameters:
    adaptation_handler (AdaptationHandler): The AdaptationHandler object containing all necessary information on how to adapt functions/how many submodules to create.
    module_name (object): The module used for execution.
    execution_environment (ExecutionEnvironment): The ExecutionEnvironment object that configures this execution.
    submodule_id (int): Identifier of the submodule
    import_from_file_path (str): A path for importing a module pointing to a file for testing purposes.

    Returns:
    tuple: The full module (including the submodule), the adapted submodule, and the instance of the parent class (if applicable).
    """

    failed_functions = []
    mapping = adaptation_handler.mappings[submodule_id]

    # Keep track if there occurs an error => if yes, the mapping is not successful
    no_error = True
    print(
        f"\n---------------------------------\nTRYING IMPLEMENTATION FOR MAPPING\n---------------------------------\n{mapping}."
    )
    submodule_name = "mapping" + str(submodule_id)
    submodule = types.ModuleType(submodule_name)

    instantiated_classes = {}
    parent_class_instance = None
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
                    class_constructor = adaptation_handler.classConstructors[
                        parent_class_name
                    ]
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
                    statement,
                    adaptation_handler.constructorAdaptations[parent_class_name],
                    class_constructor,
                    execution_environment.getSequenceExecutionRecord(mapping),
                    execution_environment.recordMetrics,
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
            print(f"For function '{moduleFunctionQualName}' there is an error: {e}.")
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
                    print(f"Trying to blindly adapt parameter order of {new_function}.")

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
            f"{GREEN}Successful creation of submodule {submodule_id} for this mapping.{RESET}"
        )
        mapping.successful = True

    return (module, submodule, parent_class_instance)


def instantiate_class(
    module: object,
    parent_class_name: str,
    statement: Statement,
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

    class_instantiation_params = statement.inputParams
    # Create a copy to possibly use the original parameters later
    original_class_instantiation_params = list(
        copy.deepcopy(class_instantiation_params)
    )

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

        # Strategy: get standard values for each data type (standard_constructor_values dict) and try to instantiate the class with them, if datatype is unknown use value 1
        class_instantiation_params = tuple(
            STANDARD_CONSTRUCTOR_VALUES.get(parameterType, 1)
            for parameterType in parameterTypes
        )

        # Retrospectively update the adaptation instruction
        adaptation_instruction.useStandardConstructorValues = class_instantiation_params

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
            filename = os.path.abspath(
                filename
            )  # NOTE: Using the absolute path is neccessary as a relative path will mess up the coverage report

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
    constructor_name = (
        constructor.qualName if constructor else f"{parent_class_name}.None"
    )  # Account for the situation that the class has no constructor, i.e. the constructor is None
    row_record = RowRecord(
        position=statement.position,
        methodName="create",
        originalFunctionName=constructor_name,
        inputParams=original_class_instantiation_params,
        instanceParam=parent_class_name,
        adaptationInstruction=adaptation_instruction,
    )
    row_record.metrics = metrics

    if successful_instantiation:
        row_record.returnValue = parent_class_instance
    else:
        row_record.returnValue = "UNSUCCESSFUL"
        row_record.errorMessage = "Could not instantiate class"

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

    # Get the coverage report (outfile="-" -> report is written to stdout). Warnings from coverage have to be catched to avoid termination
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")  # Always trigger the warning for capture

        # Attempt to get json_report
        try:
            cov.json_report(outfile="-")
        except Exception as e:
            print(f"Error with getting coverage report: {e}")

        # Check if any warnings were raised
        for warning in w:
            print(f"Coverage warning: {warning.message}")

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
