import uuid
import pandas as pd
import git
import sys

repo = git.Repo(search_parent_directories=True)
sys.path.insert(0, repo.working_tree_dir)

from backend.crawl import import_helper
from backend.crawl.nexus import Nexus, Package
from backend.arena.lasso_solr_connector import LassoSolrConnector
from backend.arena.sequence_specification import SequenceSpecification
from backend.arena.ignite import LassoIgniteClient
from backend.arena.adaptation_identification import AdaptationHandler
from backend.arena.execution import execute_test, ExecutionEnvironment
from backend.lql.antlr_parser import parse_interface_spec

import builtins
import ast
import json

cell_number = 1

def create_lql(task):
    task_ast = ast.parse(task["code"])
    lql = [f"Task{task['task_id']}"]
    for element in task_ast.body:
        if type(element) == ast.FunctionDef:
            arg_count = len(element.args.args)
            lql.append(f"{element.name}({','.join(['Any' for _ in range(arg_count)])})->Any")
    lql = f'{lql[0]} <begin>' + "\n\t".join([""] + lql[1:]) + "\n<end>"
    lql = lql.replace("<begin>", "{").replace("<end>", "}")
    with open(f"./evaluation_sheets/llm_lql_scripts/task{task['task_id']}.lql", "w") as file:
        file.write(lql)

def create_sequence_sheet_entries(test, element, cell_type):
    global cell_number
    sequence_sheet = []
    if type(element) == ast.Call:
        args = []
        for arg in element.args:
            if type(arg) == ast.Call:
                sequence_sheet += create_sequence_sheet_entries(test, arg, cell_type)
                args.append(f"{cell_type}{cell_number - 1}")
            elif type(arg) == ast.List or type(arg) == ast.Tuple:
                sequence_sheet += create_sequence_sheet_entries(test, arg, cell_type)
                args.append(f"{cell_type}{cell_number - 1}")
            else:
                args.append(ast.get_source_segment(test, arg))
        function_name = element.func.id
        if function_name in dir(builtins):
            function_name = "python." + function_name.capitalize()
            sequence_sheet.append([f"{cell_type}{cell_number}", "create", function_name] + args)
        else:
            sequence_sheet.append([f"{cell_type}{cell_number}", function_name, ""] + args)
    elif type(element) == ast.List or type(element) == ast.Tuple:
        elts = []
        for elt in element.elts:
            if type(elt) == ast.Call:
                sequence_sheet += create_sequence_sheet_entries(test, elt, cell_type)
                elts.append(f"{cell_type}{cell_number - 1}")
            elif type(elt) == ast.List:
                sequence_sheet += create_sequence_sheet_entries(test, elt, cell_type)
                elts.append(f"{cell_type}{cell_number - 1}")
            else:
                elts.append(ast.get_source_segment(test, elt))
        if type(element) == ast.List:
            sequence_sheet.append([f"{cell_type}{cell_number}", "create", "python.List"] + elts)
        else:
            sequence_sheet.append([f"{cell_type}{cell_number}", "create", "python.Tuple"] + elts)
    else:
        sequence_sheet.append([f"result{cell_number}", ast.get_source_segment(test, element), ""])
    cell_number += 1
    return sequence_sheet


def generate_sequence_sheets(llm_file):
    global cell_number

    file = open(llm_file, 'r')
    tasks = json.load(file)
    sequence_sheets = {}
    for task in tasks:
        tests = task["test_list"]
        sequence_sheet = []
        cell_number = 1
        for test in tests:
            test_ast = ast.parse(test).body[0].test
            if type(test_ast) == ast.Compare:
                try:
                    right = create_sequence_sheet_entries(test, test_ast.comparators[0], "lasso_comp")
                    left = create_sequence_sheet_entries(test, test_ast.left, "lasso_test")
                    if "result" in right[-1][0]:
                        left[-1][0] = right[-1][1]
                        right.pop(-1)
                    else:
                        left[-1][0] = "res_" + right[-1][0]
                    sequence_sheet += (right + left)
                except Exception as e:
                    print(e)
                    pass
        first_row = [x[0] for x in sequence_sheet]
        for i, element in enumerate(first_row):
            if "res_" in element:
                sequence_sheet[i][0] = f"A{first_row.index(element[4:]) + 2}"
            elif "lasso_comp" in element or "lasso_test" in element:
                sequence_sheet[i][0] = ""
        for i_1, row in enumerate(sequence_sheet):
            for i_2, element in enumerate(row):
                if "lasso_test" in element or "lasso_comp" in element:
                    sequence_sheet[i_1][i_2] = f"A{first_row.index(element) + 2}"
        sequence_sheet = [["", "create", f"Task{task['task_id']}", ""]] + sequence_sheet
        sequence_sheets[task['task_id']] = sequence_sheet
    return sequence_sheets

