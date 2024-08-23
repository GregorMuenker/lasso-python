class Calculator:
    def __init__(self):
        pass

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
    def __init__(self, a: float):
        self.a = a

    def cubed(self, a: int):
        return a * a * a

    def add(self, a: int, b: str):
        return f"{a}<>{b}"

    def minus(self, a: float, b: float) -> float:
        return a - b