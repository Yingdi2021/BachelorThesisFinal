from findOptimalProbesets_Threshold import findOptimalProbesets_Threshold
from properties import *
import numpy as np
from optimum import Optimum


def testRandomInstanceAll1sIsLowestBitsOptimal(n, k):
    inputData = sorted(np.random.rand(n))
    inputData = np.round(inputData, ROUNDING_DIGIT_INPUT)
    maxSets, maxU, optimumType = findOptimalProbesets_Threshold(inputData, n, k)
    if optimumType != Optimum.TRUE:
        return True
    else:
        for maxSet in maxSets:
            if maxSet[0] == 0:
                return True  # the lowest k bits is (at least one of) the optimal probeset
        # if after looping through all optimal probesets, we still haven't found the one expected (lowest bits) then:
        logging.critical("Exception found! inputData=%s, n=%s, l=1, k=%s. None of the optimal Probesets is the "
                         "lowest %s bits", inputData, n, k, k)
        return False


def batchTestAll1sLowestBits():
    violation = False
    for n in range(SIMULATION_N_START, SIMULATION_N_END):
        for k in range(2, n):
            for i in range(NUM_SIMULATIONS_PER_PARAMETER_COMBINATION):
                if not testRandomInstanceAll1sIsLowestBitsOptimal(n, k):
                    violation = True
                    break
    if not violation:
        logging.critical("All1s: always lowest bits? %s instances tested, no exception found. ",
                         NUM_SIMULATIONS_PER_PARAMETER_COMBINATION, )


batchTestAll1sLowestBits()
