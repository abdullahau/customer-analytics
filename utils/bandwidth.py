import numpy as np
from scipy.stats import norm

# Compute the bandwidth of kernel smoothing window using Silverman's rule of thumb (normal approximation method)
# https://www.mathworks.com/matlabcentral/answers/232493-ksdensity-default-bandwidth-value
# https://en.wikipedia.org/wiki/Median_absolute_deviation#Relation_to_standard_deviation
def modified_silverman(x):
    n = len(x)
    median_x = np.median(x) # median
    mad = np.median(np.abs(x - median_x)) # median absolute deviation (MAD) - median of the absolute deviations from the data's median
    k = 1 / norm.ppf(3/4) # Conversion factor for normal distribution - scale factor k
    
    sigma = k * mad # standard deviation

    bw = sigma * (4/(3*n))**(1/5)
    
    return bw