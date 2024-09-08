import inspect
import os
import time
import coverage
import datetime
import json
import io
import uuid

import sys

sys.path.insert(1, "../../backend")
from constants import BLUE, CYAN, GREEN, MAGENTA, RED, RESET, YELLOW
from ignite import CellId, CellValue
from adaptation_identification import InterfaceSpecification, Mapping, AdaptationHandler
from sequence_specification_greg import SequenceSpecification
from pyignite.datatypes import TimestampObject

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
        list: A list of (CellId, CellValue) tuples that represent the cells in the sequence sheet.
        """
        cells = []
        serializedStrLength = 15

        for rowRecord in self.rowRecords:
            # NOTE no handling of python operations (creating a list etc.)
            
            originalFunctionName, adaptationInstruction = (
                self.mapping.adaptationInfo[rowRecord.methodName]
            )
            adaptationId = str(adaptationInstruction.identifier)

            # Return value
            cellId = CellId(
                EXECUTIONID=str(self.executionId),
                ABSTRACTIONID=self.interfaceSpecification.className,
                ACTIONID="",
                ARENAID="execute",
                SHEETID=self.sequenceSpecification.name,
                SYSTEMID="",
                VARIANTID="original",
                ADAPTERID=adaptationId,
                X=0,
                Y=rowRecord.position,
                TYPE="value",
            )
            cellValue = CellValue(
                VALUE=str(rowRecord.returnValue)[:serializedStrLength],
                RAWVALUE=str(rowRecord.returnValue),
                VALUETYPE=str(type(rowRecord.returnValue)),
                LASTMODIFIED=datetime.datetime.now(),
                EXECUTIONTIME=rowRecord.metrics.executionTime,
            )
            cells.append((cellId, cellValue))

            # Oracle
            if rowRecord.oracleValue != None:
                cellId = CellId(
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
                cellValue = CellValue(
                    VALUE=str(rowRecord.oracleValue)[:serializedStrLength],
                    RAWVALUE=str(rowRecord.oracleValue),
                    VALUETYPE=str(type(rowRecord.oracleValue)),
                    LASTMODIFIED=datetime.datetime.now(),
                    EXECUTIONTIME=rowRecord.metrics.executionTime,
                )
                cells.append((cellId, cellValue))

            # Operation
            cellId = CellId(
                EXECUTIONID=str(self.executionId),
                ABSTRACTIONID=self.interfaceSpecification.className,
                ACTIONID="",
                ARENAID="execute",
                SHEETID=self.sequenceSpecification.name,
                SYSTEMID="",
                VARIANTID="original",
                ADAPTERID=adaptationId,
                X=1,
                Y=rowRecord.position,
                TYPE="op",
            )
            cellValue = CellValue(
                VALUE=originalFunctionName[:serializedStrLength],
                RAWVALUE=originalFunctionName,
                VALUETYPE="function",
                LASTMODIFIED=datetime.datetime.now(),
                EXECUTIONTIME=rowRecord.metrics.executionTime,
            )
            cells.append((cellId, cellValue))

            # Input values
            for xPosition, inputParam in enumerate(rowRecord.inputParams):
                cellId = CellId(
                    EXECUTIONID=str(self.executionId),
                    ABSTRACTIONID=self.interfaceSpecification.className,
                    ACTIONID="",
                    ARENAID="execute",
                    SHEETID=self.sequenceSpecification.name,
                    SYSTEMID="",
                    VARIANTID="original",
                    ADAPTERID=adaptationId,
                    X=3 + xPosition,
                    Y=rowRecord.position,
                    TYPE="input_value",
                )
                cellValue = CellValue(
                    VALUE=str(inputParam)[:serializedStrLength],
                    RAWVALUE=str(inputParam),
                    VALUETYPE=str(type(inputParam)),
                    LASTMODIFIED=datetime.datetime.now(),
                    EXECUTIONTIME=-1,
                )
                cells.append((cellId, cellValue))

            # Metrics
            if not rowRecord.metrics.isEmpty():
                for key, value in rowRecord.metrics.toDict().items():
                    if value == None:
                        continue

                    cellId = CellId(
                        EXECUTIONID=str(self.executionId),
                        ABSTRACTIONID=self.interfaceSpecification.className,
                        ACTIONID="",
                        ARENAID="metrics",
                        SHEETID=self.sequenceSpecification.name,
                        SYSTEMID="",
                        VARIANTID="original",
                        ADAPTERID=adaptationId,
                        X=-1,
                        Y=rowRecord.position,
                        TYPE=key,
                    )
                    cellValue = CellValue(
                        VALUE=str(value)[:serializedStrLength],
                        RAWVALUE=str(value),
                        VALUETYPE=str(type(value)),
                        LASTMODIFIED=datetime.datetime.now(),
                        EXECUTIONTIME=-1,
                    )
                    cells.append((cellId, cellValue))

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

    # def getCorrectMethods(self):
    #    for sequenceExecutionRecord in self.allSequenceExecutionRecords:
    #        correct = True
    #        for rowRecord in sequenceExecutionRecord.rowRecords:
    #            if rowRecord.oracleValue != rowRecord.returnValue:
    #                correct = False
    #                print(f"Method {rowRecord.originalFunctionName} was correct")
    #        if correct:
    #            print(f"Mapping {[rowRecord.originalFunctionName for rowRecord in sequenceExecutionRecord.rowRecords]} is correct")


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
        self.errorMessage = None

    def __repr__(self) -> str:
        inputParamsString = ", ".join(map(str, self.inputParams))
        instruction = f"{self.methodName}({inputParamsString})"
        result = f"{CYAN}{instruction}: {self.returnValue} (expected: {self.oracleValue}){RESET}, {self.metrics}"
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
    """
    
    from adaptation_implementation import create_adapted_submodule
    sequence_spec = execution_environment.sequenceSpecification
    mappings = execution_environment.mappings

    print(
        f"\n{CYAN}----------------------\nEXECUTE SEQUENCE SHEET\n----------------------{RESET}"
    )
    print(f"Module: {module_name}")
    print(f"Number of submodules: {len(mappings)}")
    print(f"\n {sequence_spec.sequenceSheet}\n")

    for i, mapping in enumerate(mappings):

        sequenceExecutionRecord = execution_environment.getSequenceExecutionRecord(mapping)
        
        adopted = False
        
        for index, statement in sequence_spec.statements.items():
            
            print(sequence_spec.statements)
            
            for param in statement.inputParams:
                if isinstance(param, str) and param[0].isupper() and param[1:].isnumeric():
                    statement.inputParams[statement.inputParams.index(param)] = sequence_spec.resolve_reference(param)
            
            if statement.oracleValue is not None and isinstance(statement.oracleValue, str) and statement.oracleValue[0].isupper() and statement.oracleValue[1:].isnumeric():
                statement.oracleValue = sequence_spec.resolve_reference(statement.oracleValue)
                    
            # Skip the create statement as it already has been covered during creating the adapted module
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
                            )
                            rowRecord.returnValue = statement.output
                            sequenceExecutionRecord.rowRecords.append(rowRecord)
                        except Exception as e:
                            print(f"Error when trying to execute create method for {instance_param}: {e}")
                    else:
                        print(f"Invalid python instance param: {instance_param}")
                elif "." not in statement.instanceParam:
                    adapted_module, submodule, class_instance = create_adapted_submodule(
                        adaptation_handler,
                        module_name,
                        execution_environment,
                        i,
                        statement.inputParams,
                        import_from_file_path,
                    )
                    adopted = True
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
                )
                rowRecord.returnValue = statement.output
                sequenceExecutionRecord.rowRecords.append(rowRecord)
                continue
            
            print(statement.inputParams)
            print(mappings[i].adaptationInfo)
            
            if not adopted:
                raise ValueError("No create statement found in sequence sheet")
                #adapt_submodule = create_adapted_submodule(
                #    adaptation_handler,
                #    module_name,
                #    execution_environment,
                #    i,
                #    [],
                #    import_from_file_path,
                #)
            
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
                rowRecord.errorMessage = e
                continue

            # Set the return value
            return_value = "UNSUCCESSFUL"
            metrics = Metrics()
            try:
                if not execution_environment.recordMetrics:
                    return_value = method(*statement.inputParams)
                else:
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
                rowRecord.errorMessage = e

            # Fill in the results for this execution
            statement.output = return_value
            rowRecord.returnValue = return_value
            rowRecord.metrics = metrics

            sequenceExecutionRecord.rowRecords.append(rowRecord)
            
    sequenceExecutionRecord
    
def execute_default_functions(statement):
    if len(statement.inputParams) == 1:
        if statement.methodName == "__len__":
            statement.output = len(statement.inputParams[0])
    if statement.methodName == "__getitem__":
        statement.output = statement.inputParams[0][statement.inputParams[1]]
    if statement.methodName == "__setitem__":
        statement.inputParams[0][statement.inputParams[1]] = statement.inputParams[2]
    if statement.methodName == "__delitem__":
        del statement.inputParams[0][statement.inputParams[1]]
    if statement.methodName == "__iter__":
        statement.output = iter(statement.inputParams[0])
    if statement.methodName == "__next__":
        statement.output = next(statement.inputParams[0])
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
