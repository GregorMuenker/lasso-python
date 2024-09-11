import inspect
import os
import time
import coverage
import datetime
import json
import io
import uuid
import warnings
import importlib
import sys
import git
repo = git.Repo(search_parent_directories=True)
sys.path.insert(0, repo.working_tree_dir)

from backend.constants import BLUE, CYAN, GREEN, MAGENTA, RED, RESET, YELLOW
from ignite import CellId, CellValue
from adaptation_identification import (
    InterfaceSpecification,
    Mapping,
    AdaptationHandler,
    AdaptationInstruction,
)
from sequence_specification import SequenceSpecification


class SequenceExecutionRecord:
    
    def __init__(
        self,
        mapping: Mapping,
        interfaceSpecification: InterfaceSpecification,
        sequenceSpecification: SequenceSpecification,
        executionId,
    ) -> None:
        self.interfaceSpecification = interfaceSpecification
        self.mapping = mapping
        self.sequenceSpecification = sequenceSpecification
        self.rowRecords = []  # List[RownRecord]
        self.executionId = executionId

    def toSheetCells(self) -> list:
        """
        This method converts the sequence execution record into pairs of (CellId, CellValue) that can be put into the Ignite cache.

        Returns:
        A list of (CellId, CellValue) tuples that represent the cells in the sequence sheet.
        """
        cells = []
        serializedStrLength = 15
        for rowRecord in self.rowRecords:

            originalFunctionName = rowRecord.originalFunctionName
            adaptationId = str(rowRecord.adaptationInstruction.identifier)
            adaptationInstruction = str(rowRecord.adaptationInstruction.getDetailedInstructions())

            if rowRecord.metrics.executionTime == None:
                executionTime = -1
            else:
                executionTime = rowRecord.metrics.executionTime

            systemId = str(self.mapping.identifier) # TODO change to id from Solr

            # Return value
            ci1 = CellId(
                EXECUTIONID=str(self.executionId),
                ABSTRACTIONID=self.interfaceSpecification.className,
                ACTIONID="",
                ARENAID="execute",
                SHEETID=self.sequenceSpecification.name,
                SYSTEMID=systemId,
                VARIANTID="original",
                ADAPTERID=adaptationId,
                X=0,
                Y=rowRecord.position,
                TYPE="value",
            )
            cv1 = CellValue(
                VALUE=str(rowRecord.returnValue)[:serializedStrLength],
                RAWVALUE=str(rowRecord.returnValue),
                VALUETYPE=str(type(rowRecord.returnValue)),
                LASTMODIFIED=datetime.datetime.now(),
                EXECUTIONTIME=executionTime,
            )
            cells.append((ci1, cv1))

            # Oracle
            if rowRecord.oracleValue != None:
                ci2 = CellId(
                    EXECUTIONID=str(self.executionId),
                    ABSTRACTIONID=self.interfaceSpecification.className,
                    ACTIONID="",
                    ARENAID="execute",
                    SHEETID=self.sequenceSpecification.name,
                    SYSTEMID="oracle",
                    VARIANTID="oracle",
                    ADAPTERID="oracle",
                    X=0,
                    Y=rowRecord.position,
                    TYPE="oracle",
                )
                cv2 = CellValue(
                    VALUE=str(rowRecord.oracleValue)[:serializedStrLength],
                    RAWVALUE=str(rowRecord.oracleValue),
                    VALUETYPE=str(type(rowRecord.oracleValue)),
                    LASTMODIFIED=datetime.datetime.now(),
                    EXECUTIONTIME=-1,
                )
                cells.append((ci2, cv2))

            # Operation
            ci3 = CellId(
                EXECUTIONID=str(self.executionId),
                ABSTRACTIONID=self.interfaceSpecification.className,
                ACTIONID="",
                ARENAID="execute",
                SHEETID=self.sequenceSpecification.name,
                SYSTEMID=systemId,
                VARIANTID="original",
                ADAPTERID=adaptationId,
                X=1,
                Y=rowRecord.position,
                TYPE="op",
            )
            cv3 = CellValue(
                VALUE=originalFunctionName[:serializedStrLength],
                RAWVALUE=originalFunctionName,
                VALUETYPE="function",
                LASTMODIFIED=datetime.datetime.now(),
                EXECUTIONTIME=executionTime,
            )
            cells.append((ci3, cv3))

            # Adaptation instruction
            ci4 = CellId(
                EXECUTIONID=str(self.executionId),
                ABSTRACTIONID=self.interfaceSpecification.className,
                ACTIONID="",
                ARENAID="execute",
                SHEETID=self.sequenceSpecification.name,
                SYSTEMID=systemId,
                VARIANTID="original",
                ADAPTERID=adaptationId,
                X=1,
                Y=rowRecord.position,
                TYPE="adaptation_instruction",
            )
            cv4 = CellValue(
                VALUE=adaptationInstruction[:serializedStrLength],
                RAWVALUE=adaptationInstruction,
                VALUETYPE="AdaptationInstruction",
                LASTMODIFIED=datetime.datetime.now(),
                EXECUTIONTIME=-1,
            )
            cells.append((ci4, cv4))

            # Error message
            if rowRecord.errorMessage != None:
                ci5 = CellId(
                EXECUTIONID=str(self.executionId),
                ABSTRACTIONID=self.interfaceSpecification.className,
                ACTIONID="",
                ARENAID="execute",
                SHEETID=self.sequenceSpecification.name,
                SYSTEMID=systemId,
                VARIANTID="original",
                ADAPTERID=adaptationId,
                X=1,
                Y=rowRecord.position,
                TYPE="error_message",
                )
                cv5 = CellValue(
                VALUE=str(rowRecord.errorMessage)[:serializedStrLength],
                RAWVALUE=str(rowRecord.errorMessage),
                VALUETYPE=str(type(rowRecord.errorMessage)),
                LASTMODIFIED=datetime.datetime.now(),
                EXECUTIONTIME=executionTime,
            )
                cells.append((ci5, cv5))

            # Input values
            for xPosition, inputParam in enumerate(rowRecord.inputParams):
                ci6 = CellId(
                    EXECUTIONID=str(self.executionId),
                    ABSTRACTIONID=self.interfaceSpecification.className,
                    ACTIONID="",
                    ARENAID="execute",
                    SHEETID=self.sequenceSpecification.name,
                    SYSTEMID=systemId,
                    VARIANTID="original",
                    ADAPTERID=adaptationId,
                    X=3 + xPosition,
                    Y=rowRecord.position,
                    TYPE="input_value",
                )
                cv6 = CellValue(
                    VALUE=str(inputParam)[:serializedStrLength],
                    RAWVALUE=str(inputParam),
                    VALUETYPE=str(type(inputParam)),
                    LASTMODIFIED=datetime.datetime.now(),
                    EXECUTIONTIME=-1,
                )
                cells.append((ci6, cv6))
            
            # Instance param
            ci7 = CellId(
                EXECUTIONID=str(self.executionId),
                ABSTRACTIONID=self.interfaceSpecification.className,
                ACTIONID="",
                ARENAID="execute",
                SHEETID=self.sequenceSpecification.name,
                SYSTEMID=systemId,
                VARIANTID="original",
                ADAPTERID=adaptationId,
                X=2,
                Y=rowRecord.position,
                TYPE="input_value",
            )
            cv7 = CellValue(
                VALUE=str(rowRecord.instanceParam)[:serializedStrLength],
                RAWVALUE=str(rowRecord.instanceParam),
                VALUETYPE=str(type(rowRecord.instanceParam)),
                LASTMODIFIED=datetime.datetime.now(),
                EXECUTIONTIME=-1,
            )
            cells.append((ci7, cv7))

            # Metrics
            if not rowRecord.metrics.isEmpty():
                for key, value in rowRecord.metrics.toDict().items():
                    if value == None:
                        continue

                    ci8 = CellId(
                        EXECUTIONID=str(self.executionId),
                        ABSTRACTIONID=self.interfaceSpecification.className,
                        ACTIONID="",
                        ARENAID="execute",
                        SHEETID=self.sequenceSpecification.name,
                        SYSTEMID=systemId,
                        VARIANTID="original",
                        ADAPTERID=adaptationId,
                        X=-1,
                        Y=rowRecord.position,
                        TYPE=key,
                    )
                    cv8 = CellValue(
                        VALUE=str(value)[:serializedStrLength],
                        RAWVALUE=str(value),
                        VALUETYPE=str(type(value)),
                        LASTMODIFIED=datetime.datetime.now(),
                        EXECUTIONTIME=-1,
                    )
                    cells.append((ci8, cv8))

        return cells

    def __repr__(self) -> str:
        result = f"{self.mapping}"
        for rowRecord in self.rowRecords:
            result += f"\n\t{rowRecord}"
        return f"{result}\n"


