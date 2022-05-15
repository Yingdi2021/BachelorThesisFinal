from optimum import Optimum
from helperMethods import *

from findOptimalProbesets_Threshold_Weighted import findOptimalProbesets_Threshold_Weighted


# Part 1/2
# Hypothesis:
# It should be the case that in some instances some entries might be actually irrelevant since they have very small
# weights. Maybe you can state an algorithm that sorts them out beforehand and, hence, makes the computation of the
# optimum faster and more elegant than just brute-forcing all possible combinations.

# Is it true? Let's find out:
def isSmallWeightAlsoRelevant():
    exceptionFound = False
    for n in range(SIMULATION_N_START, SIMULATION_N_END):
        for l in range(3, 4):
            for k in range(2, 3):
                while not exceptionFound:
                    pools = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
                    inputData = sorted(np.random.choice(pools, n))
                    inputData = np.round(inputData, 1)
                    # generate a random weight array of size n, of which all elements sum up to n.
                    weights = np.random.dirichlet(np.ones(n)) * n
                    weights = np.round(weights, 1)
                    # manipulate the weights, so that the last item is very small (=0.001) but the sum is still = n
                    weights_copy = weights[:]
                    extra = weights[n - 1] - 0.001
                    weights_copy[n - 1] = 0.001
                    weights_copy[0] += extra
                    # find optimal probe-set(s) for this random input.
                    maxSets1, maxU1, secondBestU1, significant1 = findOptimalProbesets_Threshold_Weighted(
                        inputData, weights_copy, l, k)
                    # ignore the first item and then find optimal probe-set(s)
                    maxSets2, maxU2, secondBestU2, significant2 = findOptimalProbesets_Threshold_Weighted(
                        inputData[0:n - 1], weights_copy[0:n - 1], l, k)

                    if (len(maxSets1) == len(maxSets2) == 1):
                        for maxSet1 in maxSets1:
                            for maxSet2 in maxSets2:
                                if maxSet1 != maxSet2 and len(maxSet1) == len(maxSet2) == 2:
                                    exceptionFound = True
                                    logging.critical(
                                        "Excpetion found! data=%s, weights_original=%s, l=%s, k=%s, original optimalSet=%s, if we ignore.. optimalSet=%s.",
                                        inputData, weights, l, k, maxSet1, maxSet2)


isSmallWeightAlsoRelevant()

# You see? The answer is no, even bits with very small weights can not be safely ignored! An example:
threshold = 3
k = 2
inputData = np.array([0.1, 0.1, 0.4, 0.5])
weights = np.array([2.999, 0.4, 0.6, 0.001])
findOptimalProbesets_Threshold_Weighted(inputData, weights, threshold, k)  # (0, 2) is the only optimal probeset.
inputData = inputData[0:3]
weights = weights[0:3]
findOptimalProbesets_Threshold_Weighted(inputData, weights, threshold, k)  # (0, 3) would be the only optimal probeset.


# Part 2/2
# ok all bits have to be taken into account. Now, the question is: does the consecutive conjecture still hold?
# Run simulations to find out empirically. try to find an instance where the consecutive conjecture is broken:
# when we sort the vector according to the inputData (probabilities) as well as
# when we sort the vector according to the weighted sum.

def testRandomInstanceConsecutive_Threshold_Weighted(n, l, k):
    """generate a random inputData vector based on the given parameters, find optimal probeset, return true if all
    the optimal probesets violate the consecutive conjecture no matter how we sort the vector: weighted or unweighted"""

    violation = False

    pools = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    inputData = sorted(np.random.choice(pools, n))
    inputData = np.round(inputData, 1)  # the goal is not to round (unnecessary) but convert the type to ndarray.
    weights = np.random.dirichlet(np.ones(n)) * n
    weights = np.round(weights, ROUNDING_DIGIT_WEIGHTS)

    maxSets, maxU, optimumType = findOptimalProbesets_Threshold_Weighted(inputData, weights, l, k)

    weighted_inputdata = weights * inputData
    sorted_index_weighted_inputdata = np.argsort(weighted_inputdata)  # sorted index of the weighted inputdata
    if optimumType == Optimum.TRUE:
        violationCount = 0  # keep track of (if there are multiple optimal probesets) how many of them violate.
        for maxSet in maxSets:
            if not isConsecutive_WithRespectToWeightedOrder(maxSet, sorted_index_weighted_inputdata) and not \
                    isConsecutive_WithRespectToUnweightedProbs_RepeatingValueSafe(maxSet, inputData):
                violationCount += 1
        if violationCount == len(maxSets):  # if all optimal probesets violate, then a good counterexample.
            violation = True
            logging.critical("Perfect counterexample found! inputData=%s, weights=%s, l=%s, k=%s", inputData,
                             weights, l, k)
    return violation


def batchTestConsecutiveThresholdWeighted():
    violation = False
    for n in range(SIMULATION_N_START, SIMULATION_N_END):
        for l in range(SIMULATION_N_START, n + 1):
            for k in range(2, n):
                for i in range(NUM_SIMULATIONS_PER_PARAMETER_COMBINATION):
                    print(i)
                    if testRandomInstanceConsecutive_Threshold_Weighted(n, l, k):
                        violation = True
                        break
    if not violation:
        logging.critical("Simulations finished, no violation instance found.")


batchTestConsecutiveThresholdWeighted()  # --------batch test--------

# There seems to be exceptions.
# check the counter-example found. Is it really a counter-example?
inputData = np.array([0.3, 0.5, 0.7, 0.8])
weights = np.array([1.2, 1.3, 0.1, 1.4])
weighted_input = weights * inputData
l = 4
k = 2
maxSets, maxU, optimumType = findOptimalProbesets_Threshold_Weighted(inputData, weights, l, k)
print(weighted_input)
# ok indeed, no matter how you sort the vector, the optimal probeset is not consecutive.
