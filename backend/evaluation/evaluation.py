import os
import uuid
import pandas as pd
import git
import sys
import re

from tqdm import tqdm

repo = git.Repo(search_parent_directories=True)
sys.path.insert(0, repo.working_tree_dir)

from backend.crawl.crawl_pipeline import index_package
from backend.crawl import import_helper
from backend.crawl.nexus import Nexus, Package
from backend.arena.lasso_solr_connector import LassoSolrConnector
from backend.arena.sequence_specification import SequenceSpecification
from backend.arena.ignite import LassoIgniteClient
from backend.arena.adaptation_identification import AdaptationHandler
from backend.arena.execution import execute_test, ExecutionEnvironment
from backend.arena.lql.antlr_parser import parse_interface_spec

import builtins
import ast
import json


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


if __name__ == "__main__":
    llm_file = open("evaluation_sanitized-mbpp.json", 'r')

    index_package("lasso-llm", llm_file="evaluation_sanitized-mbpp.json")

    tasks = json.load(llm_file)

    lassoIgniteClient = LassoIgniteClient()

    executionId = uuid.uuid4()

    imp_helper = import_helper.ImportHelper(runtime=True)
    nexus = Nexus()
    package_name, version = ("lasso-llm", "0.0.1")
    pkg = Package(package_name, version)
    nexus.download(pkg)
    imp_helper.pre_load_package(package_name, version)

    for index, task in enumerate(tqdm(tasks)):

        task_id = task["task_id"]

        lql_string = create_lql(task)
        print(lql_string)

        interfaceSpecification = parse_interface_spec(lql_string)

        sequenceSpecification = SequenceSpecification(f"./evaluation_sheets/llm_sequence_sheets/{task_id}.xlsx")

        solr_url = "http://localhost:8983/solr/lasso_python"
        solr_conn = LassoSolrConnector(solr_url)

        allModulesUnderTest, required_packages = solr_conn.generate_modules_under_test(interfaceSpecification)



        # Iterate through all modules under test
        for moduleUnderTest in [x for x in allModulesUnderTest if "lasso-llm" in x.moduleName]:
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
