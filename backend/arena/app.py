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

@app.post("/arena/{execution_sheets}")
async def execute(execution_sheets: str, request: Request):
    
    maxParamPermutationTries = int(request.query_params.get('maxParamPermutationTries', 1))
    typeStrictness = bool(request.query_params.get('typeStrictness', False))
    onlyKeepTopNMappings = int(request.query_params.get('onlyKeepTopNMappings', 10))
    allowStandardValueConstructorAdaptations = bool(request.query_params.get('allowStandardValueConstructorAdaptations', True))
    actionId = request.query_params.get('actionId', os.getenv("ACTIONID",'PLACEHOLDER') )
    recordMetrics = bool(request.query_params.get('recordMetrics', True))
    
    # Get the LQL string from the request body
    body = await request.body()
    lql_string = body.decode("utf-8") or """
    Calculator {
        Calculator(int)->None
        addme(int)->int
        subme(int)->int
    }
    """
    
    # Generate a unique execution ID
    executionId = uuid.uuid4()
    
    # Parse the LQL string to get the interface specification
    interfaceSpecification = parse_interface_spec(lql_string)
    print(interfaceSpecification)
    # Get the sequence specifications from the execution sheets
    sequenceSpecifications = [SequenceSpecification('/app/execution_sheets/'+execution_sheet) for execution_sheet in execution_sheets.split(";")]
    
    # Setup Solr connection
    solr_url = os.getenv("SOLR_URL", "http://localhost:8983/solr/") + os.getenv("SOLR_COLLECTION", "lasso_python")
    solr_conn = LassoSolrConnector(solr_url)

    # Setup Ignite client
    lassoIgniteClient = LassoIgniteClient()
    
    # Generate all modules under test
    allModulesUnderTest, required_packages = solr_conn.generate_modules_under_test(interfaceSpecification)

    # Download and import all required packages from Nexus
    imp_helper = import_helper.ImportHelper(runtime=True)
    nexus = Nexus()
    for package in required_packages:
        package_name, version = package.split("==")
        pkg = Package(package_name, version)
        nexus.download(pkg)
        imp_helper.pre_load_package(package_name, version)
    
    # Iterate through all modules under test
    for moduleUnderTest in allModulesUnderTest:
        # Identify adaptations
        adaptationHandler = AdaptationHandler(
            interfaceSpecification,
            moduleUnderTest,
            maxParamPermutationTries=maxParamPermutationTries,
            onlyKeepTopNMappings=onlyKeepTopNMappings,
            typeStrictness=typeStrictness,
            allowStandardValueConstructorAdaptations=allowStandardValueConstructorAdaptations
        )
        adaptationHandler.identifyAdaptations()
        adaptationHandler.identifyConstructorAdaptations()
        adaptationHandler.visualizeAdaptations()
        adaptationHandler.generateMappings()
        
        # Iterate through all sequence specifications and execute tests
        for sequenceSpecification in sequenceSpecifications:
            executionEnvironment = ExecutionEnvironment(
                adaptationHandler.mappings,
                sequenceSpecification,
                interfaceSpecification,
                executionId=executionId,
                actionId=actionId,
                recordMetrics=recordMetrics,
            )

            execute_test(
                executionEnvironment,
                adaptationHandler,
                moduleUnderTest.moduleName,
            )
            
            # Print and save results
            executionEnvironment.printResults()
            executionEnvironment.saveResults(lassoIgniteClient)
    
    # Get the results from Ignite for further analysis
    df = lassoIgniteClient.getDataFrame()
    print(df)
    df.to_csv(f"/arena/results/{executionId}.csv")

    lassoIgniteClient.cache.destroy()
    lassoIgniteClient.client.close()
    return df.to_dict(orient="records")

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
