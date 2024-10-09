from collections import deque

class Stack(deque):
    def append(self, item)->None:
        super().append(item)
    
    def appendleft(self, x)->None:
        super().appendleft(x)

    def clear(self) -> None:
        return super().clear()

    def copy(self) -> 'Stack':
        return super().copy()
    
    def count(self, x) -> int:
        return super().count(x)
    
    def extend(self, iterable):
        super().extend(iterable)

    def pop(self):
        return super().pop()
    
    def popleft(self):
        return super().popleft()

