import numpy as np

__all__ = ["aic", "bic"]


# https://en.wikipedia.org/wiki/Akaike_information_criterion
def aic(k, log_likelihood):
    """
    Akaike Information Criterion
    k: number of parameters in the model
    log_likelihood: minimized, positive (or maximized, negative) log value of the likelihood function
    """
    if log_likelihood < 0:
        log_likelihood *= -1
    return (2 * k) + (2 * log_likelihood)


# https://en.wikipedia.org/wiki/Bayesian_information_criterion
def bic(k, n, log_likelihood):
    """
    Bayesian Information Criterion
    k: number of parameters in the model
    n: number of data points or number of observations, i.e. the x in the  likelihood function L = p(x | θ, M)
       where M is the model, θ  are the parameters values that maximize the likelihood function and x is the observed data
       x in our case is the total number of customers in in the cohort
    log_likelihood: minimized, positive (or maximized, negative) log value of the likelihood function
    """
    if log_likelihood < 0:
        log_likelihood *= -1
    return (k * np.log(n)) + (2 * log_likelihood)
