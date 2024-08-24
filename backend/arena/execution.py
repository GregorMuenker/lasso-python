import ast
import inspect
import os
import time
import coverage
import datetime

import sys

sys.path.insert(1, "../../backend")
from constants import BLUE, CYAN, GREEN, MAGENTA, RED, RESET, YELLOW
from ignite import CellId, CellValue


class SequenceExecutionRecord:
    def __init__(self, interfaceSpecification, mapping, sequenceSpecification) -> None:
        self.interfaceSpecification = interfaceSpecification
        self.mapping = mapping
        self.sequenceSpecification = sequenceSpecification
        self.rowRecords = (
            {}
        )  # {int: RowRecord}, the int is the y coordinate of the row in the stimulus sheet

    def toSheetCells(self) -> list:
        """
        This method converts the sequence execution record into pairs of (CellId, CellValue) that can be put into the Ignite cache.
        The following type of stats are covered:
        - 'value' (TODO oracle value?),
        - 'op' (operation)
        - 'input_value'
        - metrics
        Not covered
        - 'seq' (Randoop)
        - 'exseq' (Randoop)
        - 'loader.classes_loaded',
        - 'loader.artifacts'

        Returns:
        list: A list of (CellId, CellValue) tuples that represent the cells in the stimulus sheet.
        """
        cells = []
        
        for position, rowRecord in self.rowRecords.items():
            original_function_name, adaptation_instruction = self.mapping.adaptationInfo[rowRecord.methodName]

            # Value
            cellId = CellId(
                EXECUTIONID="",
                ABSTRACTIONID=self.interfaceSpecification.className,
                ACTIONID="",
                ARENAID="execute",
                SHEETID=self.sequenceSpecification.name,
                SYSTEMID="",
                VARIANTID=str(self.mapping.identifier),
                ADAPTERID=str(adaptation_instruction.identifier),
                X=0,
                Y=position,
                TYPE="value",
            )
            cellValue = CellValue(
                VALUE=str(rowRecord.returnValue),
                RAWVALUE=str(rowRecord.returnValue),
                VALUETYPE=str(type(rowRecord.returnValue)),
                LASTMODIFIED=datetime.date.today(),
                EXECUTIONTIME=rowRecord.metrics.executionTime,
            )
            cells.append((cellId, cellValue))

            # Operation
            cellId = CellId(
                EXECUTIONID="",
                ABSTRACTIONID=self.interfaceSpecification.className,
                ACTIONID="",
                ARENAID="execute",
                SHEETID=self.sequenceSpecification.name,
                SYSTEMID="",
                VARIANTID=str(self.mapping.identifier),
                ADAPTERID=str(adaptation_instruction.identifier),
                X=1,
                Y=position,
                TYPE="op",
            )
            cellValue = CellValue(
                VALUE=original_function_name,
                RAWVALUE=original_function_name,
                VALUETYPE="function",
                LASTMODIFIED=datetime.date.today(),
                EXECUTIONTIME=rowRecord.metrics.executionTime,
            )
            cells.append((cellId, cellValue))

            # Input values
            for xPosition, inputParam in enumerate(rowRecord.inputParams):
                cellId = CellId(
                    EXECUTIONID="",
                    ABSTRACTIONID=self.interfaceSpecification.className,
                    ACTIONID="",
                    ARENAID="execute",
                    SHEETID=self.sequenceSpecification.name,
                    SYSTEMID="",
                    VARIANTID=str(self.mapping.identifier),
                    ADAPTERID=str(adaptation_instruction.identifier),
                    X=3+xPosition,
                    Y=position,
                    TYPE="input_value",
                )
                cellValue = CellValue(
                    VALUE=str(inputParam),
                    RAWVALUE=str(inputParam),
                    VALUETYPE=str(type(inputParam)),
                    LASTMODIFIED=datetime.date.today(),
                    EXECUTIONTIME=-1,
                )
                cells.append((cellId, cellValue))

            # Metrics
            cellId = CellId(
                EXECUTIONID="",
                ABSTRACTIONID=self.interfaceSpecification.className,
                ACTIONID="",
                ARENAID="execute",
                SHEETID=self.sequenceSpecification.name,
                SYSTEMID="",
                VARIANTID=str(self.mapping.identifier),
                ADAPTERID=str(adaptation_instruction.identifier),
                X=-1,
                Y=-1,
                TYPE="coverage_ratio",
            )
            cellValue = CellValue(
                VALUE=f"{rowRecord.metrics.coveredLinesInFunctionRatio}%",
                RAWVALUE=f"{rowRecord.metrics.coveredLinesInFunctionRatio}",
                VALUETYPE="percentage",
                LASTMODIFIED=datetime.date.today(),
                EXECUTIONTIME=-1,
            )
            cells.append((cellId, cellValue))

        return cells


    def __repr__(self) -> str:
        result = f"{self.mapping.identifier} {self.mapping}"
        for rowRecord in self.rowRecords.values():
            result += f"\n\t{rowRecord}"
        return f"{result}\n"


