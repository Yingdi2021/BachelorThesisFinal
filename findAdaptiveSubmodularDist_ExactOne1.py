from helperMethods import *


def utilityGivenInputDataAndPartialRealisation_ExactOne1(inputData, partial_realization):
    ''' given a distribution (inputData) and a partial realisation, calculate the utility score.'''
    if np.sum(partial_realization == 1) > 1:
        # if there are  more than one 1 in the probed bits, then we are certain of our decision 100%
        return 1
    elif np.sum(partial_realization == 1) == 1:
        # if there's already one 1 in the probed bits, then compare the probability that there are no 1s in the
        # unprobedd bits with its counter prob.
        unprobed_bits_counter_probabilities = 1 - inputData[np.isnan(partial_realization)]
        p_all_unprobed_all_zeros = np.prod(unprobed_bits_counter_probabilities)
        return max(p_all_unprobed_all_zeros, 1 - p_all_unprobed_all_zeros)
    else:
        # if there's no 1 in the probed bits, then compare the  probability that  there are exactly one 1 in the
        # unprobed bits with its counter prob.
        unprobed_bits_probabilities = inputData[np.isnan(partial_realization)]
        p_exactly_one_1_in_unprobed = probabilityExactOne1(unprobed_bits_probabilities)
        return max(p_exactly_one_1_in_unprobed, 1 - p_exactly_one_1_in_unprobed)


def expectedMarginalBenefit_ExactOne1(inputData, partial_realization, e):
    ''' calculate the expected marginal benefit that a given "e" brings to a given partial realization. '''

    utility_without_e = utilityGivenInputDataAndPartialRealisation_ExactOne1(inputData, partial_realization)
    logging.info("utility of this partial realization=%s", np.round(utility_without_e, 5))  # rounding only in logging

    realisation_e_being_0 = partial_realization.copy()
    realisation_e_being_0[e] = 0
    utility_e_being_0 = utilityGivenInputDataAndPartialRealisation_ExactOne1(inputData, realisation_e_being_0)
    benefit_e_being_0 = utility_e_being_0 - utility_without_e
    probability_e_being_0 = 1 - inputData[e]

    realisation_e_being_1 = partial_realization.copy()
    realisation_e_being_1[e] = 1
    utility_e_being_1 = utilityGivenInputDataAndPartialRealisation_ExactOne1(inputData, realisation_e_being_1)
    benefit_e_being_1 = utility_e_being_1 - utility_without_e
    probability_e_being_1 = inputData[e]

    expected_marginal_benefit = benefit_e_being_1 * probability_e_being_1 + benefit_e_being_0 * probability_e_being_0
    logging.debug("expected marginal benefit after adding e (bit %s) = %s", e, np.round(expected_marginal_benefit,
                                                                                        ROUNDING_DIGIT_RESULT))
    return expected_marginal_benefit


def testDistribution_ExactOne1(inputData):
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
                            benefit_e_for_phi_small = expectedMarginalBenefit_ExactOne1(inputData, phi_small, e)
                            benefit_e_for_phi_big = expectedMarginalBenefit_ExactOne1(inputData, phi_big, e)
                            if benefit_e_for_phi_small - benefit_e_for_phi_big < -SIGNIFICANCE_LEVEL:
                                logging.error("At least one violation of AS found! phi1=%s, phi2=%s, e=%s", phi_small,
                                              phi_big, e)
                                return True  # violation detected
    # if all possible realizations are fine (no violation)
    logging.info("No violation found, u is adaptive submodular with respect to this distribution")
    return False


def systematicallyTest_ExactOne1(n):
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
        violation = testDistribution_ExactOne1(inputData)
        if not violation:
            logging.critical("distribution %s satisfies adaptive submodularity, counter prob=%s", inputData,
                             1 - inputData)


def testHypothesis_ExactOne1(endingN):
    """test our hypothesis that no distributions is adaptive submodular """
    for n in range(3, endingN + 1):
        for simulation_num in range(NUM_SIMULATIONS_PER_PARAMETER_COMBINATION):
            x = sorted(np.random.randint(1, 1000, n))  # To change
            inputData = np.divide(x, 1000)
            inputData = np.round(inputData, ROUNDING_DIGIT_INPUT)
            violation = testDistribution_ExactOne1(inputData)
            if not violation:
                logging.critical("this distribution %d is adaptive submodular!. Hypothesis not true!", inputData)
    logging.critical("No adaptive submodular distribution found.")


########################################################
# test a specific distribution
inputData = np.array([0.1, 0.2, 0.5, 0.8])
# violation = testDistribution_ExactOne1(inputData)

########################################################
# systematically test all possible distributions
n = 4
# systematicallyTest_ExactOne1(n)

########################################################
# Test Hypothesis with totally random distributions
trueOrFalse = testHypothesis_ExactOne1(5)
