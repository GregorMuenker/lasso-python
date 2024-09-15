import uuid
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
from backend.arena.lql.antlr_parser import parse_interface_spec
from backend.crawl.crawl_pipeline import index_package

"""
For this demo to work you need to:
- have the Solr instance lasso_quickstart running on localhost:8983
- have an Apache Ignite instance running on localhost:10800
- have a Nexus instance running on localhost:8081
"""


if __name__ == "__main__":
    # NOTE: Please install numpy version 1.26.4 locally on your machine:
    # pip install --force-reinstall numpy==1.26.4

    # Crawl, analyize and index the numpy package
    index_package("numpy==1.26.4", type_inferencing_engine="HiTyper")

    # Manually generate an execution identifier that will be used when storing results in Ignite
    executionId = uuid.uuid4()
    
    # Define an LQL interface specification
    lql_string = """
    Matrix {
        Matrix(list)->None
        mean()->Any
    }
    """
    interfaceSpecification = parse_interface_spec(lql_string)
    print(interfaceSpecification)

    # Define a set of sequence sheets
    sequenceSpecifications = [SequenceSpecification("execution_sheets/calc7_greg.xlsx"), SequenceSpecification("execution_sheets/calc8.xlsx")]

    # Setup Ignite client for storing results
    lassoIgniteClient = LassoIgniteClient()

    # Connect to Solr
    solr_url = "http://localhost:8983/solr/lasso_python"
    solr_conn = LassoSolrConnector(solr_url)

    # Retrieve all modules that meet the interface specification from Solr
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

        # Iterate through all sequence sheets
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
    

    # Finally, print the results stored in Ignite
    df = lassoIgniteClient.getDataFrame()
    print(df)
