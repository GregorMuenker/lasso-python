import json
from module_parser import parse_code
from adaptation_identification import AdaptationHandler
from lql.antlr_parser import parse_interface_spec
from execution import ExecutionEnvironment, execute_test
from sequence_specification import SequenceSpecification
from adaptation_implementation import create_adapted_module
import os

file = open('evaluation_sanitized-mbpp.json', 'r')
data = json.load(file)  

tasks = set([1])
code = ""
for task in tasks:
    code += data[task]["code"] + "\n\n"

file = open('evaluation_output.py', 'w')
file.write(code)
file = open('evaluation_output.py', 'r')
file_content = file.read()
module_under_test = parse_code(file_content, "MBPP")

lql_string = """
    Benchmark {
        not_prime(int)->bool
    }
    """

interface_spec = parse_interface_spec(lql_string)
sequence_spec = SequenceSpecification("evaluation.xlsx")

adaptationHandler = AdaptationHandler(
    interface_spec,
    module_under_test,
    maxParamPermutationTries=1,
    onlyKeepTopNMappings=3,
)
adaptationHandler.identifyAdaptations()
adaptationHandler.identifyConstructorAdaptations()
adaptationHandler.visualizeAdaptations()
adaptationHandler.generateMappings()

executionEnvironment = ExecutionEnvironment(
    adaptationHandler.mappings,
    sequence_spec,
    interface_spec
)

adapted_module = create_adapted_module(
    adaptationHandler,
    module_under_test.moduleName,
    executionEnvironment,
    import_from_file_path = "evaluation_output.py",
)

allSequenceExecutionRecords = execute_test(
    adapted_module,
    executionEnvironment,
)

executionEnvironment.printResults()

os.remove("evaluation_output.py")
