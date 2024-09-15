"""app.py - This file contains REST API."""

import os
import uvicorn
from fastapi import FastAPI, Request
import uuid
from dotenv import load_dotenv
load_dotenv()

import import_helper
from nexus import Nexus, Package
from lasso_solr_connector import LassoSolrConnector
from sequence_specification import SequenceSpecification
from ignite import LassoIgniteClient
from adaptation_identification import AdaptationHandler
from execution import execute_test, ExecutionEnvironment
from lql.antlr_parser import parse_interface_spec

app = FastAPI()

@app.post("/arena/{execution_sheet}")
async def execute(execution_sheet: str, request: Request):
    
    body = await request.body()
    lql_string = body.decode("utf-8") or """
    Calculator {
        Calculator(int)->None
        addme(int)->int
        subme(int)->int
    }
    """

    executionId = uuid.uuid4()

    interfaceSpecification = parse_interface_spec(lql_string)
    print(interfaceSpecification)

    sequenceSpecifications = [SequenceSpecification('/app/execution_sheets/'+execution_sheet)]

    solr_url = os.getenv("SOLR_URL", "http://localhost:8983/solr/") + os.getenv("SOLR_COLLECTION", "lasso_python")
    solr_conn = LassoSolrConnector(solr_url)

    # Setup Ignite client
    lassoIgniteClient = LassoIgniteClient()

    allModulesUnderTest, required_packages = solr_conn.generate_modules_under_test(interfaceSpecification)

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
            maxParamPermutationTries=2,
            onlyKeepTopNMappings=10,
        )
        adaptationHandler.identifyAdaptations()
        adaptationHandler.identifyConstructorAdaptations()
        try:
            adaptationHandler.visualizeAdaptations()
        except:
            print("Could not visualize adaptations")
        adaptationHandler.generateMappings()

        for sequenceSpecification in sequenceSpecifications:
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
    

    df = lassoIgniteClient.getDataFrame()
    print(df)

    lassoIgniteClient.cache.destroy()
    lassoIgniteClient.client.close()
    return "Done"

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
