import pysolr
from adaptation import AdaptationHandler, create_adapted_module
from execution import execute_test
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
        excludeClasses=False,
        useFunctionDefaultValues=False,
        maxParamPermutationTries=2,
        onlyKeepTopNMappings=10,
    )
    adaptationHandler.identifyAdaptations()
    adaptationHandler.visualizeAdaptations()
    adaptationHandler.generateMappings()

    (adapted_module, successful_mappings) = create_adapted_module(
        adaptationHandler,
        moduleUnderTest.moduleName,
        use_constructor_default_values=True,
    )

    allSequenceExecutionRecords = execute_test(
        sequenceSpecification,
        adapted_module,
        successful_mappings,
        interfaceSpecification,
    )
    for sequenceExecutionRecord in allSequenceExecutionRecords:
        print(sequenceExecutionRecord)

    lassoIgniteClient = LassoIgniteClient()
    for sequenceExecutionRecord in allSequenceExecutionRecords:
        cells = sequenceExecutionRecord.toSheetCells()
        lassoIgniteClient.putAll(cells)

    df = lassoIgniteClient.getDataFrame()
    print(df)

    lassoIgniteClient.cache.destroy()
    lassoIgniteClient.client.close()
    
