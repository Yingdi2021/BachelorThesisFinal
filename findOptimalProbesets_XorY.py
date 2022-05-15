from findOptimalProbesets_ExactX import utilityOfProbeset_ExactX
from helperMethods import *
from optimum import Optimum
import logging
logging.basicConfig(level=LOGGING_LEVEL)


def utilityOfProbeset_XorY(inputData, x, y, probeset):
    """ calculates the utility (probability of making the right decision) given input data, x, y and a specific
    probe-set), for the XorY scenario, ie. acceptance criteria is: number of 1s == x || y. """

    k = len(probeset)
    if x == y:
        return utilityOfProbeset_ExactX(inputData, x, probeset)

    # make sure that x, y are in ascending order. If not, switch.
    if x > y:
        x,y = y,x

    n = len(inputData)
    grundset = set(range(n))
    restset = grundset - probeset

    utility = 0
    for d in range(k + 1):
        logging.debug("*********************\nCalculating probability of having excatly %s Eins in the probe-set", d)
        subsets_for_this_d = findAllSubsets(probeset, d)
        ps = 0
        for subset in subsets_for_this_d:
            remaining_nulls = probeset - set(subset)
            p_subset = multiplyPand1MinusP(inputData, set(subset), remaining_nulls)
            logging.debug("subset: %s, R=%s, p=%s", set(subset), remaining_nulls, p_subset)
            ps += p_subset
        logging.debug("probability, that there are exactly %s Eins in probe-set is: %s",  d, ps)

        r1 = x - d
        r2 = y - d
        logging.debug("---------------\nCalculating C (Prob that there are excatly %s or %s 1s in R) for d=%s", r1, r2, d)

        c = 0
        if r1 <= n - k and r1 >= 0:
            subsets_for_this_r = findAllSubsets(restset, r1)
            for subset in subsets_for_this_r:
                remaining_nulls = restset - set(subset)
                p_subset = multiplyPand1MinusP(inputData, set(subset),remaining_nulls)
                c += p_subset
        if r2 <= n - k and r2 >= 0:
            subsets_for_this_r = findAllSubsets(restset, r2)
            for subset in subsets_for_this_r:
                remaining_nulls = restset - set(subset)
                p_subset = multiplyPand1MinusP(inputData, set(subset),remaining_nulls)
                c += p_subset
        logging.debug("probability, that exactly %s or %s Eins in Rest-Set is: %s", r1,  r2, c)
        logging.debug("choose the more likely! \nWhen there are %s Eins in probe-set: ", d)
        if c >= 0.5:
            logging.debug("it's more likely (p= %s) that this is a good candidate", c)
            logging.debug("--> probability, that d= %s AND we make the right decision is %s", d, ps * c)
            utility += ps * c
        else:
            logging.debug("it's more likely (p= %s) that this is a bad candidate", (1 - c))
            logging.debug("--> probability, that d=%s AND we make the right decision is %s", d, ps * (1 - c))
            utility += ps * (1 - c)

    logging.debug("-------------\nResult:")
    logging.debug("utiliiy=%s when we select the probe-set: %s", utility, probeset)

    return round(utility, ROUNDING_DIGIT_RESULT)


def findOptimalProbesets_XorY(inputData, x, y, k):
    """ given inputData, x, y, k (size of probeset), returns the optimal probe-set(s) yielding maximum
    utility and the corresponding maximum utility score for the XorY scenario."""

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
        u = utilityOfProbeset_XorY(inputData, x, y, set(probe_set))
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
    elif not secondBestUpdated: # if secondBest is never updated, it means the first set is the best or one of the best
        optimumType = Optimum.TRUE
    else:
        abstand = maxU - secondBestU
        if abstand > SIGNIFICANCE_LEVEL:
            optimumType = Optimum.TRUE
        else:
            optimumType = Optimum.PSEUDO
    logging.info("optimumType = %s", optimumType)

    return maxSets, maxU, optimumType
