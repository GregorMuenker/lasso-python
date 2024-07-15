import unittest
from adaptation import adapt_function

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


if __name__ == '__main__':
    unittest.main()
