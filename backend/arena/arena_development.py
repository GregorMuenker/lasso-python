if __name__ == "__main__":
    from execution import execute_test, ExecutionEnvironment
    from module_parser import parse_code
    from sequence_specification import SequenceSpecification
    from adaptation_implementation import create_adapted_module
    from adaptation_identification import AdaptationHandler
    from lql.antlr_parser import parse_interface_spec
    from ignite import LassoIgniteClient

    lql_string = """
    Calculator {
        Calculator(int)->None
        iminus(float, int)->float
        icubed(int)->set
    }
    """

    interfaceSpecification = parse_interface_spec(lql_string)
    print(interfaceSpecification)

    sequenceSpecification = SequenceSpecification("calc3_adaptation.xlsx")
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
        onlyKeepTopNMappings=10,
        allowStandardValueConstructorAdaptations=True,
    )
    adaptationHandler.identifyAdaptations()
    adaptationHandler.identifyConstructorAdaptations()
    adaptationHandler.visualizeAdaptations()
    adaptationHandler.generateMappings()

    executionEnvironment = ExecutionEnvironment(
        adaptationHandler.mappings, sequenceSpecification, interfaceSpecification
    )

    adapted_module = create_adapted_module(
        adaptationHandler,
        moduleUnderTest.moduleName,
        executionEnvironment,
        import_from_file_path="./test_data_file.py",
    )

    execute_test(adapted_module, executionEnvironment)

    executionEnvironment.printResults()

    # TODO enable ignite support, current bug: if create statement row record is read in execution.py toSheetCells()
    # lassoIgniteClient = LassoIgniteClient()
    # executionEnvironment.saveResults(lassoIgniteClient)

    # df = lassoIgniteClient.getDataFrame()
    # print(df)

    # lassoIgniteClient.cache.destroy()
    # lassoIgniteClient.client.close()
