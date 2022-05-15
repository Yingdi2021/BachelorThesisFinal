from helperMethods import *
import logging

logging.basicConfig(level=LOGGING_LEVEL)
from optimum import Optimum


def utilityOfProbeset_Threshold(inputData, l, probeset):
    """ calculates the utility (probability of making the right decision) given input data, l (threshold) and a
    specific probe-set, for the Threshold scenario, ie. acceptance criteria is: number of 1s >= l. """

    k = len(probeset)
    n = len(inputData)
    grundset = set(range(n))
    restset = grundset - probeset

    utility = 0
    for d in range(k + 1):
        logging.debug("Calculating probability of having excatly %s Eins in the probe-set", d)
        subsets_for_this_d = findAllSubsets(probeset, d)
        logging.debug("there are in total %s subsets: %s for d=%s", len(subsets_for_this_d), subsets_for_this_d, d)
        ps = 0
        for subset in subsets_for_this_d:
            remaining_nulls = probeset - set(subset)
            p_subset = multiplyPand1MinusP(inputData, set(subset), remaining_nulls)
            logging.debug("subset: %s, R=%s, p=%s", set(subset), remaining_nulls, p_subset)
            ps += p_subset
        logging.debug("probability, that there are exactly %s Eins in probe-set is: %s", d, ps)

        logging.debug("---------------\nCalculating C (P that there are enough Eins in R) for d= %s", d)
        if d >= l:
            logging.debug("there are already enough Eins in probe-set. Therefore C=1.")
            utility += ps
        else:
            c = 0
            for m in range(l - d, n - k + 1):
                subsets_for_this_m = findAllSubsets(restset, m)
                logging.debug("there are %s subsets for m=%s", len(subsets_for_this_m), m)
                for subset in subsets_for_this_m:
                    remaining_nulls = restset - set(subset)
                    p_subset = multiplyPand1MinusP(inputData, set(subset), remaining_nulls)
                    c += p_subset
            logging.debug("probability, that at least %s Eins in Rest-Set is:%s", l - d, c)
            logging.debug("choose the more likely! \nWhen there are %s Eins in probe-set: ", d)
            if c >= 0.5:
                logging.debug("it's more likely (p=%s) that this is a good candidate", c)
                logging.debug("--> probability, that d=%s AND we make the right decision is %s", d, ps * c)
                utility += ps * c
            else:
                logging.debug("it's more likely (p=%s ) that this is a bad candidate ", (1 - c))
                logging.debug("--> probability, that d=%s AND we make the right decision is %s", d, ps * (1 - c))
                utility += ps * (1 - c)

    logging.debug("-------------\nResult:")
    logging.debug("utiliiy=%s when we select the probe-set: %s", utility, probeset)
    return round(utility, ROUNDING_DIGIT_RESULT)


def findOptimalProbesets_Threshold(inputData, l, k):
    """ given inputData, l (threshold), k (size of probeset), returns the optimal probe-set(s) yielding maximum
    utility and the corresponding maximum utility score for the Threshold scenario."""

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
        u = utilityOfProbeset_Threshold(inputData, l, set(probe_set))
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


inputData = np.array([0.5, 0.749, 0.81, 0.976])
l = 2
k = 2
maxSets, maxU, optimumType = findOptimalProbesets_Threshold(inputData, l, k)




