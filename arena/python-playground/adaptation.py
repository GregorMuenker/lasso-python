import ast
import textwrap

from pytype import config
# from pytype.tests import test_base
from pytype.tools.annotate_ast import annotate_ast

import inspect


# annotate would actually happen in analyzer?
def annotate(source):
    source = textwrap.dedent(source.lstrip('\n'))
    # pytype_options = config.Options.create(python_version=self.python_version)
    pytype_options = config.Options.create()

    module = annotate_ast.annotate_source(source, ast, pytype_options)
    return module


def get_annotations_dict(module):
    return {_get_node_key(node): node.resolved_annotation
            for node in ast.walk(module)
            if hasattr(node, 'resolved_type')}


def _get_node_key(node):
    base = (node.lineno, node.__class__.__name__)

    if isinstance(node, ast.Name):
        return base + (node.id,)
    elif isinstance(node, ast.Attribute):
        return base + (node.attr,)
    elif isinstance(node, ast.FunctionDef):
        return base + (node.name,)
    else:
        return base


### example function encode_bytes

def calc(input_bytes):
    a = 0
    a += 1
    return input_bytes


def encode(input_str: str) -> str:
    # Get the original function object
    original_func = calc

    # Get the arguments and defaults of the old method
    args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations = inspect.getfullargspec(original_func)

    # get source
    source = inspect.getsource(original_func)
    print(source)

    # infer type information
    module = annotate(source)
    print(get_annotations_dict(module))

    # FIXME do something with it

    # Call the original function with the modified arguments
    input_bytes = input_str.encode()
    output_bytes = original_func(input_bytes)
    output_str = output_bytes.decode()

    # Return the modified output
    return output_str


if __name__ == '__main__':
    print(encode("hello world"))

