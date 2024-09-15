if __name__ == "__main__":
    """
    This script can be used to develop the arena backend with a minimal setup, i.e. without having to care about Solr or Nexus instances.
    In this script, the results are saved into Ignite at the end which means that an Ignite instance has to be running on localhost:10800.
    However, if saving results to Ignite is not needed, the last part can simply be removed.

    To execute this script, navigate to the directory `backend/arena` and run `python arena_development.py` in the terminal.
    """
    
    import uuid
    import sys
    import git
    repo = git.Repo(search_parent_directories=True)
    sys.path.insert(0, repo.working_tree_dir)
    
    from execution import execute_test, ExecutionEnvironment
    from module_parser import parse_code
    from sequence_specification import SequenceSpecification
    from adaptation_identification import AdaptationHandler
    from backend.arena.lql.antlr_parser import parse_interface_spec
    from ignite import LassoIgniteClient

    # Define the LQL interface specification which will be used for searching, adapting and executing methods
    lql_string = """
    Calculator {
        Calculator(int)->None
        addme(int)->int
        subme(int)->int
    }
    """
    interfaceSpecification = parse_interface_spec(lql_string)
    print(interfaceSpecification)

    # Read in a sequence sheet which defines the test
    sequenceSpecification = SequenceSpecification("execution_sheets/arena_development.xlsx")
    print(sequenceSpecification.sequenceSheet)

    # Read source code of the Python module to test directly from a file. NOTE: This path can also be changed to a sitepackage file.
    path = "./test_data_file.py"
    with open(path, "r") as file:
        file_content = file.read()
        moduleUnderTest = parse_code(file_content, "Test")

    # Set up and run an adaptation handler that will identify and generate mappings
    adaptationHandler = AdaptationHandler(
        interfaceSpecification,
        moduleUnderTest,
        excludeClasses=False,
        useFunctionDefaultValues=False,
        maxParamPermutationTries=2,
        typeStrictness=False,
        onlyKeepTopNMappings=5,
        allowStandardValueConstructorAdaptations=True,
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
    )
    execute_test(
        executionEnvironment,
        adaptationHandler,
        moduleUnderTest.moduleName,
        import_from_file_path=path,
    )
    executionEnvironment.printResults()

    # Save the results to Ignite
    lassoIgniteClient = LassoIgniteClient()
    try:
        executionEnvironment.saveResults(lassoIgniteClient)
        df = lassoIgniteClient.getDataFrame()
        print(df)
        # df.to_csv("arena_development_results.csv", index=False) # NOTE: Uncomment this line to save the results to a CSV file.
    except Exception as e:
        print(f"Error with Ignite: {e}")
    # NOTE: Cache is destroyed and closed here to keep the example clean. In a real-world scenario, the cache should likely be kept open.
    lassoIgniteClient.cache.destroy()
    lassoIgniteClient.client.close()