class ExecutionEnvironment:
    """
    Holds multiple SequenceExecutionRecord objects.
    This class is associated with multiple mappings that all are associated with the same module, interface spec and sequence spec.
    """
    def __init__(
        self,
        mappings: list,
        sequenceSpecification: SequenceSpecification,
        interfaceSpecification: InterfaceSpecification,
        recordMetrics: bool = True
    ) -> None:
        self.mappings = mappings
        self.interfaceSpecification = interfaceSpecification
        self.sequenceSpecification = sequenceSpecification
        self.recordMetrics = recordMetrics
        self.uuid = uuid.uuid4() # Later used as execution id when saving observations in Ignite

        self.allSequenceExecutionRecords = []

        for mapping in mappings:
            sequenceExecutionRecord = SequenceExecutionRecord(
                mapping=mapping,
                interfaceSpecification=interfaceSpecification,
                sequenceSpecification=sequenceSpecification,
                executionId=self.uuid
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
        instanceParam: object,
        adaptationInstruction: AdaptationInstruction,
        oracleValue=None,
    ) -> None:
        self.position = position  # The y coordinate of the row in the sequence sheet
        self.methodName = methodName
        self.originalFunctionName = originalFunctionName
        self.inputParams = inputParams
        self.instanceParam = instanceParam
        self.adaptationInstruction = adaptationInstruction
        self.oracleValue = oracleValue

        self.returnValue = None
        self.metrics = None
        self.errorMessage = None

    def __repr__(self) -> str:
        inputParamsString = ", ".join(map(str, self.inputParams))
        instruction = f"{str(self.instanceParam)[:15]}.{self.methodName}({inputParamsString})"
        result = f"{CYAN}[{self.position}] {instruction}: {self.returnValue}{RESET} (expected: {self.oracleValue}), {self.metrics}"
        
        if self.errorMessage != None:
            result += f", Error: {self.errorMessage}"
        return result


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

    def isEmpty(self) -> bool:
        return (
            self.executionTime == None
            and self.allLinesInFile == None
            and self.coveredLinesInFile == None
            and self.allLinesInFunction == None
            and self.coveredLinesInFunction == None
            and self.coveredLinesInFunctionRatio == None
            and self.allBranchesInFile == None
            and self.coveredBranchesInFile == None
            and self.allBranchesInFunction == None
            and self.coveredBranchesInFunction == None
        )

    def toDict(self) -> dict:
        return {
            "metrics_execution_time": self.executionTime,
            "metrics_all_lines_in_file": self.allLinesInFile,
            "metrics_covered_lines_in_file": self.coveredLinesInFile,
            "metrics_all_lines_in_function": self.allLinesInFunction,
            "metrics_covered_lines_in_function": self.coveredLinesInFunction,
            "metrics_covered_lines_in_function_ratio": self.coveredLinesInFunctionRatio,
            "metrics_all_branches_in_file": self.allBranchesInFile,
            "metrics_covered_branches_in_file": self.coveredBranchesInFile,
            "metrics_all_branches_in_function": self.allBranchesInFunction,
            "metrics_covered_branches_in_function": self.coveredBranchesInFunction,
        }


    def __repr__(self) -> str:
        if self.isEmpty():
            return "No metrics recorded"
        else:
            return f"Time: {self.executionTime} microseconds. Covered lines: {self.coveredLinesInFile}/{self.allLinesInFile} in file, {self.coveredLinesInFunction}/{self.allLinesInFunction} in function ({self.coveredLinesInFunctionRatio}%). Covered branches: {self.coveredBranchesInFile}/{self.allBranchesInFile} in file, {self.coveredBranchesInFunction}/{self.allBranchesInFunction} in function."


