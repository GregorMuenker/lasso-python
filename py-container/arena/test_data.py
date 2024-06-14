CALCULATOR_CLASS = """
class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b
    
    def multiply(self, a, b, c):
        return a * b * c

    def divide(self, a, b):
        x = self.add(1, 2)
        return a / b
    
    def test(self, a, b):
        return a + b
"""
CALCULATOR_FUNCTIONS = """
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
"""
CALCULATOR_LAMBDAS = """
add = lambda a, b: a + b
subtract = lambda a, b: a - b
"""

CALCULATOR_MODULE = """
class Calculator:
    def __init__(self):
        pass
    
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b
    
def multiply(a, b, c):
    return a * b * c

def divide( a, b):
    return a / b
"""