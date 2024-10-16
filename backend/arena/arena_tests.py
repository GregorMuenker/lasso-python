import unittest
import sys
import git
repo = git.Repo(search_parent_directories=True)
sys.path.insert(0, repo.working_tree_dir)

from adaptation_identification import (
    can_convert_params,
    can_convert_type,
    find_permutation,
)
from adaptation_implementation import adapt_function


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

if __name__ == "__main__":
    unittest.main()
