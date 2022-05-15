from helperMethods import *
from findAdaptiveSubmodularDist_Threshold import testDistribution_Threshold

def utilityGivenInputDataAndPartialRealisation_AllOne(inputData, partial_realization):
    ''' given a distribution (inputData) and a partial realisation, calculate the utility score.'''
    if not partial_realization.all():  # if there's a 0, then we are certain of our decision: 100% correct.
        return 1
    else:  # otherwise we campare the probability that all unprobed bits are 1s with its counter-probability and
        # choose the greater one
        unprobed_bits = inputData[np.isnan(partial_realization)]
        p_all_unprobed_all_ones = np.prod(unprobed_bits)
        return max(p_all_unprobed_all_ones, 1 - p_all_unprobed_all_ones)


def expectedMarginalBenefit_AllOne(inputData, partial_realization, e):
    ''' calculate the expected marginal benefit that a given "e" brings to a given partial realization. '''
    utility_without_e = utilityGivenInputDataAndPartialRealisation_AllOne(inputData, partial_realization)
    logging.debug("utility gvien this partial realization(%s)=%s", partial_realization, np.round(utility_without_e,
                                                                                                 ROUNDING_DIGIT_RESULT))
    new_realizatiton = partial_realization.copy()
    new_realizatiton[e] = 1
    utility_e_being_1 = utilityGivenInputDataAndPartialRealisation_AllOne(inputData, new_realizatiton)
    utility_e_being_0 = 1  # then we are 100% sure to reject.
    benefit_e_being_1 = utility_e_being_1 - utility_without_e
    benefit_e_being_0 = utility_e_being_0 - utility_without_e
    probability_e_being_1 = inputData[e]
    expected_marginal_benefit = benefit_e_being_1 * probability_e_being_1 + benefit_e_being_0 * (
            1 - probability_e_being_1)
    logging.debug("expected marginal benefit after adding e (bit %s) = %s", e,
                  np.round(expected_marginal_benefit, ROUNDING_DIGIT_RESULT))
    return expected_marginal_benefit


def testDistribution_All1s(inputData):
    ''' test if the utility function is adaptive submodular with respect to this specific distribution.
    Go through every possible partial-realization and its sub-realization and every possible e out of the rest set to
    see if there are violations. Return false if there are no violations to the definition. '''
    n = len(inputData)
    phi_template = np.empty(n)
    phi_template[:] = np.NAN
    phi_complete = phi_template.copy()
    realizations = list(itertools.product([0, 1], repeat=n))
    for realization in realizations:
        phi_complete[:] = realization
        for size_bigger_set in range(2, n):
            for biggerSet in findAllSubsets(set(range(n)), size_bigger_set):
                restSet = set(range(n)) - set(biggerSet)
                for size_smaller_set in range(1, size_bigger_set):
                    for smallerSet in findAllSubsets(biggerSet, size_smaller_set):
                        phi_small = phi_template.copy()
                        phi_small[list(smallerSet)] = [realization[index] for index in smallerSet]
                        phi_big = phi_template.copy()
                        phi_big[list(biggerSet)] = [realization[index] for index in biggerSet]
                        for e in restSet:
                            benefit_e_for_phi_small = expectedMarginalBenefit_AllOne(inputData, phi_small, e)
                            benefit_e_for_phi_big = expectedMarginalBenefit_AllOne(inputData, phi_big, e)
                            if benefit_e_for_phi_small - benefit_e_for_phi_big < -SIGNIFICANCE_LEVEL:
                                logging.error("At least one violation of AS found! phi1=%s, phi2=%s, e=%s", phi_small,
                                              phi_big, e)
                                return True  # violation detected
    # if all possible realizations are fine (no violation)
    logging.info("No violation found, u is adaptive submodular with respect to this distribution")
    return False


def systematicallyTest_All1s(n):
    possible_bits = np.round(np.linspace(0.1, 0.9, 9), 1)
    combinations = list(itertools.product(possible_bits, repeat=n))
    combinations_without_repetition = set()
    for combi in combinations:
        sorted_combi = tuple(sorted(combi))
        if sorted_combi not in combinations_without_repetition:
            combinations_without_repetition.add(sorted_combi)

    combinations_without_repetition_sorted = sorted(combinations_without_repetition)
    # for combi in combinations_without_repetition_sorted:
    #     print(combi)

    for combi in combinations_without_repetition_sorted:
        inputData = np.array(combi)
        violation = testDistribution_All1s(inputData)
        # violation = testDistribution_Threshold(inputData, n) # is equivalent.
        if not violation:
            logging.critical("distribution %s satisfies adaptive submodularity", inputData)


def testHypothesis(endingN):
    for n in range(3, endingN + 1):
        for simulation_num in range(NUM_SIMULATIONS_PER_PARAMETER_COMBINATION):
            x = sorted(np.random.randint(1, 1000, n))  # To change
            inputData = np.divide(x, 1000)
            inputData = np.round(inputData, ROUNDING_DIGIT_INPUT)
            # violation = testDistribution_All1s(inputData)
            violation = testDistribution_Threshold(inputData, n) # is equivalent
            if violation:
                if np.prod(inputData[:-1]) > 0.5:
                    logging.critical("unexpected violation observed, Hypothesis not true!")
                    logging.critical("inputdata=%s, product=%s", inputData, np.prod(inputData[:-1]))
                    return False
            else:  # no violation
                if np.prod(inputData[:-1]) < 0.5:
                    logging.critical("Violation expected but did not occur, Hypothesis not true!")
                    logging.critical("inputdata=%s, product=%s", inputData, np.prod(inputData[:-1]))
                    return False
    logging.critical("No counter-evidence to the Hypothesis found.")
    return True


#################################################################################
# test a specific distribution
inputData = np.array([0.8, 0.9, 0.9])
# violation = testDistribution_All1s(inputData)
# violation = testDistribution_Threshold(inputData, len(inputData)) # is equivalent

########################################################
# systematically test all possible distributions
n = 4
systematicallyTest_All1s(n)

########################################################
# Test Hypothesis with totally random distributions
trueOrFalse = testHypothesis(n)
