import pysolr
from adaptation import AdaptationHandler, create_adapted_module
from backend.arena.run import move
from execution import execute_test
from backend.lql.antlr_parser import parse_interface_spec
from solr_parser import parse_solr_response
from backend.arena.lasso_solr_connector import LassoSolrConnector
from stimulus_sheet_reader import get_stimulus_sheet
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


#TODO: Dynamic?
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

    solr_url = "http://localhost:8983/solr/lasso_quickstart"
    solr_conn = LassoSolrConnector(solr_url)

    allModulesUnderTest, required_packages = solr_conn.generate_modules_under_test(interfaceSpecification)
    loaded_folders = []
    for package in required_packages:
        package_name, version = package.split("==")
        loaded_folders += move(package_name, version)

    moduleUnderTest = allModulesUnderTest[0]  # only take the first module for now

    adaptationHandler = AdaptationHandler(
        interfaceSpecification,
        moduleUnderTest,
        excludeClasses=False,
        useFunctionDefaultValues=False,
    )
    adaptationHandler.identifyAdaptations(maxParamPermutationTries=2)
    adaptationHandler.visualizeAdaptations()
    adaptationHandler.generateMappings(onlyKeepTopN=10)

    (adapted_module, successful_mappings) = create_adapted_module(
        adaptationHandler,
        moduleUnderTest.moduleName,
        use_constructor_default_values=True,
    )

    stimulus_sheet = get_stimulus_sheet("calc4_demo.csv")
    allSequenceExecutionRecords = execute_test(stimulus_sheet, adapted_module, successful_mappings, interfaceSpecification)
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
