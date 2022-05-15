import logging
import numpy as np
from findOptimalProbesets_XOR import findOptimalSubsets_XOR
from properties import *


def findProbesetByGreedy(inputData, k):
    """ Implementation of the greedy algorithm. given a vector of probabilities (inputdata) and the size of the
    probeset (k) returns the optimal subset according to the greedy algorithm along with the abs(2pi-1) scores ->
    needed for a meaningful comparison between the results from greedy and exhaustion. """

    scores = np.absolute(np.subtract(inputData * 2, 1))  # abs(2pi-1)
    scores = np.round(scores, 3)
    a = 0  # the left edge
    b = len(inputData) - 1  # the right edge
    while b - a >= k:
        if scores[a] > scores[b]:
            a += 1
        else:  # scores[a] < scores[b]:
            b -= 1
    return np.arange(a, b + 1, 1), scores


def batchTestXorGreedy():
    # for any instance (a specific input-data, n, k) we can check if the result of greedy algorithm is correct.
    for n in range(SIMULATION_N_START, SIMULATION_N_END):
        for k in range(2, n):
            violation = False
            for i in range(NUM_SIMULATIONS_PER_PARAMETER_COMBINATION):
                inputData = sorted(np.random.rand(n))
                inputData = np.round(inputData, ROUNDING_DIGIT_INPUT)
                # find the optimal probe-set(s) for this random input through brutal force
                maxSets, maxU, optimumType = findOptimalSubsets_XOR(inputData, k)
                # find the probe-set returned by the greedy algorithm
                greedyResult, scores = findProbesetByGreedy(inputData, k)

                violation_for_this_instance = True
                for maxSet in maxSets:
                    if (greedyResult == maxSet).all():
                        violation_for_this_instance = False
                        break

                if violation_for_this_instance:
                    logging.critical("inputData=%s, scores=%s, n=%s, k=%s, maxSets: ", inputData, scores, n, k)
                    for maxSet in maxSets:
                        logging.critical(np.asarray(maxSet))
                    logging.critical("Violation! maxSet returned by greedy is: %s", greedyResult)
                    violation = True
            logging.critical("n=%s, k=%s, any violation?: %s" % (n, k, violation))


batchTestXorGreedy()