class Calculator:
    def __init__(self, a):
        pass

    def add(self, a, b):
        return a + b

    def subtract(self, a: int, b: float):
        return a - b


def multiply(a, b, c):
    return a * b * c


def divide(a, b):
    return a / b


def square(a):
    return a * a


class Test:
    def __init__(self, a: float):
        self.a = a

    def square(self, a: int):
        return a * a

    def add(self, a: int, b: str):
        return a + b

    def subtract(self, a: float, b: float):
        return a - b
