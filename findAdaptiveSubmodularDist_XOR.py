from helperMethods import *


def utilityGivenInputDataAndPartialRealisation_XOR(inputData, partial_realization):
    ''' given a distribution (inputData) and a partial realisation, calculate the utility score.'''
    # 1. if there are even number of 1s in the probeset
    # utility = max(p_rest_even, 1-p_rest_even)
    # 2. if there are odd number of 1s in probeset:
    # utility = max(p_rest_odd, 1-p_rest_odd)
    # Note that p_rest_odd = 1-p_rest_even; 1-p_rest_odd = p_rest_even
    # --> no matter how probeset looks like, u is always max(p_rest_even, p_rest_odd)
    ############################ !!!!!!!!!!!!!!!!!! ############################
    # It's not about the partial realization, but the rest-probabilities, i.e. which bits are unprobed/left.
    ############################################################################
    rest_probs = inputData[np.isnan(partial_realization)]
    p_rest_even = probabilityEvenNumberOfEventsHappen(rest_probs)
    logging.debug("prob that rest set has even number of 1s=%s", p_rest_even)
    utility = max(p_rest_even, 1 - p_rest_even)
    return round(utility, ROUNDING_DIGIT_RESULT)


def expectedMarginalBenefit_XOR(inputData, partial_realization, e):
    ''' calculate the expected marginal benefit that a given "e" brings to a given partial realization. '''
    utility_without_e = utilityGivenInputDataAndPartialRealisation_XOR(inputData, partial_realization)
    logging.debug("utility gvien this partial realization(%s)=%s", partial_realization,
                  np.round(utility_without_e, ROUNDING_DIGIT_RESULT))
    new_realizatiton = partial_realization.copy()
    new_realizatiton[e] = 1
    utility_e_being_1 = utilityGivenInputDataAndPartialRealisation_XOR(inputData, new_realizatiton)
    new_realizatiton[e] = 0
    utility_e_being_0 = utilityGivenInputDataAndPartialRealisation_XOR(inputData, new_realizatiton)
    benefit_e_being_1 = utility_e_being_1 - utility_without_e
    benefit_e_being_0 = utility_e_being_0 - utility_without_e
    probability_e_being_1 = inputData[e]
    probability_e_being_0 = 1 - inputData[e]
    expected_marginal_benefit = benefit_e_being_1 * probability_e_being_1 + benefit_e_being_0 * probability_e_being_0
    logging.debug("utility_e_being_1=%s, utility_e_being_0=%s, prob_e_1=%s,  prob_e_0=%s", utility_e_being_1,
                  utility_e_being_0, probability_e_being_1, probability_e_being_0)
    logging.debug("expected marginal benefit after adding e (bit %s) = %s", e, np.round(expected_marginal_benefit,
                                                                                        ROUNDING_DIGIT_RESULT))
    return expected_marginal_benefit


def testDistribution_XOR(inputData):
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
                            benefit_e_for_phi_small = expectedMarginalBenefit_XOR(inputData, phi_small, e)
                            benefit_e_for_phi_big = expectedMarginalBenefit_XOR(inputData, phi_big, e)
                            if benefit_e_for_phi_small - benefit_e_for_phi_big < -SIGNIFICANCE_LEVEL:
                                logging.error("At least one violation of AS found! phi1=%s, phi2=%s, e=%s", phi_small,
                                              phi_big, e)
                                return True  # violation detected
    # if all possible realizations are fine (no violation)
    logging.info("No violation found, u is adaptive submodular with respect to this distribution")
    return False


def systematicallyTest_XOR(n):
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

    adaptiveSubmodularDistributionExist = False
    for combi in combinations_without_repetition_sorted:
        inputData = np.array(combi)
        violation = testDistribution_XOR(inputData)
        if not violation:
            adaptiveSubmodularDistributionExist = True
            logging.critical("distribution %s satisfies adaptive submodularity.", inputData)
    if not adaptiveSubmodularDistributionExist:
        logging.critical("No distribution found that satisfies AS.")


def testHypothesis_XOR(endingN):
    """test our hypothesis that no distributions is adaptive submodular """
    adaptiveSubmodularDistributionExist = False
    for n in range(3, endingN + 1):
        for simulation_num in range(NUM_SIMULATIONS_PER_PARAMETER_COMBINATION):
            x = sorted(np.random.randint(1, 1000, n))  # To change
            inputData = np.divide(x, 1000)
            inputData = np.round(inputData, ROUNDING_DIGIT_INPUT)
            violation = testDistribution_XOR(inputData)
            if not violation:
                adaptiveSubmodularDistributionExist = True
                logging.critical("this distribution %d is adaptive submodular!. Hypothesis not true!", inputData)
    if not adaptiveSubmodularDistributionExist:
        logging.critical("No adaptive submodular distribution found.")


########################################################
# test a specific distribution
inputData = np.array([0.1, 0.2, 0.5, 0.8])
# violation = testDistribution_XOR(inputData)

########################################################
# systematically test all possible distributions
n = 4
# systematicallyTest_XOR(n)

########################################################
# Test Hypothesis with totally random distributions
trueOrFalse = testHypothesis_XOR(n)
