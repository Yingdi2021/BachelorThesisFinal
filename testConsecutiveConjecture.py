from helperMethods import *
from optimum import Optimum
from definitionslevel import DefinitionLevel

from findOptimalProbesets_Threshold import findOptimalProbesets_Threshold
from findOptimalProbesets_ExactX import findOptimalProbesets_ExactX
from findOptimalProbesets_XorY import findOptimalProbesets_XorY
from findOptimalProbesets_XOR import findOptimalSubsets_XOR


def testRandomInstanceConsecutive_Threshold(n, l, k, standard):
    """ generate a random inputData vector based on the given parameters, find optimal probeset and test if it is
    consecutive, returns boolean. If false, meaning conjecture is violated, an output warning will be showed. """

    violation = False

    inputData = sorted(np.random.rand(n))
    inputData = np.round(inputData, ROUNDING_DIGIT_INPUT)

    maxSets, maxU, optimumType = findOptimalProbesets_Threshold(inputData, l, k)

    if optimumType == Optimum.TRUE:
        if standard == DefinitionLevel.STRICT:
            for maxSet in maxSets:
                if not isConsecutive_WithRespectToUnweightedProbs_RepeatingValueSafe(maxSet, inputData):
                    violation = True
                    logging.critical(
                        "Violation of consecutiveness (Strict) found for scenario Threshold! inputData=%s, "
                        "n=%s, l=%s, k=%s", inputData, n, l, k)
        if standard == DefinitionLevel.LOOSE:
            atLeastOneOptimalSetIsConsecutive = False
            for maxSet in maxSets:
                if isConsecutive_WithRespectToUnweightedProbs_RepeatingValueSafe(maxSet, inputData):
                    atLeastOneOptimalSetIsConsecutive = True
            if not atLeastOneOptimalSetIsConsecutive:
                violation = True
                logging.critical("Violation of consecutiveness (Loose) found for scenario Threshold! inputData=%s, "
                                 "n=%s, l=%s, k=%s", inputData, n, l, k)
    return violation


def testRandomInstanceConsecutive_ExactOne(n, k, standard):
    """ generate a random inputData vector based on the given parameters, find optimal probeset and test if it is
    consecutive, returns boolean. If false, meaning conjecture is violated, an output warning will be showed. """

    violation = False

    inputData = sorted(np.random.rand(n))
    inputData = np.round(inputData, ROUNDING_DIGIT_INPUT)

    maxSets, maxU, optimumType = findOptimalProbesets_ExactX(inputData, 1, k)

    if optimumType == Optimum.TRUE:
        if standard == DefinitionLevel.STRICT:
            for maxSet in maxSets:
                if not isConsecutive_WithRespectToUnweightedProbs_RepeatingValueSafe(maxSet, inputData):
                    violation = True
                    logging.critical(
                        "Violation of consecutiveness (Strict) found for scenario ExactOne! inputData=%s, "
                        "n=%s, k=%s", inputData, n, k)
        if standard == DefinitionLevel.LOOSE:
            atLeastOneOptimalSetIsConsecutive = False
            for maxSet in maxSets:
                if isConsecutive_WithRespectToUnweightedProbs_RepeatingValueSafe(maxSet, inputData):
                    atLeastOneOptimalSetIsConsecutive = True
            if not atLeastOneOptimalSetIsConsecutive:
                violation = True
                logging.critical("Violation of consecutiveness (Loose) found for scenario ExactOne! inputData=%s, "
                                 "n=%s, k=%s", inputData, n, k)
    return violation


def testRandomInstanceConsecutive_XorY(n, x, y, k, standard):
    """ generate a random inputData vector based on the given parameters, find optimal probeset and test if it is
    consecutive, returns boolean. If false, meaning conjecture is violated, an output warning will be showed. """

    violation = False

    inputData = sorted(np.random.rand(n))
    inputData = np.round(inputData, ROUNDING_DIGIT_INPUT)

    maxSets, maxU, optimumType = findOptimalProbesets_XorY(inputData, x, y, k)

    if optimumType == Optimum.TRUE:
        if standard == DefinitionLevel.STRICT:
            for maxSet in maxSets:
                if not isConsecutive_WithRespectToUnweightedProbs_RepeatingValueSafe(maxSet, inputData):
                    violation = True
                    logging.critical("Violation of consecutiveness (Strict) found for scenario NoneOrAll! "
                                     "inputData=%s n=%s, k=%s", inputData, n, k)
        if standard == DefinitionLevel.LOOSE:
            atLeastOneOptimalSetIsConsecutive = False
            for maxSet in maxSets:
                if isConsecutive_WithRespectToUnweightedProbs_RepeatingValueSafe(maxSet, inputData):
                    atLeastOneOptimalSetIsConsecutive = True
            if not atLeastOneOptimalSetIsConsecutive:
                violation = True
                logging.critical("Violation of consecutiveness (Loose) found for scenario NoneOrAll! inputData=%s, "
                                 "n=%s, k=%s", inputData, n, k)
    return violation


