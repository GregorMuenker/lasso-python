from collections import deque

class Stack(deque):
    def append(self, item) -> None:
        super().append(item)

    def appendleft(self, x) -> None:
        super().appendleft(x)

    def clear(self) -> None:
        super().clear()

    def copy(self) -> deque:
        return super().copy()

    def count(self, x) -> int:
        return super().count(x)

    def extend(self, iterable) -> None:
        super().extend(iterable)

    def extendleft(self, iterable) -> None:
        super().extendleft(iterable)

    def index(self, x, start=0, stop=None) -> int:
        return super().index(x, start, stop)

    def insert(self, i, x) -> None:
        super().insert(i, x)

    def pop(self):
        return super().pop()

    def popleft(self):
        return super().popleft()

    def remove(self, value) -> None:
        super().remove(value)

    def reverse(self) -> None:
        super().reverse()

    def rotate(self, n=1) -> None:
        super().rotate(n)
    
    @property
    def maxlen(self):
        return super().maxlen