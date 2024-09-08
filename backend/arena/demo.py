import pysolr
from adaptation_identification import AdaptationHandler
from adaptation_implementation import create_adapted_module
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
from sequence_specification_greg import SequenceSpecification
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
    Matrix {
        Matrix(arr)->None
        mean()->Any
    }
    """

    interfaceSpecification = parse_interface_spec(lql_string)
    print(interfaceSpecification)

    sequenceSpecification = SequenceSpecification("calc7_greg.xlsx")

    solr_url = "http://localhost:8983/solr/lasso_quickstart"
    solr_conn = LassoSolrConnector(solr_url)

    allModulesUnderTest, required_packages = solr_conn.generate_modules_under_test(interfaceSpecification)

    imp_helper = import_helper.ImportHelper(runtime=True)
    nexus = Nexus()
    for package in required_packages:
        package_name, version = package.split("==")
        pkg = Package(package_name, version, f"{package_name}-{version}.tar.gz", f"{package_name}/{version}")
        nexus.download(pkg)
        imp_helper.pre_load_package(package_name, version)
        dependencies = import_helper.get_dependencies(package_name, version)
        for dep_name in dependencies:
            dep_version = dependencies[dep_name]['version']
            imp_helper.pre_load_package(dep_name, dep_version)



    #moduleUnderTest = allModulesUnderTest[0]  # only take the first module for now
    for moduleUnderTest in allModulesUnderTest:
        adaptationHandler = AdaptationHandler(
            interfaceSpecification,
            moduleUnderTest,
            maxParamPermutationTries=2,
            onlyKeepTopNMappings=10,
        )
        adaptationHandler.identifyAdaptations()
        adaptationHandler.identifyConstructorAdaptations()
        # adaptationHandler.visualizeAdaptations()
        adaptationHandler.generateMappings()

        executionEnvironment = ExecutionEnvironment(
            adaptationHandler.mappings,
            sequenceSpecification,
            interfaceSpecification,
        )

        execute_test(
            executionEnvironment,
            adaptationHandler,
            moduleUnderTest.moduleName,
            # import_from_file_path = path,
        )

        executionEnvironment.printResults()

    #lassoIgniteClient = LassoIgniteClient()
    #executionEnvironment.saveResults(lassoIgniteClient)
    #df = lassoIgniteClient.getDataFrame()
    #print(df)


    #lassoIgniteClient.cache.destroy()
    #lassoIgniteClient.client.close()