def testRandomInstanceConsecutive_XOR(n, k, standard):
    """ generate a random inputData vector based on the given parameters, find optimal probeset and test if it is
    consecutive, returns boolean. If false, meaning conjecture is violated, an output warning will be showed. """

    violation = False

    inputData = sorted(np.random.rand(n))
    inputData = np.round(inputData, ROUNDING_DIGIT_INPUT)

    maxSets, maxU, optimumType = findOptimalSubsets_XOR(inputData, k)

    if optimumType == Optimum.TRUE:
        if standard == DefinitionLevel.STRICT:
            for maxSet in maxSets:
                if not isConsecutive_WithRespectToUnweightedProbs_RepeatingValueSafe(maxSet, inputData):
                    violation = True
                    logging.critical("Violation of consecutiveness (Strict) found for scenario XOR! inputData=%s "
                                     "n=%s, k=%s", inputData, n, k)
        if standard == DefinitionLevel.LOOSE:
            atLeastOneOptimalSetIsConsecutive = False
            for maxSet in maxSets:
                if isConsecutive_WithRespectToUnweightedProbs_RepeatingValueSafe(maxSet, inputData):
                    atLeastOneOptimalSetIsConsecutive = True
            if not atLeastOneOptimalSetIsConsecutive:
                violation = True
                logging.critical("Violation of consecutiveness (Loose) found for scenario XOR! inputData=%s, n=%s, "
                                 "k=%s", inputData, n, k)
    return violation


################# run simulations to batch test the conjecture ############
def batchTestConsecutiveThreshold(standard):
    violation = False
    for n in range(SIMULATION_N_START, SIMULATION_N_END):
        for l in range(2, n):  # we do not consider l=1 (AtLeastOne1) and l=n (All1s)
            for k in range(2, n):
                for i in range(NUM_SIMULATIONS_PER_PARAMETER_COMBINATION):
                    if testRandomInstanceConsecutive_Threshold(n, l, k, standard):
                        violation = True
                        break
    if not violation:
        logging.critical("No violation instance found for scenario=Threshold (1<l<n), standard=%s", standard)


def batchTestConsecutiveAtLeastOne1(standard):
    violation = False
    for n in range(SIMULATION_N_START, SIMULATION_N_END):
        for k in range(2, n):
            for i in range(NUM_SIMULATIONS_PER_PARAMETER_COMBINATION):
                if testRandomInstanceConsecutive_Threshold(n, 1, k, standard):
                    violation = True
                    break
    if not violation:
        logging.critical("No violation instance found for scenario=AtLeastOne1, standard=%s", standard)


def batchTestConsecutiveAll1s(standard):
    violation = False
    for n in range(SIMULATION_N_START, SIMULATION_N_END):
        for k in range(2, n):
            for i in range(NUM_SIMULATIONS_PER_PARAMETER_COMBINATION):
                if testRandomInstanceConsecutive_Threshold(n, n, k, standard):
                    violation = True
                    break
    if not violation:
        logging.critical("No violation instance found for scenario=All1s, standard=%s", standard)


def batchTestConsecutiveExactOne(standard):
    violation = False
    for n in range(SIMULATION_N_START, SIMULATION_N_END):
        for k in range(2, n):
            for i in range(NUM_SIMULATIONS_PER_PARAMETER_COMBINATION):
                if testRandomInstanceConsecutive_ExactOne(n, k, standard):
                    violation = True
                    break
    if not violation:
        logging.critical("No violation instance found for scenario=AtLeastOne1, standard=%s", standard)


def batchTestConsecutiveNoneOrAll(standard):
    violation = False
    for n in range(SIMULATION_N_START, SIMULATION_N_END):
        for x in range(0, 1):
            for y in range(n, n + 1):
                for k in range(2, n):
                    for i in range(NUM_SIMULATIONS_PER_PARAMETER_COMBINATION):
                        if testRandomInstanceConsecutive_XorY(n, x, y, k, standard):
                            violation = True
                            break
    if not violation:
        logging.critical("No violation instance found for scenario NoneOrAll, standard=%s", standard)


def batchTestConsecutiveXOR(standard):
    violation = False
    for n in range(SIMULATION_N_START, SIMULATION_N_END):
        for k in range(2, n):
            for i in range(NUM_SIMULATIONS_PER_PARAMETER_COMBINATION):
                if testRandomInstanceConsecutive_XOR(n, k, standard):
                    violation = True
                    break
    if not violation:
        logging.critical("No violation instance found for scenario XOR, standard=%s", standard)


batchTestConsecutiveThreshold(DefinitionLevel.LOOSE)
batchTestConsecutiveAtLeastOne1(DefinitionLevel.STRICT)  # strict, because always the lowest k bits.
batchTestConsecutiveAll1s(DefinitionLevel.STRICT)  # strict, because always the highest k bits.
batchTestConsecutiveExactOne(DefinitionLevel.STRICT)
batchTestConsecutiveNoneOrAll(DefinitionLevel.STRICT)
batchTestConsecutiveXOR(DefinitionLevel.STRICT)
