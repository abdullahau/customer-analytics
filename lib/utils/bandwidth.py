import numpy as np
from scipy.stats import norm

__all__ = ["modified_silverman", "bw_nrd0"]


# Compute the bandwidth of kernel smoothing window using Silverman's rule of thumb (normal approximation method)
# https://www.mathworks.com/matlabcentral/answers/232493-ksdensity-default-bandwidth-value
# https://en.wikipedia.org/wiki/Median_absolute_deviation#Relation_to_standard_deviation
def modified_silverman(x):
    n = len(x)
    median_x = np.median(x)  # median
    mad = np.median(
        np.abs(x - median_x)
    )  # median absolute deviation (MAD) - median of the absolute deviations from the data's median
    k = 1 / norm.ppf(
        3 / 4
    )  # Conversion factor for normal distribution - scale factor k

    sigma = k * mad  # standard deviation

    bw = sigma * (4 / (3 * n)) ** (1 / 5)

    return bw


def bw_nrd0(x):
    """
    Implementation of R's rule-of-thumb for choosing the bandwidth of a Gaussian
    kernel density estimator. It defaults to 0.9 times the minimum of the standard
    deviation and the interquartile range divided by 1.34 times the sample size to
    the negative one-fifth power (= Silverman's ‘rule of thumb’, Silverman (1986,
    page 48, eqn (3.31))) unless the quartiles coincide when a positive result
    will be guaranteed.
    """
    if len(x) < 2:
        raise (Exception("need at least 2 data points"))

    hi = np.std(x, ddof=1)
    q75, q25 = np.percentile(x, [75, 25])
    iqr = q75 - q25
    lo = min(hi, iqr / 1.34)

    lo = lo or hi or abs(x[0]) or 1

    return 0.9 * lo * len(x) ** -0.2
