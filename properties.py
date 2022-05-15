import logging
LOGGING_LEVEL = logging.CRITICAL

# due to the inaccurate nature of float numbers:
# if the difference of two numbers is too small, we consider them to be the same.
SIGNIFICANCE_LEVEL = pow(10, -10)

# Float inaccuracy issues: limiting float to x decimal points
# For calculated result (e.g. utility scores)
ROUNDING_DIGIT_RESULT = 11
# For input (e.g. random generated inputData)
ROUNDING_DIGIT_INPUT = 3
ROUNDING_DIGIT_WEIGHTS = 1

NUM_SIMULATIONS_PER_PARAMETER_COMBINATION = 100000
SIMULATION_N_START = 3
SIMULATION_N_END = 6


