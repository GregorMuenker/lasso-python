from adaptation_identification import AdaptationHandler
from execution import execute_test, ExecutionEnvironment
from lql.antlr_parser import parse_interface_spec
from solr_parser import parse_solr_response
import git
import sys

repo = git.Repo(search_parent_directories=True)
sys.path.insert(0, repo.working_tree_dir)

from backend.crawl import import_helper
from backend.crawl.nexus import Nexus, Package
from backend.arena.lasso_solr_connector import LassoSolrConnector
from sequence_specification import SequenceSpecification
from ignite import LassoIgniteClient

if __name__ == "__main__":
    lql_string = """
    Task2 {
        similar_elements(tuple, tuple)->set
    }
    """

    interfaceSpecification = parse_interface_spec(lql_string)

    sequenceSpecification = SequenceSpecification("./evaluation_sheets/2.xlsx")

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
        # imp_helper.pre_load_package(package_name, version)
        # dependencies = import_helper.get_dependencies(package_name, version)
        # for dep_name in dependencies:
        #     dep_version = dependencies[dep_name]['version']
        #     imp_helper.pre_load_package(dep_name, dep_version)


    # Setup Ignite client
    # lassoIgniteClient = LassoIgniteClient()
    
    # # Iterate through all modules under test
    # for moduleUnderTest in allModulesUnderTest:
    #     adaptationHandler = AdaptationHandler(
    #         interfaceSpecification,
    #         moduleUnderTest,
    #         maxParamPermutationTries=2,
    #         onlyKeepTopNMappings=10,
    #     )
    #     adaptationHandler.identifyAdaptations()
    #     adaptationHandler.identifyConstructorAdaptations()
    #     adaptationHandler.visualizeAdaptations()
    #     adaptationHandler.generateMappings()

    #     executionEnvironment = ExecutionEnvironment(
    #         adaptationHandler.mappings,
    #         sequenceSpecification,
    #         interfaceSpecification,
    #         recordMetrics=True,
    #     )

    #     execute_test(
    #         executionEnvironment,
    #         adaptationHandler,
    #         moduleUnderTest.moduleName,
    #         import_from_file_path = path,
    #     )

    #     executionEnvironment.printResults()
    #     executionEnvironment.saveResults(lassoIgniteClient)
    

    # df = lassoIgniteClient.getDataFrame()
    # print(df)

    # lassoIgniteClient.cache.destroy()
    # lassoIgniteClient.client.close()
