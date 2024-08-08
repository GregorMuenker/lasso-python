import ast
import inspect
import os
import time

import coverage
from constants import BLUE, CYAN, GREEN, MAGENTA, RED, RESET, YELLOW


class ExecutionRecord:
    def __init__(self) -> None:
        self.methodName = None
        self.inputParams = None
        self.x = None
        self.y = None
        self.returnValue = None
        self.metrics = None

    def __repr__(self) -> str:
        inputParamsString = ", ".join(map(str, self.inputParams))
        instruction = f"{self.methodName}({inputParamsString})"
        return f"{YELLOW}{instruction}: {self.returnValue}{RESET}, {self.metrics}"


def execute_test(stimulus_sheet, adapted_module, mappings) -> None:
    """
    Executes a stimulus sheet based on a provided module and prints out the results.

    Parameters:
    stimulus_sheet (pandas.DataFrame): The stimulus sheet that contains the instructions for the test.
    adapted_module (module): The module that contains the adapted functions in 1 or more submodules (mapping1, mapping2, ...).
    number_of_submodules (int): The number of submodules in the adapted module.
    mappings (list): A list of mappings containing metadata for each mapping.
    """

    print(
        f"\n{CYAN}----------------------\nEXECUTE STIMULUS SHEET\n----------------------{RESET}"
    )
    print(f"Module: {adapted_module.__name__}")
    print(f"\n {stimulus_sheet}\n")

    stimulus_sheet_id = 0  # TODO refine this identifier

    for i in range(len(mappings)):
        submodule = getattr(adapted_module, "mapping" + str(i))

        # Prepare an empty list where ExecutionRecord objects will be stored
        mappings[i].executions[stimulus_sheet_id] = []

        for index, row in stimulus_sheet.iterrows():
            method_name = row["method_name"]
            input_params = row["input_params"]

            executionRecord = ExecutionRecord()
            executionRecord.methodName = method_name
            executionRecord.inputParams = input_params
            executionRecord.x = 2
            executionRecord.y = index

            input_params_string = ", ".join(map(str, input_params))
            instruction = f"{method_name}({input_params_string})"

            method = None
            try:
                method = getattr(submodule, method_name)
            except Exception as e:
                print(
                    f"Error when trying to get method {method_name} from submodule {submodule}. Error: {e}"
                )
                executionRecord.returnValue = "Method not found"
                continue

            # Needed for the metrics
            original_function_name, adaptationInstruction = mappings[i].adaptationInfo[
                method_name
            ]
            executable_statements = get_executable_statements(
                original_function_name, adapted_module
            )

            return_value = "Error"
            metrics = "No metrics recorded"
            try:
                filename = inspect.getfile(adapted_module)
                filename = os.path.abspath(
                    filename
                )  # NOTE: This is neccessary as a relative path will mess up the coverage report

                cov = coverage.Coverage(source=[adapted_module.__name__], branch=True)
                return_value, metrics = run_with_metrics(
                    method, input_params, executable_statements, filename, cov
                )
            except Exception as e:
                print(f"Error when executing instruction: {instruction}: {e}")

            # Fill in the results for this execution
            executionRecord.returnValue = return_value
            executionRecord.metrics = metrics
            mappings[i].executions[stimulus_sheet_id].append(executionRecord)

    # Printing the results
    counter = 0
    for mapping in mappings:
        print(f"{counter} {mapping}\t")
        for execution in mapping.executions[stimulus_sheet_id]:
            print(f"\t{execution}")
        counter += 1


def get_executable_statements(original_function_name, module) -> set:
    """
    Returns a set of line numbers that contain executable statements in the original function, i.e. the lines that are not comments/whitespaces/etc.
    """
    original_function = None
    if "." in original_function_name:
        # split_qualname = original_function_name.split(".")
        # original_class = getattr(module, split_qualname[0])
        # original_function = getattr(original_class, split_qualname[1])
        # TODO Return empty set of covered lines as Python does not support inspect.getsource for class methods, see: https://github.com/python/cpython/issues/116987
        return set()
    else:
        original_function = getattr(module, original_function_name)

    lines, start_line = inspect.getsourcelines(original_function)

    # Join the lines into a single string and parse
    source_code = "".join(lines)
    tree = ast.parse(source_code)

    executable_statements = set()

    for node in ast.walk(tree):
        # Check if the node has a lineno attribute (indicating it's an executable statement)
        if hasattr(node, "lineno"):
            # Adjust the line number to be relative to the file
            line_number = node.lineno + start_line - 1
            executable_statements.add(line_number)

    # Find the line number of the function definition and discard lines before it including the function signature
    for index, line in enumerate(lines):
        if line.strip().startswith("def "):
            function_signature_line = start_line + index
            break

    for line_no in range(start_line, function_signature_line + 1):
        executable_statements.discard(line_no)

    return executable_statements


def run_with_metrics(function, args, executable_statements, filename, cov) -> tuple:
    """
    Executes a function and records the code coverage and arc coverage metrics.
    """
    cov.start()
    start_time = time.time()
    result = function(*args)
    end_time = time.time()
    execution_time = end_time - start_time
    cov.stop()

    data = cov.get_data()
    covered_lines = data.lines(filename)

    arcs = data.arcs(filename)
    covered_arcs = []

    if arcs and covered_lines:
        covered_arcs = [
            arc for arc in arcs if arc[0] in covered_lines or arc[1] in covered_lines
        ]

    if len(executable_statements) == 0:
        # If the function is a class method, we cannot get the source code and therefore cannot get the executable statements
        return result, f"Time: {execution_time:.5f}s. Lines: {len(covered_lines)} total."

    if covered_lines:
        covered_by_function = set(covered_lines) & set(executable_statements)

    covered_arcs_in_function = []
    if arcs:
        covered_arcs_in_function = [
            arc
            for arc in arcs
            if arc[0] in covered_by_function or arc[1] in covered_by_function
        ]

    metrics = f"Time: {execution_time:.5f}s. "
    if covered_lines:
        metrics += f"Lines: {len(covered_lines)} total, {len(covered_by_function)}/{len(executable_statements)} in function."
    if arcs:
        metrics += f"Arcs: {len(covered_arcs)} total, {len(covered_arcs_in_function)} in function."

    return (result, metrics)
