import numpy as np
import unittest
from findOptimalProbesets_ExactX import findOptimalProbesets_ExactX
from findOptimalProbesets_XorY import findOptimalProbesets_XorY
from helperMethods import findAllSubsets

class testUtilityImplementations(unittest.TestCase):

    ############################## All '1' or no '1' ##############################
    def test_all_1s_or_no_1s_A(self):
        input = np.array([0.9615, 0.8872, 0.6361])
        x = 0
        y = len(input)
        k = 3
        maxSets, maxU, optimumType = findOptimalProbesets_XorY(input, x, y, k)
        self.assertEqual(maxSets, {(0, 1, 2)})
        self.assertEqual(maxU, 1)

    def test_all_1s_or_no_1s_B(self):
        input = np.array([0.9416, 0.4679, 0.4054, 0.3818, 0.1685, 0.1577, 0.1392, 0.0951] )
        x = 0
        n = len(input)
        y = n
        k = 3
        maxSets, maxU, optimumType = findOptimalProbesets_XorY(input, x, y, k)
        # expected outcome: all subsets of size k are optimal
        self.assertEqual(len(maxSets), len(findAllSubsets(set(range(n)), k)))
        self.assertEqual(round(maxU,6), 0.993745)

    def test_all_1s_or_no_1s_C(self):
        input = np.array([0.8952, 0.7803, 0.6411, 0.585,  0.399,  0.3972, 0.295, 0.262])
        x = 0
        y = len(input)
        k = 6
        maxSets, maxU, optimumType = findOptimalProbesets_XorY(input, x, y, k)
        self.assertEqual(maxSets, {(2, 3, 4, 5, 6, 7)})
        self.assertEqual(round(maxU,6), 0.997969)

    def test_all_1s_or_no_1s_D(self):
        input = np.array([0.9547, 0.669,  0.6313, 0.5828, 0.2072] )
        x = 0
        y = len(input)
        k = 4
        maxSets, maxU, optimumType = findOptimalProbesets_XorY(input, x, y, k)
        self.assertEqual(maxSets, {(1,2,3,4)})
        self.assertEqual(round(maxU,6), 0.995861)

#     ############################## Exactly one '1' ##############################
    def test_exactly_one_1s_A(self):
        input = np.array([0.4947, 0.3994, 0.344,  0.2253])
        m = 1
        k = 3
        maxSets, maxU, optimumType = findOptimalProbesets_ExactX(input, m, k)
        self.assertEqual(maxSets, {(0,1,2)})
        self.assertEqual(round(maxU,6), 0.857884)

    def test_exactly_one_1s_B(self):
        input = np.array([0.8527, 0.8081, 0.6303, 0.3062, 0.271,  0.2024, 0.1187, 0.0238])
        m = 1
        k = 6
        maxSets, maxU, optimumType = findOptimalProbesets_ExactX(input, m, k)
        self.assertEqual(maxSets, {(0,1,2,3,4,5)})
        self.assertEqual(round(maxU,6), 0.991903)

    def test_exactly_one_1s_C(self):
        input = np.array([0.7752, 0.6877, 0.6528, 0.2347, 0.0502])
        m = 1
        k = 5
        maxSets, maxU, optimumType = findOptimalProbesets_ExactX(input, m, k)
        self.assertEqual(maxSets, {(0,1,2,3,4)})
        self.assertEqual(round(maxU,6), 1.0)

    def test_exactly_one_1s_D(self):
        input = np.array([0.9882, 0.9722, 0.6802, 0.5504, 0.4576, 0.4224, 0.1661])
        n = len(input)
        m = 1
        k = 2
        maxSets, maxU, optimumType = findOptimalProbesets_ExactX(input, m, k)
        # expected outcome: all subsets of size k are optimal
        self.assertEqual(len(maxSets), len(findAllSubsets(set(range(n)), k)))
        self.assertEqual(round(maxU,6), 0.998474)
