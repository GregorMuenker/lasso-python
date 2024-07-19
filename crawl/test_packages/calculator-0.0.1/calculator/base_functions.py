def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b) -> int:
    product = 0
    for _ in range(b):
        product = add(product, a)
    return product