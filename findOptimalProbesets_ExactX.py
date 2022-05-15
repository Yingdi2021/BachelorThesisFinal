import numpy as np

from helperMethods import *
import logging

logging.basicConfig(level=LOGGING_LEVEL)
from optimum import Optimum


def utilityOfProbeset_ExactX(inputData, m, probeset):
    """ calculates the utility (probability of making the right decision) given input data, m and a specific
    probe-set), for the ExactX scenario, ie. acceptance criteria is: number of 1s == m. """

    k = len(probeset)
    n = len(inputData)
    grundset = set(range(n))
    restset = grundset - probeset

    utility = 0

    # if there are no more than m 1s in the probe-set:
    for d in range(m + 1):
        logging.debug("*********************\nCalculating probability of having excatly %s Eins in the probe-set", d)
        subsets_for_this_d = findAllSubsets(probeset, d)
        logging.debug("there are in total %s subsets: %s for d=%s", len(subsets_for_this_d), subsets_for_this_d, d)
        ps = 0
        for subset in subsets_for_this_d:
            remaining_nulls = probeset - set(subset)
            p_subset = multiplyPand1MinusP(inputData, set(subset), remaining_nulls)
            logging.debug("subset:%s, R=%s, p=%s ", set(subset), remaining_nulls, p_subset)
            ps += p_subset
        logging.debug("probability, that there are exactly %s Eins in probe-set is:%s", d, ps)

        r = m - d
        logging.debug("---------------\nCalculating C (Prob that there are excatly %s 1s in R) for d=%s ", r, d)

        c = 0
        if r <= n - k:
            subsets_for_this_m = findAllSubsets(restset, r)
            for subset in subsets_for_this_m:
                remaining_nulls = restset - set(subset)
                p_subset = multiplyPand1MinusP(inputData, set(subset), remaining_nulls)
                c += p_subset
        logging.debug("probability, that exactly %s Eins in Rest-Set is: %s", r, c)
        logging.debug("choose the more likely! \nWhen there are %s Eins in probe-set: ", d)
        if c >= 0.5:
            logging.debug("it's more likely (p=%s) that this is a good candidate", c)
            logging.debug("--> probability, that d=%s AND we make the right decision is %s", d, ps * c)
            utility += ps * c
        else:
            logging.debug("it's more likely (p=%s) that this is a bad candidate", (1 - c))
            logging.debug("--> probability, that d=%s AND we make the right decision is %s", d, ps * (1 - c))
            utility += ps * (1 - c)

    # if there are more than m 1s in probe-set, we always make the right decision: reject
    if k > m:
        for d in range(m + 1, k + 1):
            logging.debug("*********************\nif there are %s Eins (>m) in probeset, we always make the right "
                          "decision: reject", d)
            subsets_for_this_d = findAllSubsets(probeset, d)
            logging.debug("there are in total %s subsets: %s for d=%s", len(subsets_for_this_d), subsets_for_this_d, d)
            ps = 0
            for subset in subsets_for_this_d:
                remaining_nulls = probeset - set(subset)
                p_subset = multiplyPand1MinusP(inputData, set(subset), remaining_nulls)
                logging.debug("subset: %s, R=%s, p=%s ", set(subset), remaining_nulls, p_subset)
                ps += p_subset
            logging.debug(
                "probability, that there are exactly %s Eins in probe-set AND we make the right decision is:%s", d, ps)
            utility += ps

    logging.debug("-------------\nResult:")
    logging.debug("-------------utiliiy=%s when we select the probe-set: %s -----------", utility, probeset)
    return round(utility, ROUNDING_DIGIT_RESULT)


def findOptimalProbesets_ExactX(inputData, m, k):
    """ given inputData, m, k (size of probeset), returns the optimal probe-set(s) yielding maximum
    utility and the corresponding maximum utility score for the ExactX scenario."""

    n = len(inputData)
    maxU = 0
    secondBestU = 0
    maxSets = set()
    counter = 0
    secondBestUpdated = False
    for probe_set in findAllSubsets(set(range(n)), k):
        logging.debug("*****************************************************************")
        logging.debug("possible probeset %s: S=%s", counter, probe_set)
        counter += 1
        u = utilityOfProbeset_ExactX(inputData, m, set(probe_set))
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


inputData = np.array([0.444, 0.685, 0.709, 0.975])
m = 0
k = 2
findOptimalProbesets_ExactX(inputData, m, k)