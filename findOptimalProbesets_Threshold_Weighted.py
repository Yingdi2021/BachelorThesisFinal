from helperMethods import *
import logging

logging.basicConfig(level=LOGGING_LEVEL)
from optimum import Optimum


def calculProbOverWeightedThreshold(probs, weights, l):
    """ given a unprobed rest_set (a vector of probs and weights) and a threshold value l, calculate the probability
    that this rest_set has a weighted number of Eins > l"""
    p_ok = 0
    n = len(probs)
    for possibility in list(itertools.product({0,1}, repeat=n)):
        if np.dot(weights, possibility) >= l: # if this happens, is good,but what is the possibility that this happens?
            p = 1
            for i in range(n):
                p *= (((possibility[i] == 1)*probs[i])+(possibility[i]==0)*(1-probs[i]))
            p_ok += p
    return p_ok

def utilityOfProbeset_Threshold_Weighted(inputData, weights, l, S):
    """ calculates the utility (probability of making the right decision) given input data, weights, l (threshold) and a
    specific probe-set, for the WEIGHTED Threshold scenario, ie. acceptance criteria is: WEIGHTED number of 1s >= l. """

    n = len(inputData)
    k = len(S)
    N = set(range(n))
    R = N - S
    probe_set_probs = inputData[list(S)]
    rest_set_probs = inputData[list(R)]
    probe_set_weights = weights[list(S)]
    rest_set_weights = weights[list(R)]

    utility = 0

    # loop through all possibilities in the probeset and calculate for each possiblity the weighted number of Eins.
    for combination_in_probe in list(itertools.product({0,1}, repeat=k)): # if k=2, then 4 combinations: 00, 01, 10, 11
        p_this_combination = 1
        for i in range(k):
            p_this_combination *= (((combination_in_probe[i] == 1)*probe_set_probs[i])+(combination_in_probe[i]==0)*(1-probe_set_probs[i]))
        # now we know how likely it is that exactly this combination is the case.
        weighted_sum_in_probeset = np.dot(probe_set_weights, combination_in_probe)
        logging.debug("if it is %s (prob=%s) in the probe-set, then weighted_sum_in_probeset = %s, we need %s in rest_set ",
                      combination_in_probe, p_this_combination, weighted_sum_in_probeset, l-weighted_sum_in_probeset)
        if l-weighted_sum_in_probeset > 0:
            p_rest_enough = calculProbOverWeightedThreshold(rest_set_probs, rest_set_weights, l-weighted_sum_in_probeset)
        else:
            p_rest_enough = 1

        if p_rest_enough >= 0.5:
            u = p_this_combination * p_rest_enough
            logging.debug("prob that rest_set has enough Eins is %s, good candidate, accept. u=%s", p_rest_enough, u)
        else:
            u = p_this_combination * (1-p_rest_enough)
            logging.debug("prob that rest_set has enough Eins is %s, bad candidate, reject. u=%s", p_rest_enough, u)
        utility += u

    logging.debug("-------------\nResult:")
    logging.debug("utiliiy=%s when we select the probe-set: %s", utility, S)
    return round(utility, ROUNDING_DIGIT_RESULT)

def findOptimalProbesets_Threshold_Weighted(inputData, weights, l, k):
    """ given inputData, weights, l (threshold), k (size of probeset), returns the optimal probe-set(s) yielding
    maximum utility and the corresponding maximum utility score for the WEIGHTED Threshold scenario."""

    n = len(inputData)
    maxU = 0
    secondBestU = 0
    maxSets = set()
    counter = 0
    secondBestUpdated = False
    for probe_set in findAllSubsets(set(range(n)), k):
        logging.debug("*****************************************************************")
        logging.debug("S=%s", probe_set)
        counter += 1
        u = utilityOfProbeset_Threshold_Weighted(inputData, weights, l, set(probe_set))
        if counter == 1:
            secondBestU = u
            maxU = u
            maxSets = set()
            maxSets.add(probe_set)
        else:
            if u - maxU >= SIGNIFICANCE_LEVEL: # if the new utility is significantly greater than the maxU so far
                secondBestU = maxU # then the old maxU becomes the secondBest
                secondBestUpdated = True
                maxU = u # update the maxU
                maxSets = set()
                maxSets.add(probe_set)
            elif abs(u-maxU) < SIGNIFICANCE_LEVEL: # if the new utility is almost identical to the maxU so far
                maxSets.add(probe_set)
        logging.info("when probe-set=%s ,u=%s", set(probe_set), u)

    logging.info("*****************************************************************")
    logging.info("Utility is maximum (%s) when probeset is (one of) the following:", maxU)
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