from helperMethods import *
from optimum import Optimum
import logging

logging.basicConfig(level=LOGGING_LEVEL)


def utilityOfProbeset_XOR(inputData, subset):
    """ calculates the utility (probability of making the right decision) given input data and a specific Subset (the
    probe-set) for the XOR scenario, ie. acceptance criteria is: number of 1s is even.

    1. in case there are even number of 1s in the probeset
    utility += p_probe_even * max(p_rest_even, 1-p_rest_even)
    2. in case there are odd number of 1s in probeset:
    utility += p_probe_odd * max(p_rest_odd, 1-p_rest_odd)

    Note that p_rest_odd = 1-p_rest_even; 1-p_rest_odd = p_rest_even

    Altogether:
    utility = (p_rest_even + p_probe_odd) * max(p_rest_even, 1-p_rest_even)
            = 1 * max(p_rest_even, 1-p_rest_even)
    """

    n = len(inputData)
    grundset = set(range(n))
    restset = grundset - subset
    restData = inputData[list(restset)]

    p_rest_even = probabilityEvenNumberOfEventsHappen(restData)
    utility = max(p_rest_even, 1 - p_rest_even)
    logging.debug("p_rest_even=%s, p_restOdd=%s", round(p_rest_even, 3), round((1 - p_rest_even), 3))
    return utility


def findOptimalSubsets_XOR(inputData, k):
    """ given inputData, k (size of probeset), returns the optimal probe-set yielding maximum utility and the
    corresponding utility score for the XOR scenario. """

    n = len(inputData)
    maxU = 0
    secondBestU = 0
    maxSets = set()
    counter = 0
    secondBestUpdated = False
    for probe_set in findAllSubsets(set(range(n)), k):
        counter += 1
        logging.debug("*****************************************************************")
        logging.debug("possible probeset %s: S=%s", counter, probe_set)
        u = utilityOfProbeset_XOR(inputData, set(probe_set))
        if counter == 1:
            secondBestU = u
            maxU = u
            maxSets = set()
            maxSets.add(probe_set)
        else:
            if u - maxU >= SIGNIFICANCE_LEVEL:  # if the new utility is significantly greater than the maxU so far
                secondBestU = maxU  # then the old maxU becomes the secondBest
                secondBestUpdated = True
                maxU = u  # update the maxU
                maxSets = set()
                maxSets.add(probe_set)
            elif abs(u - maxU) < SIGNIFICANCE_LEVEL:  # if the new utility is almost identical to the maxU so far
                maxSets.add(probe_set)
        logging.info("when probe-set=%s ,u=%s", set(probe_set), u)

    logging.info("*****************************************************************")
    logging.info("Utility is maximum (%s) when probeset is (one of) the following: ", maxU)
    for bestSet in maxSets:
        logging.info("%s corresponding prob: %s", bestSet, inputData[list(bestSet)])

    # determines optimum Type
    if len(maxSets) == len(findAllSubsets(set(range(n)), k)):
        optimumType = Optimum.ANY
    elif not secondBestUpdated:  # if secondBest is never updated, it means the first set is the best or one of the best
        optimumType = Optimum.TRUE
    else:
        abstand = maxU - secondBestU
        if abstand > SIGNIFICANCE_LEVEL:
            optimumType = Optimum.TRUE
        else:
            optimumType = Optimum.PSEUDO
    logging.info("optimumType = %s", optimumType)

    return maxSets, maxU, optimumType


# Run a example test
inputData = np.array([0.065, 0.191, 0.263, 0.263, 0.39, 0.456, 0.737, 0.888])
k = 4
maxSets, maxU, optimumType = findOptimalSubsets_XOR(inputData, k)
