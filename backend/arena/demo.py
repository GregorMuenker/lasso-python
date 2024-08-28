import pysolr
from adaptation_identification import AdaptationHandler
from adaptation_implementation import create_adapted_module
from execution import execute_test, ExecutionEnvironment
from lql.antlr_parser import parse_interface_spec
from solr_parser import parse_solr_response
from solr_query import translate_to_solr_query
from sequence_specification import SequenceSpecification
from ignite import LassoIgniteClient

"""
For this demo to work you need to:
- have the Solr instance lasso_quickstart running on localhost:8983
- have an Apache Ignite instance running
    1. download Apache Ignite binaries (NOT SOURCE FILES) version 2.16.0 from https://ignite.apache.org/download.cgi#binaries
    2. unzip the zip archive
    3. navigate to the bin folder in the unzipped folder
    4. run ignite.bat (Windows) or ignite.sh (Unix) via the command line
- alternatively comment out the part starting from "lassoIgniteClient = LassoIgniteClient() ..."
"""


# TODO: Dynamic?
if __name__ == "__main__":
    lql_string = """
    Calculator {
        Calculator(int)->None
        log(int, int)->float
        sqrd(int)->float
    }
    """

    interfaceSpecification = parse_interface_spec(lql_string)
    print(interfaceSpecification)

    sequenceSpecification = SequenceSpecification("calc4_demo.xlsx")

    solr_url = "http://localhost:8983/solr/lasso_quickstart"
    solr = pysolr.Solr(solr_url)
    solr_query = translate_to_solr_query(interfaceSpecification)
    print("QUERY:", solr_query)
    results = solr.search(solr_query)
    print(f"Found {len(results)} results")

    allModulesUnderTest = parse_solr_response(results)
    moduleUnderTest = allModulesUnderTest[0]  # only take the first module for now

    adaptationHandler = AdaptationHandler(
        interfaceSpecification,
        moduleUnderTest,
        maxParamPermutationTries=2,
        onlyKeepTopNMappings=10,
    )
    adaptationHandler.identifyAdaptations()
    adaptationHandler.identifyConstructorAdaptations()
    adaptationHandler.visualizeAdaptations()
    adaptationHandler.generateMappings()

    executionEnvironment = ExecutionEnvironment(
        adaptationHandler.mappings, sequenceSpecification, interfaceSpecification
    )

    adapted_module = create_adapted_module(
        adaptationHandler,
        moduleUnderTest.moduleName,
        executionEnvironment,
    )

    allSequenceExecutionRecords = execute_test(
        adapted_module,
        executionEnvironment,
    )

    executionEnvironment.printResults()

    lassoIgniteClient = LassoIgniteClient()
    executionEnvironment.saveResults(lassoIgniteClient)

    df = lassoIgniteClient.getDataFrame()
    print(df)

    lassoIgniteClient.cache.destroy()
    lassoIgniteClient.client.close()
