from helperMethods import *
from findAdaptiveSubmodularDist_Threshold import testDistribution_Threshold


def utilityGivenInputDataAndPartialRealisation_AtLeastOne1(inputData, partial_realization):
    ''' given a distribution (inputData) and a partial realisation, calculate the utility score.'''
    if np.any(partial_realization == 1):  # if there's a 1 in the probed bits, then we are certain of our decision 100%
        return 1
    else:  # otherwise we campare the probability that all unprobed bits are 0s with its counter-probability
        unprobed_bits_counter_probabilities = 1 - inputData[np.isnan(partial_realization)]
        p_all_unprobed_all_zeros = np.prod(unprobed_bits_counter_probabilities)
        return max(p_all_unprobed_all_zeros, 1 - p_all_unprobed_all_zeros)


def expectedMarginalBenefit_AtLeastOne1(inputData, partial_realization, e):
    ''' calculate the expected marginal benefit that a given "e" brings to a given partial realization. '''
    utility_without_e = utilityGivenInputDataAndPartialRealisation_AtLeastOne1(inputData, partial_realization)
    logging.debug("utility gvien this partial realization(%s)=%s", partial_realization,
                  np.round(utility_without_e, ROUNDING_DIGIT_RESULT))
    utility_e_being_1 = 1  # then we are 100% sure to accept.
    new_realizatiton = partial_realization.copy()
    new_realizatiton[e] = 0
    utility_e_being_0 = utilityGivenInputDataAndPartialRealisation_AtLeastOne1(inputData, new_realizatiton)
    benefit_e_being_1 = utility_e_being_1 - utility_without_e
    benefit_e_being_0 = utility_e_being_0 - utility_without_e
    probability_e_being_1 = inputData[e]
    expected_marginal_benefit = benefit_e_being_1 * probability_e_being_1 + benefit_e_being_0 * (
            1 - probability_e_being_1)
    logging.debug("expected marginal benefit after adding e (bit %s) = %s", e, np.round(expected_marginal_benefit,
                                                                                        ROUNDING_DIGIT_RESULT))
    return expected_marginal_benefit


def testDistribution_AtLeastOne1(inputData):
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
                            benefit_e_for_phi_small = expectedMarginalBenefit_AtLeastOne1(inputData, phi_small, e)
                            benefit_e_for_phi_big = expectedMarginalBenefit_AtLeastOne1(inputData, phi_big, e)
                            if benefit_e_for_phi_small - benefit_e_for_phi_big < -SIGNIFICANCE_LEVEL:
                                logging.error("At least one violation of AS found! phi1=%s, phi2=%s, e=%s", phi_small,
                                              phi_big, e)
                                return True  # violation detected
    # if all possible realizations are fine (no violation)
    logging.info("No violation found, u is adaptive submodular with respect to this distribution")
    return False


def systematicallyTest_AtLeastOne1(n):
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
        # violation = testDistribution_AtLeastOne1(inputData)
        violation = testDistribution_Threshold(inputData, 1) # is equivalent
        if not violation:
            logging.critical("distribution %s satisfies adaptive submodularity, counter prob=%s", inputData,
                             1 - inputData)


def testHypothesis(endingN):
    """test our hypothesis with totally random inputData """
    for n in range(3, endingN + 1):
        for simulation_num in range(NUM_SIMULATIONS_PER_PARAMETER_COMBINATION):
            x = sorted(np.random.randint(1, 1000, n))  # To change
            inputData = np.divide(x, 1000)
            inputData = np.round(inputData, ROUNDING_DIGIT_INPUT)
            # violation = testDistribution_AtLeastOne1(inputData)
            violation = testDistribution_Threshold(inputData, 1) # is equivalent
            # do we expect a violation?
            counter_inputData = sorted(1 - inputData)
            if np.prod(counter_inputData[:-1]) > 0.5:  # Should: no violation
                if violation:  # if nevertheless occurs:
                    logging.critical("unexpected violation observed, Hypothesis not true!")
                    logging.critical("inputdata=%s", inputData)
                    return False
            if np.prod(counter_inputData[:-1]) < 0.5:  # Should: violation
                if not violation:
                    logging.critical("expected violation not found, Hypothesis not true!")
                    logging.critical("inputdata=%s", inputData)
                    return False
    logging.critical("No counter-evidence to the Hypothesis found.")
    return True


########################################################
## test a specific distribution
# inputData = np.array([0.1, 0.2, 0.5, 0.8])
# violation = testDistribution(inputData)

########################################################
# systematically test all possible distributions
n = 4
systematicallyTest_AtLeastOne1(n)

########################################################
# Test Hypothesis with totally random distributions
# trueOrFalse = testHypothesis(n)
