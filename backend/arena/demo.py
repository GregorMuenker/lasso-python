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
from backend.lql.antlr_parser import parse_interface_spec

"""
For this demo to work you need to:
- have the Solr instance lasso_quickstart running on localhost:8983
- have an Apache Ignite instance running on localhost:10800
- have a Nexus instance running on localhost:8081
"""


if __name__ == "__main__":
    lql_string = """
    Matrix {
        Matrix(arr)->None
        mean()->Any
    }
    """

    executionId = uuid.uuid4()

    interfaceSpecification = parse_interface_spec(lql_string)
    print(interfaceSpecification)

    sequenceSpecifications = [SequenceSpecification("calc7_greg.xlsx"), SequenceSpecification("calc8.xlsx")]

    solr_url = "http://localhost:8983/solr/lasso_quickstart"
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
        adaptationHandler.visualizeAdaptations()
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
