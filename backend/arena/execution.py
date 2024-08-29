import inspect
import os
import time
import coverage
import datetime
import json
import io

import sys

sys.path.insert(1, "../../backend")
from constants import CYAN, RED, RESET
from ignite import CellId, CellValue
from adaptation_identification import InterfaceSpecification, Mapping
from sequence_specification import SequenceSpecification


class SequenceExecutionRecord:
    def __init__(
        self,
        mapping: Mapping,
        interfaceSpecification: InterfaceSpecification,
        sequenceSpecification: SequenceSpecification,
    ) -> None:
        self.interfaceSpecification = interfaceSpecification
        self.mapping = mapping
        self.sequenceSpecification = sequenceSpecification
        self.rowRecords = []  # List[RownRecord]

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
        list: A list of (CellId, CellValue) tuples that represent the cells in the sequence sheet.
        """
        cells = []

        for rowRecord in self.rowRecords:
            original_function_name, adaptation_instruction = (
                self.mapping.adaptationInfo[rowRecord.methodName]
            )

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
                Y=rowRecord.position,
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
                Y=rowRecord.position,
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
                    X=3 + xPosition,
                    Y=rowRecord.position,
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
                Y=rowRecord.position,
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
        for rowRecord in self.rowRecords:
            result += f"\n\t{rowRecord}"
        return f"{result}\n"
    

class ExecutionEnvironment:
    """
    Holds multiple SequenceExecutionRecord objects.
    This class is associated with multiple mappings that all are associated with the same module, interface spec and sequence spec.
    """
    def __init__(self, mappings, sequenceSpecification: SequenceSpecification, interfaceSpecification: InterfaceSpecification) -> None:
        self.mappings = mappings
        self.interfaceSpecification = interfaceSpecification
        self.sequenceSpecification = sequenceSpecification

        self.allSequenceExecutionRecords = []
        
        for mapping in mappings:
            sequenceExecutionRecord = SequenceExecutionRecord(
                mapping=mapping,
                interfaceSpecification=interfaceSpecification,
                sequenceSpecification=sequenceSpecification,
            )
            self.allSequenceExecutionRecords.append(sequenceExecutionRecord)
    
    def getSequenceExecutionRecord(self, mapping: Mapping):
        for sequenceExecutionRecord in self.allSequenceExecutionRecords:
            if sequenceExecutionRecord.mapping == mapping:
                return sequenceExecutionRecord
        return None

    def printResults(self) -> None:
        for sequenceExecutionRecord in self.allSequenceExecutionRecords:
            print(sequenceExecutionRecord)

    def saveResults(self, igniteClient) -> None:
        for sequenceExecutionRecord in self.allSequenceExecutionRecords:
            cells = sequenceExecutionRecord.toSheetCells()
            igniteClient.putAll(cells)


class RowRecord:
    def __init__(
        self,
        position: int,
        methodName: str,
        originalFunctionName: str,
        inputParams: list,
        oracleValue=None,
    ) -> None:
        self.position = position  # The y coordinate of the row in the sequence sheet
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

        self.allLinesInFile = None
        self.coveredLinesInFile = None

        self.allLinesInFunction = None
        self.coveredLinesInFunction = None
        self.coveredLinesInFunctionRatio = None

        self.allBranchesInFile = None
        self.coveredBranchesInFile = None

        self.allBranchesInFunction = None
        self.coveredBranchesInFunction = None

    def __repr__(self) -> str:
        return f"Time: {self.executionTime} microseconds. Covered lines: {self.coveredLinesInFile}/{self.allLinesInFile} in file, {self.coveredLinesInFunction}/{self.allLinesInFunction} in function ({self.coveredLinesInFunctionRatio}%). Covered branches: {self.coveredBranchesInFile}/{self.allBranchesInFile} in file, {self.coveredBranchesInFunction}/{self.allBranchesInFunction} in function."


def execute_test(
    adapted_module: object,
    execution_environment: ExecutionEnvironment,
) -> None:
    """
    Executes a sequence sheet based on a provided module and stores the results in the ExecutionEnvironment object.

    Parameters:
    adapted_module: The module that contains the adapted functions in 1 or more submodules (mapping0, mapping1, ...).
    execution_environment: The ExecutionEnvironment object used for this execution.
    """
    sequence_spec = execution_environment.sequenceSpecification
    mappings = execution_environment.mappings

    print(
        f"\n{CYAN}----------------------\nEXECUTE SEQUENCE SHEET\n----------------------{RESET}"
    )
    print(f"Module: {adapted_module.__name__}")
    print(f"Number of submodules: {len(mappings)}")
    print(f"\n {sequence_spec.sequenceSheet}\n")

    for i, mapping in enumerate(mappings):
        if not mapping.successful:
            continue # TODO store error message?
        
        submodule = getattr(adapted_module, "mapping" + str(i))

        sequenceExecutionRecord = execution_environment.getSequenceExecutionRecord(mapping)

        for index, statement in sequence_spec.statements.items():

            # Skip the create statement as it already has been covered during creating the adapted module
            if statement.methodName == "create":
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

            # Set the return value
            return_value = "Execution unsuccessful"
            metrics = "No metrics recorded"
            try:
                filename = inspect.getfile(adapted_module)
                # NOTE: Using the absolute path is neccessary as a relative path will mess up the coverage report
                filename = os.path.abspath(filename)

                cov = coverage.Coverage(source=[adapted_module.__name__], branch=True)
                return_value, metrics = run_with_metrics(
                    method,
                    statement.inputParams,
                    filename,
                    cov,
                    original_function_name,
                )
            except Exception as e:
                print(
                    f"{RED}{instruction} ({submodule}, {original_function_name}, {adaptationInstruction}) failed{RESET}: {e}"
                )

            # Fill in the results for this execution
            rowRecord.returnValue = return_value
            rowRecord.metrics = metrics

            sequenceExecutionRecord.rowRecords.append(rowRecord)

def run_with_metrics(
    function: object,
    args: list,
    filename: str,
    cov: object,
    original_function_name: str,
) -> tuple:
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

    execution_time = int((end_time - start_time) * 1_000_000)  # Convert to microseconds
    metrics.executionTime = execution_time

    # Modify stdout to capture the coverage report
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
