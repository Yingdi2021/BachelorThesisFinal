from properties import *
import numpy as np
import itertools
import logging

logging.basicConfig(level=LOGGING_LEVEL)


def findAllSubsets(set, subset_size):
    """ For a given Set, return all possible subsets of a given size, as a list. """
    return list(itertools.combinations(set, subset_size))


def probabilityCertainNumberOfEventsHappen(ps, m):
    """ given a n-vector of probabilities p1, p2,...pn corresponding the prob that event 1, event 2, ... event n
    happens and a constant m (m <= n) return the prob that in total m events happen."""
    n = len(ps)
    assert m <= n
    pss = np.subtract(1, ps)
    result = 0
    for setThatHappens in findAllSubsets(set(range(n)), m):
        setThatDoesNotHappen = set(range(n)) - set(setThatHappens)
        temp = 1
        for i in setThatHappens:
            temp *= ps[i]
        for j in setThatDoesNotHappen:
            temp *= pss[j]
        result += temp
    return round(result, ROUNDING_DIGIT_RESULT)


def probabilityEvenNumberOfEventsHappen(ps):
    """ given a n-vector of probabilities p1, p2,...pn corresponding to the probability that event 1, event 2,
    .. event n happens, return the probability that in total an even number of events happen. """
    n = len(ps)
    result = 0
    for num in np.arange(0, n + 1, 2):
        result += probabilityCertainNumberOfEventsHappen(ps, num)
        logging.debug("----prob(have %s 1s)=%s", num, probabilityCertainNumberOfEventsHappen(ps, num))
    return result

def probabilityExactOne1(probabilities):
    """given a list of probs, calculate the probability that exactly one bit is 1.
    e.g.: sums up the probs of events 001, 010, 100 happening for an input of length 3."""
    counter_prob = 1 - probabilities
    result = 0
    for i in range(len(probabilities)):
        pp = counter_prob.copy()
        pp[i] = probabilities[i]
        result += np.prod(pp)
    return result


def multiplyPand1MinusP(inputData, setP, set1MinusP):
    """ given inputData (a vector of Probs), a set of indexes indicating items that are 1s and a set of indexes
    indicating items that are 0s, returns the probability that exactly this combination happens. """
    result = 1
    for i in setP:
        result *= inputData[i]
    for j in set1MinusP:
        result *= (1 - inputData[j])
    return result


def isConsecutive_WithRespectToUnweightedProbs_RepeatingValueSafe(theSet, inputData):
    """ checks if a given sub-set is consecutive with respect to the inputData (given probability).
    Inconsecutiveness due to repeating values are tolerated. """
    selectedElements = set(inputData[list(theSet)])
    remainingElements = set(inputData) - selectedElements
    consecutive = True
    for i in remainingElements:
        if (i < max(selectedElements)) and (i > min(selectedElements)):
            return False
    return consecutive


def isConsecutive_WithRespectToWeightedOrder(maxSet, sorted_index):
    selectedElements = set()
    for i in maxSet:
        index = np.where(sorted_index == i)
        selectedElements.add(index[0][0])
    allElements = set(sorted_index)
    remainElements = allElements - selectedElements
    consecutive = True
    for i in remainElements:
        if (i < max(selectedElements)) and (i > min(selectedElements)):
            consecutive = False
    return consecutive