def create_lql(task):
    task_ast = ast.parse(task["code"])
    lql = [f"Task{task['task_id']}"]
    for element in task_ast.body:
        if type(element) == ast.FunctionDef:
            arg_count = len(element.args.args)
            lql.append(f"{element.name}({','.join(['Any' for _ in range(arg_count)])})->Any")
    lql = f'{lql[0]} <begin>' + "\n\t".join([""] + lql[1:]) + "\n<end>"
    lql = lql.replace("<begin>", "{").replace("<end>", "}")
    return lql

if __name__ == "__maind__":
    sequence_sheets = generate_sequence_sheets("evaluation_sanitized-mbpp.json")
    for task_id in sequence_sheets.keys():
        if task_id <= 101 or task_id >= 120:
            continue
        pd.DataFrame(sequence_sheets[task_id]).to_excel(f"evaluation_sheets/llm_sequence_sheets/{task_id}.xlsx", index=False, header=False)


if __name__ == "__main__":
    llm_file = open("evaluation_sanitized-mbpp.json", 'r')
    tasks = json.load(llm_file)
    
    lassoIgniteClient = LassoIgniteClient()

    executionId = uuid.uuid4()

    for index, task in enumerate(tasks):

        task_id = task["task_id"]

        wip = [2, 3, 4, 6, 8, 9, 11, 12, 14, 16, 17, 18, 19, 20, 56, 57, 58, 59, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 74, 75, 77, 79, 80, 83, 84, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 99, 102, 103, 104, 105, 106, 108, 109, 111, 113, 115, 116, 118, 119]
        if task_id not in wip:
            continue

        lql_string = create_lql(task)
        print(lql_string)

        interfaceSpecification = parse_interface_spec(lql_string)

        sequenceSpecification = SequenceSpecification(f"./evaluation_sheets/{task_id}.xlsx")

        solr_url = "http://localhost:8983/solr/lasso_quickstart"
        solr_conn = LassoSolrConnector(solr_url)

        allModulesUnderTest, required_packages = solr_conn.generate_modules_under_test(interfaceSpecification)

        print(required_packages)

        imp_helper = import_helper.ImportHelper(runtime=True)
        nexus = Nexus()
        for package in required_packages:
            package_name, version = package.split("==")
            pkg = Package(package_name, version)
            nexus.download(pkg)
            imp_helper.pre_load_package(package_name, version)
            dependencies = import_helper.get_dependencies(package_name, version)
            for dep_name in dependencies:
                dep_version = dependencies[dep_name]['version']
                imp_helper.pre_load_package(dep_name, dep_version)

        # Iterate through all modules under test
        for moduleUnderTest in allModulesUnderTest:
            adaptationHandler = AdaptationHandler(
                interfaceSpecification,
                moduleUnderTest,
                maxParamPermutationTries=1,
                onlyKeepTopNMappings=1,
            )
            adaptationHandler.identifyAdaptations()
            adaptationHandler.identifyConstructorAdaptations()
            adaptationHandler.visualizeAdaptations()
            adaptationHandler.generateMappings()

            executionEnvironment = ExecutionEnvironment(
                adaptationHandler.mappings,
                sequenceSpecification,
                interfaceSpecification,
                executionId=executionId,
                recordMetrics=True,
            )

            execute_test(
                executionEnvironment,
                adaptationHandler,
                moduleUnderTest.moduleName,
            )

            executionEnvironment.printResults()
            executionEnvironment.saveResults(lassoIgniteClient)
            break # NOTE only use the first module as the names perfectly match and the first search result is the one we want
    
    df = lassoIgniteClient.getDataFrame()
    df.to_csv("evaluation_results.csv", index=False)
