import numpy as np

from findOptimalProbesets_Threshold import utilityOfProbeset_Threshold
from findOptimalProbesets_ExactX import utilityOfProbeset_ExactX
from findOptimalProbesets_XOR import utilityOfProbeset_XOR
from findOptimalProbesets_XorY import utilityOfProbeset_XorY
from helperMethods import findAllSubsets
from properties import *
from scenario import Scenario

logging.basicConfig(level=LOGGING_LEVEL)


def testSubmodularity(inputData, scenario):
    n = len(inputData)
    N = set(range(n))
    definitionSatisfied = True

    for aSetSize in range(1, n - 1):  # 1 to n-2
        for a in findAllSubsets(set(range(n)), aSetSize):
            # |B| = |A| + 1
            for BminusA in (N - set(a)):
                A = set(a)
                B = A.copy()
                B.add(BminusA)
                logging.debug("Set A = %s, Set B = %s", A, B)

                # i is a single bit from N-B
                for i in (N - B):
                    AI = A.copy()
                    AI.add(i)
                    BI = B.copy()
                    BI.add(i)
                    logging.debug("-- i=%s, AI=%s, BI=%s", i, AI, BI)

                    if scenario == Scenario.THRESHOLD:
                        l = 2
                        utilityA = utilityOfProbeset_Threshold(inputData, l, A)
                        utilityAI = utilityOfProbeset_Threshold(inputData, l, AI)
                        utilityB = utilityOfProbeset_Threshold(inputData, l, B)
                        utilityBI = utilityOfProbeset_Threshold(inputData, l, BI)
                    elif scenario == Scenario.ATLEASTONE:
                        utilityA = utilityOfProbeset_Threshold(inputData, 1, A)
                        utilityAI = utilityOfProbeset_Threshold(inputData, 1, AI)
                        utilityB = utilityOfProbeset_Threshold(inputData, 1, B)
                        utilityBI = utilityOfProbeset_Threshold(inputData, 1, BI)
                    elif scenario == Scenario.ALL1s:
                        utilityA = utilityOfProbeset_ExactX(inputData, n, A)
                        utilityAI = utilityOfProbeset_ExactX(inputData, n, AI)
                        utilityB = utilityOfProbeset_ExactX(inputData, n, B)
                        utilityBI = utilityOfProbeset_ExactX(inputData, n, BI)
                    elif scenario == Scenario.EXACTONE:
                        utilityA = utilityOfProbeset_ExactX(inputData, 1, A)
                        utilityAI = utilityOfProbeset_ExactX(inputData, 1, AI)
                        utilityB = utilityOfProbeset_ExactX(inputData, 1, B)
                        utilityBI = utilityOfProbeset_ExactX(inputData, 1, BI)
                    elif scenario == Scenario.NONEORALL:
                        utilityA = utilityOfProbeset_XorY(inputData, 0, n, A)
                        utilityAI = utilityOfProbeset_XorY(inputData, 0, n, AI)
                        utilityB = utilityOfProbeset_XorY(inputData, 0, n, B)
                        utilityBI = utilityOfProbeset_XorY(inputData, 0, n, BI)
                    elif scenario == Scenario.XOR:
                        utilityA = utilityOfProbeset_XOR(inputData, A)
                        utilityAI = utilityOfProbeset_XOR(inputData, AI)
                        utilityB = utilityOfProbeset_XOR(inputData, B)
                        utilityBI = utilityOfProbeset_XOR(inputData, BI)

                    deltaA = round(utilityAI - utilityA, ROUNDING_DIGIT_INPUT)
                    deltaB = round(utilityBI - utilityB, ROUNDING_DIGIT_INPUT)

                    logging.debug("---- uA=%s, uAI=%s, deltaA=%s, uB=%s, uBI=%s, deltaB=%s", utilityA, utilityAI,
                                  round(deltaA, ROUNDING_DIGIT_INPUT), utilityB, utilityBI,
                                  round(deltaB, ROUNDING_DIGIT_INPUT))
                    if deltaA < deltaB:
                        definitionSatisfied = False
                        logging.error("VIOLATION! inputdata=%s, A=%s, B=%s, i=%s: delta_a=%s, delta_b=%s",
                                      inputData, A, B, i, deltaA, deltaB)
    return definitionSatisfied


def runCounterExample():
    exampleInputData = np.array([0.1, 0.2, 0.5, 0.8])
    for scenario in Scenario:
        definitionSatisfied = testSubmodularity(exampleInputData, scenario)
        logging.critical("Is submodularity satisfied in Scenario %s?: %s", scenario, definitionSatisfied)


####################################################
runCounterExample() # In none of the scenarios is the utility function submodular.
