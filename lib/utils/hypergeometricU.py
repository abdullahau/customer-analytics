# https://functions.wolfram.com/07.33.02.0001.01
# https://stackoverflow.com/questions/49932930/tricomi-hypergeometric-u-in-python
import numpy as np
from scipy.special import gamma, hyp1f1, gammaincc

__all__ = ["U", "U_incomplete_gamma"]

def U(a, b, z):
    '''
    U(a,b,z)=\frac{\Gamma(1-b)}{\Gamma(a+1-b)}1F1(a,b,z)+\frac{\Gamma(b-1)}{\Gamma(a)}z^{1-b}1F1(a+1-b,2-b,z)
    '''    
    # First term of the equation
    term1 = gamma(1 - b) / gamma(a + 1 - b) * hyp1f1(a, b, z)

    # Second term of the equation
    term2 = gamma(b - 1) / gamma(a) * z**(1 - b) * hyp1f1(a + 1 - b, 2 - b, z)

    # Combine the terms
    result = term1 + term2
    return result

def U_incomplete_gamma(a, z):
    # https://functions.wolfram.com/07.33.03.0003.01
    '''
    confluent hypergeometric function of the second kind expressed in terms incomplete gamma function when a = c
    Compute e^z * Gamma(1 - a, z)
    '''
    gamma_upper = gamma(1 - a) * gammaincc(1 - a, z)  # Upper incomplete gamma
    result = np.exp(z) * gamma_upper
    return result