def execute_test(
    execution_environment: ExecutionEnvironment,
    adaptation_handler: AdaptationHandler,
    module_name: str,
    import_from_file_path = None,
) -> None:
    """
    Executes a sequence sheet based on a provided module and stores the results in the ExecutionEnvironment object.

    Parameters:
    adapted_module: The module that contains the adapted functions in 1 or more submodules (mapping0, mapping1, ...).
    execution_environment: The ExecutionEnvironment object used for this execution.
    module_name: The name of the module used for execution.
    import_from_file_path: The path to a file that should be imported instead of the module name. This is only used for testing purposes.
    """

    from adaptation_implementation import create_adapted_submodule
    sequence_spec = execution_environment.sequenceSpecification
    mappings = execution_environment.mappings

    print(
        f"\n{CYAN}----------------------\nEXECUTE SEQUENCE SHEET\n----------------------{RESET}"
    )
    print(f"Module: {module_name}")
    print(f"Number of submodules: {len(mappings)}")
    print(f"Execution Id: {execution_environment.uuid}")
    print("Sequence sheet:")
    sequence_spec.printSequenceSheet()

    # Try to import the module
    module = None
    try:
        if import_from_file_path != None:
            # Import module from a single file, only for testing
            spec = importlib.util.spec_from_file_location(
                module_name, import_from_file_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        else:
            module = importlib.import_module(module_name)
    except Exception as e:
        print(f"Error when trying to import module {module_name}, terminating execution: {e}")
        return

    for i, mapping in enumerate(mappings):

        sequenceExecutionRecord = execution_environment.getSequenceExecutionRecord(mapping)

        adapted = False

        class_instance = None

        for index, statement in sequence_spec.statements.items():

            # Resolve references in column input params
            for param in statement.inputParams:
                if isinstance(param, str) and param[0].isupper() and param[1:].isnumeric():
                    statement.inputParams[statement.inputParams.index(param)] = sequence_spec.resolve_reference(param)

            # Resolve references in column oracle values
            if statement.oracleValue is not None and isinstance(statement.oracleValue, str) and statement.oracleValue[0].isupper() and statement.oracleValue[1:].isnumeric():
                statement.oracleValue = sequence_spec.resolve_reference(statement.oracleValue)

            # Resolve references in column instance params
            if statement.instanceParam is not None and isinstance(statement.instanceParam, str) and statement.instanceParam[0].isupper() and statement.instanceParam[1:].isnumeric():
                statement.instanceParam = sequence_spec.resolve_reference(statement.instanceParam)

            # Some logic for handling create statements
            if statement.methodName == "create":
                if statement.instanceParam.startswith("python."):
                    instance_param = statement.instanceParam[7:]  # Remove "python." from the beginning of the instance param
                    switch_case = {
                        "Array": statement.inputParams,
                        "List": list(statement.inputParams),
                        "Tupel": tuple(statement.inputParams),
                        "Set": set(statement.inputParams),
                        # Add more cases for other modules as needed
                    }
                    if instance_param in switch_case:
                        try:
                            statement.output = switch_case[instance_param]

                            rowRecord = RowRecord(
                                position=index,
                                methodName=statement.methodName,
                                originalFunctionName=statement.methodName,
                                inputParams=statement.inputParams,
                                oracleValue=statement.oracleValue,
                                instanceParam=statement.instanceParam,
                                adaptationInstruction=AdaptationInstruction(
                                    interfaceMethodName="create",
                                    moduleFunctionQualName="createPythonObject",
                                    iteration=0,
                                ),
                            )
                            rowRecord.returnValue = statement.output
                            # For completeness, an empty metrics object is created for python.* calls
                            metrics = Metrics()
                            rowRecord.metrics = metrics
                            sequenceExecutionRecord.rowRecords.append(rowRecord)
                        except Exception as e:
                            print(f"Error when trying to execute create method for {instance_param}: {e}")
                    else:
                        print(f"Invalid python instance param: {instance_param}")
                elif "." not in statement.instanceParam:
                    module, submodule, class_instance = create_adapted_submodule(
                        adaptation_handler,
                        module,
                        execution_environment,
                        i,
                        statement,
                    )
                    adapted = True
                    statement.output = class_instance

                elif statement.instanceParam.startswith("numpy."):
                    print(f"Skipping numpy create statement {statement.instanceParam}")
                else:
                    print(f"Skipping 3rd party package create statement {statement.instanceParam}")
                continue

            if statement.methodName.startswith("__") and statement.methodName.endswith("__"):
                statement = execute_default_functions(statement)
                rowRecord = RowRecord(
                    position=index,
                    methodName=statement.methodName,
                    originalFunctionName=statement.methodName,
                    inputParams=statement.inputParams,
                    oracleValue=statement.oracleValue,
                    instanceParam=statement.instanceParam,
                    adaptationInstruction=AdaptationInstruction(
                        interfaceMethodName=statement.methodName,
                        moduleFunctionQualName=statement.methodName,
                        iteration=0,
                    ),
                )
                rowRecord.returnValue = statement.output
                rowRecord.metrics = Metrics() # Use empty metrics object for default functions
                sequenceExecutionRecord.rowRecords.append(rowRecord)
                continue

            if not adapted:
                raise ValueError("No create statement found in sequence sheet")

            original_function_name, adaptationInstruction = mappings[i].adaptationInfo[
                statement.methodName
            ]

            # Determine the actual instance param for generating a RowRecord
            actual_instance = class_instance
            if (mappings[i].functionSignatures[original_function_name].parentClass == None):
                # If the function is a standalone function, the actual instance param is set to "-"
                actual_instance = "-"

            rowRecord = RowRecord(
                position=index,
                methodName=statement.methodName,
                originalFunctionName=original_function_name,
                inputParams=statement.inputParams,
                oracleValue=statement.oracleValue,
                instanceParam=actual_instance,
                adaptationInstruction=adaptationInstruction,
            )

            # Build the instruction string to output errors in a more readable way
            input_params_string = ", ".join(map(str, statement.inputParams))
            instruction = f"{statement.methodName}({input_params_string})"

            # Retrieve the function object from the submodule
            method = None
            try:
                method = getattr(submodule, statement.methodName)
            except Exception as e:
                print(
                    f"Error when trying to get method {statement.methodName} from submodule {submodule}. Error: {e}"
                )
                rowRecord.errorMessage = e
                continue

            # Set the return value by executing the function
            return_value = "UNSUCCESSFUL"
            metrics = Metrics()
            try:
                if not execution_environment.recordMetrics:
                    return_value = method(*statement.inputParams)
                else:
                    filename = inspect.getfile(module)
                    # NOTE: Using the absolute path is neccessary as a relative path will mess up the coverage report
                    filename = os.path.abspath(filename)

                    cov = coverage.Coverage(source=[module.__name__], branch=True)
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
                rowRecord.errorMessage = e

            # Fill in the results for this execution
            statement.output = return_value
            rowRecord.returnValue = return_value
            rowRecord.metrics = metrics

            sequenceExecutionRecord.rowRecords.append(rowRecord)

        # After executing all statements for a mapping, reset the sequence sheet to remove output values and resolved references
        sequence_spec.reset()

    sequenceExecutionRecord

def execute_default_functions(statement):
    if statement.methodName == "__len__":
        statement.output = len(statement.instanceParam)
    if statement.methodName == "__getitem__":
        statement.output = statement.instanceParam[statement.inputParams[0]]

    return statement

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

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")  # Always trigger the warning for capture

        # Attempt to run json_report
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
