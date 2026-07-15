# https://stackoverflow.com/questions/60669256/how-do-you-create-a-logit-normal-distribution-in-python

import numpy as np
from scipy.special import logit, expit
from scipy.stats import norm, rv_continuous, kstest

__all__ = ["LogitNormal"]

# class LogitNorm(rv_continuous):

#     def _argcheck(self, m, s):
#         return (s > 0.) & (m > -np.inf)

#     def _pdf(self, x, m, s):
#         return norm(loc=m, scale=s).pdf(logit(x))/(x*(1-x))

#     def _cdf(self, x, m, s):
#         return norm(loc=m, scale=s).cdf(logit(x))

#     def _rvs(self, m, s, size=None, random_state=None):
#         return expit(m + s*random_state.standard_normal(size))

#     def fit(self, data, **kwargs):
#         return norm.fit(logit(data), **kwargs)


class LogitNormal(rv_continuous):
    def __init__(self, scale=1, loc=0):
        super().__init__(self)
        self.scale = scale
        self.loc = loc

    def _pdf(self, x):
        return norm.pdf(logit(x), loc=self.loc, scale=self.scale) / (x * (1 - x))


if __name__ == "__main__":
    # logitnorm = LogitNorm(a=0.0, b=1.0, name="logitnorm")

    # N = 1000
    # law = logitnorm(0.24, 1.31)             # Defining a RV
    # sample = law.rvs(size=N)                # Sampling from RV
    # params = logitnorm.fit(sample)          # Infer parameters w/ MLE
    # check = kstest(sample, law.cdf)         # Hypothesis testing
    # bins = np.arange(0.0, 1.1, 0.1)         # Bin boundaries
    # expected = np.diff(law.cdf(bins))       # Expected bin counts

    # print(sample)

    LogitNormal(scale=1.78, loc=0).pdf(10000)
