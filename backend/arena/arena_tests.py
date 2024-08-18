import unittest

from adaptation import (
    adapt_function,
    can_convert_params,
    can_convert_type,
    find_permutation,
)


class ExampleFunctions:

    def returns_param_order(self, a: float, b: float, c: str, d: int):
        return f"arg 1: {a}, arg 2: {b}, arg 3: {c}, arg 4: {d}"

    def subtract(self, a: int, b: float):
        return a - b


class TestAdaptation(unittest.TestCase):

    def test_adapt_parameter_order(self):
        exampleFunctions = ExampleFunctions()
        current_param_order = ["float", "float", "str", "int"]
        new_param_order = ["str", "int", "float", "float"]
        permutation = find_permutation(current_param_order, new_param_order)
        function = exampleFunctions.returns_param_order
        adapted_function = adapt_function(function, new_param_order=permutation)
        result = function(1.0, 2.0, "abc", 4)
        adapted_result = adapted_function("abc", 4, 1.0, 2.0)
        self.assertEqual(result, adapted_result)

    def test_adapt_return_type_and_parameter_order(self):
        exampleFunctions = ExampleFunctions()
        function = exampleFunctions.subtract
        current_param_order = ["int", "float"]
        new_param_order = ["float", "int"]
        permutation = find_permutation(current_param_order, new_param_order)
        adapted_function = adapt_function(
            function, new_return_type="str", new_param_order=permutation
        )
        result = function(10, 4)
        adapted_result = adapted_function(4, 10)
        self.assertEqual(result, int(adapted_result))
        self.assertIsInstance(adapted_result, str)

    def test_can_convert_params(self):
        source_types_1 = ["int", "float"]
        target_types_1 = ["float", "int"]
        self.assertTrue(can_convert_params(source_types_1, target_types_1))

        source_types_2 = ["int", "float", "str"]
        target_types_2 = ["float", "int", "Any"]
        self.assertFalse(can_convert_params(source_types_2, target_types_2))

    def test_can_convert_type(self):
        source_type_1 = "int"
        target_type_1 = "str"
        self.assertTrue(can_convert_type(source_type_1, target_type_1))

        source_type_2 = "str"
        target_type_2 = "Any"
        self.assertFalse(can_convert_type(source_type_2, target_type_2))

def test_arena():
    from execution import execute_test
    from module_parser import parse_code
    from stimulus_sheet_reader import get_stimulus_sheet
    from adaptation import AdaptationHandler, create_adapted_module
    from lql.antlr_parser import parse_interface_spec

    lql_string = """
    Matrix {
        Matrix(str)->None
        multiply(Any)->Any
        power(Any)->Any
    }
    """

    interfaceSpecification = parse_interface_spec(lql_string)
    print(interfaceSpecification)

    # Load source of specific file on disk
    path = "/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages/numpy/matrixlib/defmatrix.py"
    with open(path, "r") as file:
        file_content = file.read()
        moduleUnderTest = parse_code(file_content, "numpy.matrixlib.defmatrix") # Parse the file to obtain a ModuleUnderTest object

    adaptationHandler = AdaptationHandler(
        interfaceSpecification,
        moduleUnderTest,
        excludeClasses=False,
        useFunctionDefaultValues=False,
    )
    adaptationHandler.identifyAdaptations(maxParamPermutationTries=1)
    adaptationHandler.visualizeAdaptations()
    adaptationHandler.generateMappings(onlyKeepTopN=20)

    (adapted_module, successful_mappings) = create_adapted_module(
        adaptationHandler,
        moduleUnderTest.moduleName,
        class_instantiation_params=["1 2; 3 4"],
        use_constructor_default_values=True,
        testing_mode=False,
    )

    stimulus_sheet = get_stimulus_sheet("calc5_arena_tests.csv")
    execute_test(stimulus_sheet, adapted_module, successful_mappings)


if __name__ == "__main__":
    test_arena()
    unittest.main()