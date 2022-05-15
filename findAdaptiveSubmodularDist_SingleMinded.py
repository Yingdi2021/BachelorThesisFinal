from helperMethods import *


def isAlreadySmallerThanReferenceVector(phi, referenceVector):
    for i in range(len(phi)):
        if phi[i] < referenceVector[i]:
            return True
    return False


def utilityGivenInputDataAndPartialRealisation_SingleMinded(inputData, referenceVector, partial_realization):
    if isAlreadySmallerThanReferenceVector(partial_realization, referenceVector):
        # if this partial realisation is already "smaller" than reference-vector, then we are certain of our decision.
        return 1
    else:
        # if all probed-bits are fine then compare the probability that all unprobed bits >= ref (i.e. all the bits
        # where ref==1, we have also 1) with its counter-probability.
        all_unprobed_bits_that_must_be_1s = np.where((referenceVector == 1) & (np.isnan(partial_realization)))
        prob_satisfy = np.prod(inputData[all_unprobed_bits_that_must_be_1s])
        return max(prob_satisfy, 1 - prob_satisfy)


def expectedMarginalBenefit_SingleMinded(inputData, referenceVector, partial_realization, e):
    utility_without_e = utilityGivenInputDataAndPartialRealisation_SingleMinded(inputData, referenceVector,
                                                                                partial_realization)
    logging.debug("utility of this partial realization=%s", np.round(utility_without_e, 5))  # rounding only in logging

    realisation_e_being_0 = partial_realization.copy()
    realisation_e_being_0[e] = 0
    utility_e_being_0 = utilityGivenInputDataAndPartialRealisation_SingleMinded(inputData, referenceVector,
                                                                                realisation_e_being_0)
    probability_e_being_0 = 1 - inputData[e]

    realisation_e_being_1 = partial_realization.copy()
    realisation_e_being_1[e] = 1
    utility_e_being_1 = utilityGivenInputDataAndPartialRealisation_SingleMinded(inputData, referenceVector,
                                                                                realisation_e_being_1)
    probability_e_being_1 = inputData[e]

    benefit_e_being_0 = utility_e_being_0 - utility_without_e
    benefit_e_being_1 = utility_e_being_1 - utility_without_e

    expected_marginal_benefit = benefit_e_being_0 * probability_e_being_0 + benefit_e_being_1 * probability_e_being_1

    logging.debug("expected marginal benefit after adding e (bit %s) = %s", e,
                  np.round(expected_marginal_benefit, ROUNDING_DIGIT_RESULT))
    return expected_marginal_benefit


def testIfViolatesSubmodularity(inputData, referenceVector, smallerSet, biggerSet, e):
    n = len(inputData)
    phi_template = np.empty(n)
    phi_template[:] = np.NAN

    small_possibilities = list(itertools.product([0, 1], repeat=len(smallerSet)))
    for small_possbility in small_possibilities:
        if not isAlreadySmallerThanReferenceVector(small_possbility, referenceVector):
            phi_1 = phi_template.copy()
            phi_1[list(smallerSet)] = small_possbility
            differenceSet = set(biggerSet) - set(smallerSet)
            # consider all possibilities of the differenceSet!!!!!!
            possbilities = list(itertools.product([0, 1], repeat=len(differenceSet)))
            for possibility in possbilities:
                phi_2 = phi_1.copy()
                phi_2[list(differenceSet)] = possibility
                logging.info("phi_small=%s, phi_big=%s", phi_1, phi_2)
                expectedMarginBenefit_e_for_phi_1 = expectedMarginalBenefit_SingleMinded(inputData, referenceVector,
                                                                                         phi_1, e)
                if expectedMarginBenefit_e_for_phi_1 < -ALLOWED_ERROR:
                    logging.critical("warning: expected margin benefit < 0!!!!!!!!!")
                logging.info("expected Margin Benefit of e for phi_small=%s",
                             round(expectedMarginBenefit_e_for_phi_1, 3))
                expectedMarginBenefit_e_for_phi_2 = expectedMarginalBenefit_SingleMinded(inputData, referenceVector,
                                                                                         phi_2, e)
                logging.info("expected Margin Benefit of e for phi_big=%s", round(expectedMarginBenefit_e_for_phi_2, 3))
                logging.info("-----")
                if expectedMarginBenefit_e_for_phi_1 - expectedMarginBenefit_e_for_phi_2 < -ALLOWED_ERROR:
                    logging.error("--> at least one violation of adaptive submodularity found! phi1=%s, phi2=%s, e=%s",
                                  smallerSet,
                                  biggerSet, e)
                    return True  # violation detected
    # if all possibilities are fine (no violation)
    logging.info("no violation for this combination of phi_small & phi_big")
    logging.info("-------------------------------------------------------------")
    return False


