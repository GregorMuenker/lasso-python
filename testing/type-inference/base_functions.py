def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    product = 0
    for _ in range(b):
        product = add(product, a)
    return product