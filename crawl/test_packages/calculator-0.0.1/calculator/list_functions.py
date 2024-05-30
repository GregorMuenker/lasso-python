import base_functions
import numpy.core.fromnumeric

class CalcList:
    def __init__(self, list=None):
        if list == None:
            self.list = []
        else:
            self.list = list

    def append(self, element):
        self.list.append(element)

    def sum(self):
        sum = 0
        for element in self.list:
            sum = base_functions.add(sum, element)
        return sum

    def avg(self):
        return numpy.core.fromnumeric.mean(self.list)