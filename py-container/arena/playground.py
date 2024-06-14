import copy
import inspect
import importlib

np = importlib.__import__('numpy')

def is_class_method(qualname):
    class_method = '.' in qualname
    if class_method:
        print(f"The function {qualname} is defined as a method of the class '{qualname.split('.')[0]}'")
    else:
        print(f"The function {qualname} is not defined as a method of a class")
    return class_method

original_mean = getattr(np, 'mean')
is_class_method(original_mean.__qualname__)

original_median = getattr(np, 'median')
is_class_method(original_median.__qualname__)

ndarray_sum = getattr(np.ndarray, 'sum')
is_class_method(ndarray_sum.__qualname__)

def change_return_type(new_type):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return new_type(result)
        return wrapper
    return decorator

data = [1, 2, 3, 4, 5]

copied_mean = copy.deepcopy(original_mean)
copied_median = copy.deepcopy(original_median)

function_dict = {
    'mean': change_return_type(int)(copied_mean),
    'median': copied_median
}

print(function_dict['mean'](data))
print(function_dict['median'](data))

#########################
#########################
#########################

ndarray_class = getattr(np, 'ndarray')
init_signature = inspect.signature(ndarray_class.__init__)

print(f"__init__ parameters: {init_signature}")
parameters = init_signature.parameters

print(parameters)

buffer = np.array([1, 2, 3, 4], dtype=np.int32)

# Initialize the ndarray using the inspected parameters
# In practice, you would dynamically determine and provide appropriate arguments
ndarray_instance = ndarray_class((2, 2), buffer=buffer, dtype=np.int32)

# Print the initialized ndarray instance
print(ndarray_instance)