def testDistribution_SingleMinded(inputData, referenceVector):
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
                            benefit_e_for_phi_small = expectedMarginalBenefit_SingleMinded(inputData, referenceVector,
                                                                                           phi_small, e)
                            benefit_e_for_phi_big = expectedMarginalBenefit_SingleMinded(inputData, referenceVector,
                                                                                         phi_big, e)
                            if benefit_e_for_phi_small - benefit_e_for_phi_big < -SIGNIFICANCE_LEVEL:
                                logging.error( "At least one violation of AS found! InputData=%s, ref=%s, phi1=%s, phi2=%s, e=%s",
                                    inputData, referenceVector, phi_small, phi_big, e)
                                return True  # violation detected
    # if all possible realizations are fine (no violation)
    logging.info("No violation found, u is adaptive submodular with respect to this distribution and reference vector")
    return False

def testHypothesis_SingleMinded(n):
    # Test all possible reference vector
    combinations = list(itertools.product([0, 1], repeat=n))
    for combi in combinations:
        referenceVector = np.array(combi)
        logging.info("testing for reference vector=%s...", referenceVector)
        hypothesis = True
        # case 1
        if sum(combi) == 0:
            # then there is no acceptance criteria at all. All realizations are fine --> always 100%  right decition.
            # we don't expect any violation.
            for n in range(n, n + 1):
                for simulation_num in range(NUM_SIMULATIONS_PER_PARAMETER_COMBINATION):
                    x = sorted(np.random.randint(1, 1000, n))
                    inputData = np.divide(x, 1000)
                    inputData = np.round(inputData, ROUNDING_DIGIT_INPUT)
                    violation = testDistribution_SingleMinded(inputData, referenceVector)
                    if violation:
                        logging.critical("no violation expected, but occured. distribution=%s", inputData)
                        hypothesis = False
            if hypothesis:
                logging.critical("Any distribution is AS when ref-vector=%s", referenceVector)
        # case 2
        elif sum(combi) == 1:  # then we don't expect any violation. Any distribution is adaptive submodular.
            for n in range(n, n + 1):
                for simulation_num in range(NUM_SIMULATIONS_PER_PARAMETER_COMBINATION):
                    x = sorted(np.random.randint(1, 1000, n))
                    inputData = np.divide(x, 1000)
                    inputData = np.round(inputData, ROUNDING_DIGIT_INPUT)  # round input data

                    violation = testDistribution_SingleMinded(inputData, referenceVector)

                    if violation:
                        logging.critical("no violation expected, but occured. distribution=%s", inputData)
                        hypothesis = False
            if hypothesis:
                logging.critical("Any distribution is AS when ref-vector=%s", referenceVector)
        # case 3
        elif sum(combi) == n:  # d.h. all 1s.
            for n in range(n, n + 1):
                for simulation_num in range(NUM_SIMULATIONS_PER_PARAMETER_COMBINATION):
                    x = sorted(np.random.randint(1, 1000, n))
                    inputData = np.divide(x, 1000)
                    inputData = np.round(inputData, ROUNDING_DIGIT_INPUT)
                    violation = testDistribution_SingleMinded(inputData, referenceVector)
                    if np.prod(inputData[:-1]) >= 0.5: # then should be no violation
                        if violation:
                            logging.critical("no violation expected, but occured. distribution=%s", inputData)
                            hypothesis = False
                    else: # expect violation
                        if not violation:
                            logging.critical("violation expected, but did not occur. distribution=%s", inputData)
                            hypothesis = False
            if hypothesis:
                logging.critical("Any distribution is AS when ref-vector=%s", referenceVector)
        # case 4
        else: # lies within (1,n)
            bits_that_are_1 = np.where(referenceVector == 1)
            for n in range(n, n + 1):
                for simulation_num in range(NUM_SIMULATIONS_PER_PARAMETER_COMBINATION):
                    x = sorted(np.random.randint(1, 1000, n))
                    inputData = np.divide(x, 1000)
                    inputData = np.round(inputData, ROUNDING_DIGIT_INPUT)  # round input data
                    violation = testDistribution_SingleMinded(inputData, referenceVector)
                    if np.prod(inputData[bits_that_are_1]) >= 0.5:
                        # then we don't expect any violation of adaptive submodularity
                        if violation:
                            logging.critical("no violation expected, but occured. distribution=%s", inputData)
                            hypothesis = False
                    else:
                        # then we expect a violation
                        if not violation:
                            logging.critical("violation expected but did not occur. Distribution=%s", inputData)
                            hypothesis = False
            if hypothesis:
                logging.critical("Any distribution is AS when ref-vector=%s", referenceVector)

########################################################
####test individual distribution
inputData = np.array([0.2, 0.4, 0.5, 0.8])
referenceVector = np.array([1, 1, 1, 1])
# violation = testDistribution_SingleMinded(inputData,referenceVector)

########################################################
# Test Hypothesis with totally random distributions
testHypothesis_SingleMinded(4)