class RowRecord:
    def __init__(
        self, position, methodName, originalFunctionName, inputParams, oracleValue=None
    ) -> None:
        self.position = position  # The y coordinate of the row in the stimulus sheet
        self.methodName = methodName
        self.originalFunctionName = originalFunctionName
        self.inputParams = inputParams
        self.oracleValue = oracleValue

        self.returnValue = None
        self.metrics = None

    def __repr__(self) -> str:
        inputParamsString = ", ".join(map(str, self.inputParams))
        instruction = f"{self.methodName}({inputParamsString})"
        return f"{CYAN}{instruction}: {self.returnValue}{RESET}, {self.metrics}"


class Metrics:
    def __init__(self) -> None:
        self.executionTime = None
        self.coveredLinesInFile = None
        self.coveredLinesInFunction = None
        self.coveredLinesInFunctionRatio = None

        self.coveredArcsInFile = None
        self.coveredArcsInFunction = None

    def __repr__(self) -> str:
        return f"Time: {self.executionTime} microseconds. Covered lines: {self.coveredLinesInFile} in file, {self.coveredLinesInFunction} in function ({self.coveredLinesInFunctionRatio}% of function lines). Covered arcs: {self.coveredArcsInFile} in file, {self.coveredArcsInFunction} in function."


def execute_test(sequence_spec, adapted_module, mappings, interface_spec) -> list:
    """
    Executes a stimulus sheet based on a provided module and prints out the results.

    Parameters:
    stimulus_sheet (pandas.DataFrame): The stimulus sheet that contains the instructions for the test.
    adapted_module (module): The module that contains the adapted functions in 1 or more submodules (mapping0, mapping1, ...).
    number_of_submodules (int): The number of submodules in the adapted module.
    mappings (list): A list of mappings containing metadata for each mapping.

    Returns:
    list: A list of SequenceExecutionRecord objects that contain the results for executing each module on the provided stimulus sheet.
    """

    print(
        f"\n{CYAN}----------------------\nEXECUTE STIMULUS SHEET\n----------------------{RESET}"
    )
    print(f"Module: {adapted_module.__name__}")
    print(f"Number of submodules: {len(mappings)}")
    print(f"\n {sequence_spec.stimulusSheet}\n")

    allSequenceExecutionRecords = []

    for i in range(len(mappings)):
        submodule = getattr(adapted_module, "mapping" + str(i))

        sequenceExecutionRecord = SequenceExecutionRecord(
            interfaceSpecification=interface_spec,
            mapping=mappings[i],
            sequenceSpecification=sequence_spec,
        )

        for index, statement in sequence_spec.statements.items():

            # Skip the create statement as it already has been covered during creating the adapted module
            if (statement.methodName == "create"):
                continue

            original_function_name, adaptationInstruction = mappings[i].adaptationInfo[
                statement.methodName
            ]

            rowRecord = RowRecord(
                position=index,
                methodName=statement.methodName,
                originalFunctionName=original_function_name,
                inputParams=statement.inputParams,
                oracleValue=statement.oracleValue,
            )

            # Build the instruction string to output errors in a more readable way
            input_params_string = ", ".join(map(str, statement.inputParams))
            instruction = f"{statement.methodName}({input_params_string})"

            method = None
            try:
                method = getattr(submodule, statement.methodName)
            except Exception as e:
                print(
                    f"Error when trying to get method {statement.methodName} from submodule {submodule}. Error: {e}"
                )
                rowRecord.returnValue = "Method not found"
                continue

            # Needed for the metrics
            executable_statements = get_executable_statements(
                original_function_name, adapted_module
            )

            # Set the return value
            return_value = "Execution unsuccessful"
            metrics = "No metrics recorded"
            try:
                filename = inspect.getfile(adapted_module)
                filename = os.path.abspath(
                    filename
                )  # NOTE: Using the absolute path is neccessary as a relative path will mess up the coverage report

                cov = coverage.Coverage(source=[adapted_module.__name__], branch=True)
                return_value, metrics = run_with_metrics(
                    method, statement.inputParams, executable_statements, filename, cov
                )
            except Exception as e:
                print(
                    f"{RED}{instruction} ({submodule}, {original_function_name}, {adaptationInstruction}) failed{RESET}: {e}"
                )

            # Fill in the results for this execution
            rowRecord.returnValue = return_value
            rowRecord.metrics = metrics

            sequenceExecutionRecord.rowRecords[index] = rowRecord

        allSequenceExecutionRecords.append(sequenceExecutionRecord)

    return allSequenceExecutionRecords


