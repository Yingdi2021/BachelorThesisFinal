from helperMethods import *


def utilityGivenInputDataAndPartialRealisation_Threshold(inputData, partial_realization, l):
    ''' given a distribution (inputData) and a partial realisation, calculate the utility score.'''
    probed_bits = partial_realization[~np.isnan(partial_realization)]
    rest_probs = inputData[np.isnan(partial_realization)]
    n = len(inputData)
    k = len(probed_bits)
    r = n - k
    if sum(probed_bits) >= l:  # if there are already enough 1s in the probeset, then 100% sure
        return 1
    else:  # otherwise we campare the probability that there are enough 1s in the restset with its counter-probability
        missingNumberOf1 = int(l - sum(probed_bits))
        if missingNumberOf1 > r:  # then there can never be enough 1s.
            return 1
        else:
            result = 0
            for i in range(missingNumberOf1, r+1):
                result += probabilityCertainNumberOfEventsHappen(rest_probs, i)
            return max(result, 1-result)


def expectedMarginalBenefit_Threshold(inputData, partial_realization, e, l):
    ''' calculate the expected marginal benefit that a given "e" brings to a given partial realization. '''
    utility_without_e = utilityGivenInputDataAndPartialRealisation_Threshold(inputData, partial_realization, l)
    logging.debug("utility gvien this partial realization(%s)=%s", partial_realization,
                  np.round(utility_without_e, ROUNDING_DIGIT_RESULT))
    new_realizatiton = partial_realization.copy()
    new_realizatiton[e] = 1
    utility_e_being_1 = utilityGivenInputDataAndPartialRealisation_Threshold(inputData, new_realizatiton, l)
    new_realizatiton[e] = 0
    utility_e_being_0 = utilityGivenInputDataAndPartialRealisation_Threshold(inputData, new_realizatiton, l)
    benefit_e_being_1 = utility_e_being_1 - utility_without_e
    benefit_e_being_0 = utility_e_being_0 - utility_without_e
    probability_e_being_1 = inputData[e]
    probability_e_being_0 = 1-inputData[e]
    expected_marginal_benefit = benefit_e_being_1 * probability_e_being_1 + benefit_e_being_0 * probability_e_being_0
    logging.debug("expected marginal benefit after adding e (bit %s) = %s", e, np.round(expected_marginal_benefit,
                                                                                        ROUNDING_DIGIT_RESULT))
    return expected_marginal_benefit


def testDistribution_Threshold(inputData, l):
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
                            benefit_e_for_phi_small = expectedMarginalBenefit_Threshold(inputData, phi_small, e, l)
                            benefit_e_for_phi_big = expectedMarginalBenefit_Threshold(inputData, phi_big, e, l)
                            if benefit_e_for_phi_small - benefit_e_for_phi_big < -SIGNIFICANCE_LEVEL:
                                logging.error("At least one violation of AS found! phi1=%s, phi2=%s, e=%s", phi_small,
                                              phi_big, e)
                                return True  # violation detected
    # if all possible realizations are fine (no violation)
    logging.info("No violation found, u is adaptive submodular with respect to this distribution")
    return False


def systematicallyTest_Threshold(n):
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

    for l in range(2, n):  # we don't consider l=1 or l=n, both addressed in other scenarios.
        adaptiveSubmodularDistributionExist = False
        for combi in combinations_without_repetition_sorted:
            inputData = np.array(combi)
            violation = testDistribution_Threshold(inputData, l)
            if not violation:
                adaptiveSubmodularDistributionExist = True
                logging.critical("distribution %s satisfies adaptive submodularity, l=%s", inputData, l)
        if not adaptiveSubmodularDistributionExist:
            logging.critical("No distribution found that satisfies AS when l=%s", l)


def testHypothesis_Threshold(endingN):
    """test our hypothesis that no distributions is adaptive submodular """
    adaptiveSubmodularDistributionExist = False
    for n in range(3, endingN + 1):
        for l in range(2, n):  # we don't consider l=1 or l=n, both addressed in other scenarios.
            for simulation_num in range(NUM_SIMULATIONS_PER_PARAMETER_COMBINATION):
                x = sorted(np.random.randint(1, 1000, n))  # To change
                inputData = np.divide(x, 1000)
                inputData = np.round(inputData, ROUNDING_DIGIT_INPUT)
                violation = testDistribution_Threshold(inputData, l)
                if not violation:
                    adaptiveSubmodularDistributionExist = True
                    logging.critical("this distribution %d is adaptive submodular!. Hypothesis not true!", inputData)
    if not adaptiveSubmodularDistributionExist:
        logging.critical("No adaptive submodular distribution for any l between (2,n) found.")


########################################################
# test a specific distribution
inputData = np.array([0.1, 0.2, 0.5, 0.8])
# violation = testDistribution_Threshold(inputData, 3)

########################################################
# systematically test all possible distributions
n = 5
# systematicallyTest_Threshold(n)

########################################################
# Test Hypothesis with totally random distributions
trueOrFalse = testHypothesis_Threshold(n)
