from enum import Enum

class Scenario(Enum):
    THRESHOLD = 1
    ATLEASTONE = 2
    ALL1s = 3
    EXACTONE = 4
    NONEORALL = 5
    XOR = 6