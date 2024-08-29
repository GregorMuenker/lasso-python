class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a: int, b: float):
        return a - b


def multiply(a, b, c):
    return a * b * c


def divide(a, b):
    return a / b


def square(a: int) -> int:
    return a * a


class Test:
    def __init__(self):
        pass

    def cubed(self, a: list):
        return a

    def add(self, a: int, b: str):
        return f"{a}<>{b}"

    def minus(self, a: float, b: float) -> float:
        return a - b