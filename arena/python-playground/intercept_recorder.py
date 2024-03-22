import functools
import json


class Interceptor:
    """
    Wraps functions/methods and records inputs and output
    """

    @staticmethod
    def intercept_args_and_return_values(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # FIXME use JSONL recorder to store SRM?

            # Intercept input values (args and kwargs)
            print("Input arguments:", args, kwargs)
            print("JSON Inputs")
            print(json.dumps(args))

            # Call the original function
            result = func(*args, **kwargs)

            # Intercept return value
            print("Return value:", result)

            print("JSON Outputs")
            print(json.dumps(result))

            # Return the result
            return result

        return wrapper

    @staticmethod
    def apply_decorator_dynamically(func, decorator):
        """
        Apply the given decorator to the function dynamically at runtime.
        """
        # if not isinstance(decorator, type) or not issubclass(decorator, (type,)):
        #     raise ValueError("The decorator must be a class.")

        if not hasattr(func, "__wrapped__"):
            # The function has not been decorated yet, so apply the decorator
            func = decorator(func)

        return func


## demonstration
if __name__ == '__main__':
    interceptor = Interceptor()
    exec_globals = {}
    exec_locals = {}

    # FIXME also look into competitive impls (HumanEval, EvalPlus etc.) .. so replicate their behavior
    # FIXME read in from benchmarks (MultiPL-E, HumanEvalPack etc.)
    # exec dynamically creates program and runs it
    exec('''def sum(a, b):
         a += 1
         b -= 2
         return a + b''', exec_globals, exec_locals)

    # only one function in local scope (lookup dict)
    for k, v in exec_locals.items():
        print(f"found function '{k}'")

        print("wrapping function")
        dec_func = interceptor.apply_decorator_dynamically(v, interceptor.intercept_args_and_return_values)

        # test
        # FIXME replace with values passed by existing tests (see benchmarks)
        dec_func(2, 3)

    # do recorder stuff (write out, e.g. JSONL or something, or directly into LASSO Ignite)