import pandas as pd
import types
from functools import partial

# read in excel and interpret it as stimulus sheet
def get_stimulus_sheet(path):
    df = pd.read_excel(path, header=None)
    
    # combine all input param columns into one list and drop null entries
    #input_params = pd.DataFrame(df.apply(lambda row: row[3:].tolist(), axis=1)) # also include empty params here
    input_params = pd.DataFrame(df.apply(lambda row: [x for x in row[3:] if pd.notnull(x)], axis=1))

    df = df.drop(df.columns[3:], axis=1) # drop all separate input_param columns
    df = pd.concat([df, input_params], axis=1) # concat with combined input_param column

    # create headers/column labels
    df.columns = ['output_param', 'method_name', 'instance_param', 'input_params']

    return df

class StimulusResponseMatrix:
    def __init__(self, implementations) -> None:
        self.implementations = implementations # {name1: implementation1, name2: implementation2, ...}
        self.tests = {} # name:stimulus_sheet
        self.results = {} # (implementation, test):result

    def add_implementation(self, name, code) -> None:
        self.implementations[name] = code

    def add_test(self, name, stimulus_sheet):
        self.tests[name] = stimulus_sheet

    def visualize_stimulus_matrix(self) -> None:
        df = pd.DataFrame(index=self.tests.keys())
        
        # create column for each implementation with value = "implementation_name, test_name"
        for implementation in self.implementations:
            df[implementation] = [f"{test}({implementation})" for test in self.tests.keys()]
        
        print(df)
    
    def visualize_results(self) -> None:
        # create DataFrame with test names as index and implementation names as columns
        df = pd.DataFrame(columns=list(self.implementations.keys()), index=list(self.tests.keys()))

        # fill in results for each cell
        for key, value in self.results.items():
            implementation_name, test_name = key
            # Assuming the result is a scalar that can be placed directly into the DataFrame
            df.at[test_name, implementation_name] = value

        print(df)
    
    # method for running all stimulus sheets for all implementations
    def run_tests(self) -> None:
      # loop through implementations
      for impl_name, impl_code in self.implementations.items():
          callables = self.get_callables_from_code(impl_code)
          print(callables)

          # loop through stimulus sheets
          for test_name, test_df in self.tests.items():
              test_results = []

              # loop through all rows in a stimulus sheet
              for _, row in test_df.iterrows():
                  method_name = row['method_name']
                  input_params = row['input_params'] # TODO better support for kwargs
                  # execute method found in row with parameters
                  row_result = self.find_and_execute_callable(callables, method_name, input_params)
                  test_results.append(row_result)

              # Store the result for implementation-test-pair TODO pyignite?
              self.results[(impl_name, test_name)] = test_results
    
    # helper method needed to identify all callables,
    # works for both functions and classes with methods
    def get_callables_from_code(self, code) -> dict:
        # dynamically execute code
        local_namespace = {}
        # TODO safety of calling directly with exec?
        exec(code, globals(), local_namespace)

        callables = {}
        for name, obj in local_namespace.items():
            if isinstance(obj, (types.FunctionType, types.MethodType)):
                # function or lambda
                callables[name] = {'type': 'function', 'callable': obj}
            elif isinstance(obj, type):
                # normal class, instantiate it to get methods
                # TODO handle classes that require initialization parameters
                callables[name] = {'type': 'class_instance', 'callable': obj()}
        
        return callables
    
    # helper method needed to find and execute a callable referenced in test
    def find_and_execute_callable(self, callables, method_name, input_params) -> any:
        for callable_name, callable_info in callables.items():
            # check if callable is a class instance
            if callable_info['type'] == 'class_instance':
                class_instance = callable_info['callable']
                if hasattr(class_instance, method_name):
                    # Directly access and call the method from the class instance
                    method = getattr(class_instance, method_name)
                    return method(*input_params)
            # check if callable is a function or lambda
            elif callable_info['type'] == 'function' and callable_name == method_name:
                function = callable_info['callable']
                return function(*input_params)
        else:
            # loop completes normally, i.e., no return was hit and the method/function wasn't found
            print(f"{method_name} not found")
            return None


# Example: create StimulusResponseMatrix from 2 stimulus sheets and two implementations
# and run tests on all implementations
stimulus_sheet1 = get_stimulus_sheet("calc1.xlsx")
stimulus_sheet2 = get_stimulus_sheet("calc2.xlsx")
implementation_code1 = """
class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b
"""
implementation_code2 = """
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
"""
implementation_code3 = """
add = lambda a, b: a + b
subtract = lambda a, b: a - b
"""
matrix = StimulusResponseMatrix({'s': implementation_code1, 'm1': implementation_code2, 'm2': implementation_code3})
matrix.add_test(name="t1", stimulus_sheet=stimulus_sheet1)
matrix.add_test(name="t2", stimulus_sheet=stimulus_sheet2)
matrix.add_test(name="t3", stimulus_sheet=stimulus_sheet2)
matrix.visualize_stimulus_matrix()
matrix.run_tests()
matrix.visualize_results()