def get_executable_statements(original_function_name, module) -> set:
    """
    Returns a set of line numbers that contain executable statements in the original function, i.e. the lines that are not comments/whitespaces/etc.
    """
    original_function = None
    if "." in original_function_name:
        # split_qualname = original_function_name.split(".")
        # original_class = getattr(module, split_qualname[0])
        # original_function = getattr(original_class, split_qualname[1])
        # NOTE Returning empty set of covered lines here for now
        # Reason: Python 3.9.9 and older does not support inspect.getsource for class methods, see: https://github.com/python/cpython/issues/116987
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

    # Find the line number of the function definition to later discard all lines before it (e.g., @ annotations) and the function signature line itself
    function_signature_line = None
    for index, line in enumerate(lines):
        if line.strip().startswith("def "):
            function_signature_line = start_line + index
            break

    # Discard the function signature line
    if function_signature_line is not None:
        for line_no in range(start_line, function_signature_line + 1):
            executable_statements.discard(line_no)
        
        # Check if the next line after the function signature is a docstring (i.e., starts with triple quotes)
        # Unfortunately these starting docstrings have a lineno attribute so they have to be discarded manually
        next_line_index = function_signature_line - start_line + 1
        if next_line_index < len(lines):
            next_line = lines[next_line_index].strip()
            if next_line.startswith('"""'):
                executable_statements.discard(function_signature_line + 1)

    return executable_statements


def run_with_metrics(function, args, executable_statements, filename, cov) -> tuple:
    """
    Executes a function and records the execution time, code coverage and arc coverage.
    
    Returns:
    tuple: A tuple containing the result of the function and the metrics object.
    """
    metrics = Metrics()

    cov.start()
    start_time = time.time()
    result = function(*args)
    end_time = time.time()
    cov.stop()

    execution_time = int((end_time - start_time) * 1_000_000) # Convert to microseconds
    metrics.executionTime = execution_time

    data = cov.get_data()
    covered_lines = data.lines(filename)

    all_arcs_in_file = data.arcs(filename)
    covered_arcs = []

    if all_arcs_in_file and covered_lines:
        covered_arcs = [
            arc
            for arc in all_arcs_in_file
            if arc[0] in covered_lines or arc[1] in covered_lines
        ]
        metrics.coveredArcsInFile = len(covered_arcs)

    metrics.coveredLinesInFile = len(covered_lines)

    if len(executable_statements) == 0:
        # If there is no information on which lines of the function are executable (e.g., for class functions),
        # further metrics like ratio of covered lines are not possible
        return (result, metrics)

    covered_lines_in_function = None

    if covered_lines:
        covered_lines_in_function = set(covered_lines) & set(executable_statements)

    covered_arcs_in_function = []
    if all_arcs_in_file:
        covered_arcs_in_function = [
            arc
            for arc in all_arcs_in_file
            if arc[0] in covered_lines_in_function
            or arc[1] in covered_lines_in_function
        ]

    if covered_lines:
        metrics.coveredLinesInFunction = len(covered_lines_in_function)
        metrics.coveredLinesInFunctionRatio = len(covered_lines_in_function) / len(
            executable_statements
        ) * 100
    if all_arcs_in_file:
        metrics.coveredArcsInFunction = len(covered_arcs_in_function)

    return (result, metrics)

if __name__ == "__main__":
    import numpy.lib.scimath as np
    print(get_executable_statements("sqrt", np))
