from enum import Enum

class Optimum(Enum):
    ANY = 1 # all possible subsets (of the given size) yield the same utility
    PSEUDO = 2 # there is a max-set with maximum utility but the difference is too small to be considered significant
    TRUE = 3 # there is indeed a optimal subset.