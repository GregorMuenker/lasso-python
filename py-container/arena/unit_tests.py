import unittest
from adaptation import adapt_function, can_convert_params, can_convert_type

class ExampleFunctions:
    
    def returns_param_order(self, a: float, b: float, c: str, d: int):
        return(f"arg 1: {a}, arg 2: {b}, arg 3: {c}, arg 4: {d}")
    
    def subtract(self, a: int, b: float):
        return a - b

class TestAdaptation(unittest.TestCase):

    def test_adapt_parameter_order(self):
        exampleFunctions = ExampleFunctions()
        function = exampleFunctions.returns_param_order
        adapted_function = adapt_function(function, new_return_type = None, convert_to_types = None, current_param_order = ['float', 'float', 'str', 'int'], new_param_order = ['str', 'int', 'float', 'float'])
        result = function(1.0, 2.0, "abc", 4)
        adapted_result = adapted_function("abc", 4, 1.0, 2.0)
        self.assertEqual(result, adapted_result)

    def test_adapt_return_type_and_parameter_order(self):
        exampleFunctions = ExampleFunctions()
        function = exampleFunctions.subtract
        adapted_function = adapt_function(function, new_return_type = "str", convert_to_types = None, current_param_order = ['int', 'float'], new_param_order = ['float', 'int'])
        result = function(10, 4)
        adapted_result = adapted_function(4, 10)
        self.assertEqual(result, int(adapted_result))
        self.assertIsInstance(adapted_result, str)

    def test_can_convert_params(self):
        source_types_1 = ['int', 'float']
        target_types_1 = ['float', 'int']
        self.assertTrue(can_convert_params(source_types_1, target_types_1))

        source_types_2 = ['int', 'float', 'str']
        target_types_2 = ['float', 'int', 'Any']
        self.assertFalse(can_convert_params(source_types_2, target_types_2))

    def test_can_convert_type(self):
        source_type_1 = 'int'
        target_type_1 = 'str'
        self.assertTrue(can_convert_type(source_type_1, target_type_1))

        source_type_2 = 'str'
        target_type_2 = 'Any'
        self.assertFalse(can_convert_type(source_type_2, target_type_2))


if __name__ == '__main__':
    unittest.main()
