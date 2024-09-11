if __name__ == "__main__":
    from execution import execute_test, ExecutionEnvironment
    from module_parser import parse_code
    from sequence_specification_greg import SequenceSpecification
    from adaptation_identification import AdaptationHandler
    from lql.antlr_parser import parse_interface_spec
    from ignite import LassoIgniteClient

    lql_string = """
    Calculator {
        Calculator(int)->None
        addme(int)->int
        subme(int)->int
    }
    """

    interfaceSpecification = parse_interface_spec(lql_string)
    print(interfaceSpecification)

    sequenceSpecification = SequenceSpecification("arena_development.xlsx")
    print(sequenceSpecification.sequenceSheet)

    # Read source code directly from a file. NOTE: This path can also be changed to a sitepackage file (e.g., numpy.lib.scimath.py).
    path = "./test_data_file.py"
    with open(path, "r") as file:
        file_content = file.read()
        moduleUnderTest = parse_code(file_content, "Test")

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

    executionEnvironment = ExecutionEnvironment(
        adaptationHandler.mappings,
        sequenceSpecification,
        interfaceSpecification,
        recordMetrics=True,
    )

    execute_test(
        executionEnvironment,
        adaptationHandler,
        moduleUnderTest.moduleName,
        import_from_file_path=path,
    )

    executionEnvironment.printResults()

    lassoIgniteClient = LassoIgniteClient()
    try:
        executionEnvironment.saveResults(lassoIgniteClient)
        df = lassoIgniteClient.getDataFrame()
        print(df)
        # df.to_csv("arena_development.csv", index=False)
    except Exception as e:
        print(f"Error with Ignite: {e}")

    lassoIgniteClient.cache.destroy()
    lassoIgniteClient.client.close()
