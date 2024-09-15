if __name__ == "__main__":
    import uuid
    import sys
    import git

    repo = git.Repo(search_parent_directories=True)
    sys.path.insert(0, repo.working_tree_dir)

    from backend.arena.execution import execute_test, ExecutionEnvironment
    from backend.arena.module_parser import parse_code
    from backend.arena.sequence_specification import SequenceSpecification
    from backend.arena.adaptation_identification import AdaptationHandler
    from backend.arena.lql.antlr_parser import parse_interface_spec
    from backend.arena.ignite import LassoIgniteClient

    lql_string = """
    Matrix {
        Calculator(int)->None
        multiply(int)->Any
        power(int)->Any
    }
    """

    interfaceSpecification = parse_interface_spec(lql_string)
    print(interfaceSpecification)

    sequenceSpecification = SequenceSpecification("execution_sheets/arena_numpy.xlsx")
    print(sequenceSpecification.sequenceSheet)

    # Read source code directly from a file.
    path = "/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages/numpy/matrixlib/defmatrix.py"
    with open(path, "r") as file:
        file_content = file.read()
        moduleUnderTest = parse_code(file_content, "numpy.matrixlib.defmatrix")

    adaptationHandler = AdaptationHandler(
        interfaceSpecification,
        moduleUnderTest,
        excludeClasses=False,
        useFunctionDefaultValues=False,
        maxParamPermutationTries=2,
        typeStrictness=False,
        onlyKeepTopNMappings=10,
        allowStandardValueConstructorAdaptations=True,
    )
    adaptationHandler.identifyAdaptations()
    adaptationHandler.identifyConstructorAdaptations()
    adaptationHandler.visualizeAdaptations()
    adaptationHandler.generateMappings()

    executionEnvironment = ExecutionEnvironment(
        adaptationHandler.mappings,
        sequenceSpecification,
        interfaceSpecification,
        executionId=uuid.uuid4(),
        actionId="PLACEHOLDER",
        recordMetrics=True,
    )

    execute_test(
        executionEnvironment,
        adaptationHandler,
        moduleUnderTest.moduleName,
    )

    executionEnvironment.printResults()

    lassoIgniteClient = LassoIgniteClient()
    try:
        executionEnvironment.saveResults(lassoIgniteClient)
        df = lassoIgniteClient.getDataFrame()
        print(df)
    except Exception as e:
        print(f"Error with Ignite: {e}")

    lassoIgniteClient.cache.destroy()
    lassoIgniteClient.client.close()
