import uuid
import git
import sys

repo = git.Repo(search_parent_directories=True)
sys.path.insert(0, repo.working_tree_dir)

from backend.arena.lasso_solr_connector import LassoSolrConnector
from backend.arena.sequence_specification import SequenceSpecification
from backend.arena.ignite import LassoIgniteClient
from backend.arena.adaptation_identification import AdaptationHandler
from backend.arena.execution import execute_test, ExecutionEnvironment
from backend.arena.lql.antlr_parser import parse_interface_spec
from backend.arena.module_parser import parse_code


if __name__ == "__main__":

    # Manually generate an execution identifier that will be used when storing results in Ignite
    executionId = uuid.uuid4()
    
    # Define an LQL interface specification
    # NOTE: peek of deque is realized via builtin __getitem__(-1) and length via builtin __len__()
    lql_string = """
    Stack {
        Stack()->None
        append(Any)->None
        appendleft(Any)->None
        pop()->Any
        clear()->None
    }
    """
    interfaceSpecification = parse_interface_spec(lql_string)
    print(interfaceSpecification)

    # Read in a sequence sheet which defines the test
    sequenceSpecification = SequenceSpecification("execution_sheets/stack.xlsx")
    print(sequenceSpecification.sequenceSheet)

    # Read source code of the stack interface
    path = "./stack_interface.py"
    with open(path, "r") as file:
        file_content = file.read()
        moduleUnderTest = parse_code(file_content, "Stack")

    # Set up and run an adaptation handler that will identify and generate mappings
    adaptationHandler = AdaptationHandler(
        interfaceSpecification,
        moduleUnderTest,
        onlyKeepTopNMappings=1,
    )
    adaptationHandler.identifyAdaptations()
    adaptationHandler.identifyConstructorAdaptations()
    adaptationHandler.visualizeAdaptations()
    adaptationHandler.generateMappings()

    # Manually set the execution identifier for this example which will be saved to Ignite at the end
    executionId = uuid.uuid4()

    # Set up the execution environment, run the test, and print the results
    executionEnvironment = ExecutionEnvironment(
        adaptationHandler.mappings,
        sequenceSpecification,
        interfaceSpecification,
        recordMetrics=True,
        executionId=executionId,
        actionId="PLACEHOLDER",
    )
    execute_test(
        executionEnvironment,
        adaptationHandler,
        moduleUnderTest.moduleName,
        import_from_file_path=path,
    )
    executionEnvironment.printResults()

    # Save the results to Ignite
    # lassoIgniteClient = LassoIgniteClient()
    # try:
    #     executionEnvironment.saveResults(lassoIgniteClient)
    #     df = lassoIgniteClient.getDataFrame()
    #     print(df)
    #     # df.to_csv("arena_development_results.csv", index=False) # NOTE: Uncomment this line to save the results to a CSV file.
    # except Exception as e:
    #     print(f"Error with Ignite: {e}")
    # # NOTE: Cache is destroyed and closed here to keep the example clean. In a real-world scenario, the cache should likely be kept open.
    # lassoIgniteClient.cache.destroy()
    # lassoIgniteClient.client.close()
