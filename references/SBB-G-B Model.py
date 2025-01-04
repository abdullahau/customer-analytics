import numpy as np
from scipy.optimize import minimize
from utils import Donation

data = Donation()
rfm_summary_calib = data.p1x_data()
rfm_array_calib = rfm_summary_calib.collect().to_numpy()
p1x, t_x, _, num_donors = [*rfm_array_calib.T]

n = 6

Z = np.random.randn(100000, 2)

# Uncorrelated S_BB-G/B
# Method 1

def SbbGB_ll_uncorr(param):
    'evaluate the log-likelihood function for the uncorrelated S_BB-G/B model'
    # Part A
    Mu = param[:2]
    Sigma = np.diag(param[2:4])
    Y = Z @ np.sqrt(Sigma)
    
    logitp = Y[:, 0] + Mu[0]
    p = np.exp(logitp) / (1 + np.exp(logitp))
    logitt = Y[:, 1] + Mu[1]
    t = np.exp(logitt) / (1 + np.exp(logitt))

    # Part B
    ll = np.zeros(len(p1x))
    for i in range(len(p1x)):
        tmp_lik = p**p1x[i] * (1 - p)**(n - p1x[i]) * (1 - t)**n
        for j in range(n - t_x[i]):
            tmp_lik += p**p1x[i] * (1 - p)**(t_x[i] - p1x[i] + j) * t * (1 - t)**(t_x[i] + j)
        ll[i] = np.log(np.mean(tmp_lik))

    return -np.sum(ll * num_donors)

# Method 2

def SbbGB_ll_uncorr(param):
    """
    evaluate the log-likelihood function for the uncorrelated S_BB-G/B model
    
    Parameters:
    param: array-like
        [μ_p, μ_θ, σ²_p, σ²_θ] for the logit-normal distributions
    """    
    # Part A - Initial calculations
    Mu = param[:2]
    Sigma = np.diag(param[2:4])
    Y = Z @ np.sqrt(Sigma)
    
    # Compute p and t for all samples at once
    p = 1 / (1 + np.exp(-(Y[:, 0] + Mu[0])))    # More numerically stable
    t = 1 / (1 + np.exp(-(Y[:, 1] + Mu[1])))
    
    # Part B - Vectorized likelihood computation
    ll = np.empty(len(p1x))
    
    # Pre-compute log terms for p and (1-p)
    log_p = np.log(p)
    log_1mp = np.log1p(-p)  # More accurate than np.log(1-p)
    log_t = np.log(t)
    log_1mt = np.log1p(-t)
    
    for i in range(len(p1x)):
        # Base term (j = n - t_x[i])
        base_term = (p1x[i] * log_p + 
                    (n - p1x[i]) * log_1mp + 
                    n * log_1mt)
        base_lik = np.exp(base_term)
        
        # Compute all j terms at once
        j_range = np.arange(n - t_x[i])
        
        # Broadcast shapes for vectorized computation
        j_terms = (p1x[i] * log_p[:, None] +
                  (t_x[i] - p1x[i] + j_range) * log_1mp[:, None] +
                  log_t[:, None] +
                  (t_x[i] + j_range) * log_1mt[:, None])
        
        # Sum all likelihoods
        total_lik = base_lik + np.sum(np.exp(j_terms), axis=1)
        
        # Compute log mean
        ll[i] = np.log(np.mean(total_lik))
    
    return -np.sum(ll * num_donors)

# Method 3

def compute_likelihood_matrix(p, t, p1x_i, tx_i, n):
    """Compute likelihood matrix for a single donor group"""
    # First term calculation (when j = n - tx_i)
    base_lik = (p ** p1x_i) * ((1 - p) ** (n - p1x_i)) * ((1 - t) ** n)
    
    # Calculate terms for j = 0 to (n - tx_i - 1)
    remaining_terms = np.zeros_like(p)
    for j in range(n - tx_i):
        remaining_terms += (p ** p1x_i) * \
                         ((1 - p) ** (tx_i - p1x_i + j)) * \
                         t * ((1 - t) ** (tx_i + j))
    
    return base_lik + remaining_terms

def SbbGB_ll_uncorr_optimized(param):
    """
    Optimized version of the log-likelihood function for the uncorrelated S_BB-G/B model
    """
    # Part A - Vectorized calculations
    Mu = param[:2]
    Sigma = np.diag(param[2:4])
    Y = Z @ np.sqrt(Sigma)
    
    # Vectorized logistic transformations
    p = 1 / (1 + np.exp(-(Y[:, 0] + Mu[0])))  
    t = 1 / (1 + np.exp(-(Y[:, 1] + Mu[1])))
    
    # Part B - Vectorized operations with cached computations
    ll = np.zeros(len(p1x))
    
    # Process each donor group
    for i in range(len(p1x)):
        lik_matrix = compute_likelihood_matrix(p, t, p1x[i], t_x[i], n)
        ll[i] = np.log(np.mean(lik_matrix))
    
    return -np.sum(ll * num_donors)

# Method 4

# # computes the value of the sample log-likelihood function for a given set of model parameters
def SbbGB_ll_uncorr(param):
    'evaluate the log-likelihood function for the uncorrelated S_BB-G/B model'
    # Part A
    Mu = param[:2]
    Sigma = np.diag(param[2:4])
    Y = Z @ np.sqrt(Sigma)
    logit_p = Y[:, 0] + Mu[0]
    p = np.exp(logit_p) / (1 + np.exp(logit_p))
    logit_theta = Y[:, 1] + Mu[1]
    theta = np.exp(logit_theta) / (1 + np.exp(logit_theta))

    # Part B
    A1 = p[:,None]**p1x * (1-p[:,None])**(n-p1x) * (1-theta[:,None])**n
    i = np.arange(6).reshape(-1,1)
    A2 = p[:,None,None]**p1x * (1-p[:,None,None])**(t_x-p1x+i) * theta[:,None,None] * (1-theta[:,None,None])**(t_x + i)
    A2 = np.where(i <=  (n - t_x - 1), A2, 0)

    return -np.sum(np.log(np.mean(A1 + np.sum(A2, axis=1), axis=0)) * num_donors)

# Method 5

def sample_logitnormal(mu, sigma, size=1):
    """
    Generate samples from a logit-normal distribution
    
    Parameters:
    mu: float
        Location parameter on logit scale
    sigma: float
        Scale parameter on logit scale
    size: int
        Number of samples to generate
    
    Returns:
    array of samples from logit-normal distribution on (0,1) scale
    """
    # Sample from normal distribution
    np.random.seed(100)
    x = np.random.normal(mu, np.sqrt(sigma), size=size)
    # Transform to (0,1) scale
    return 1 / (1 + np.exp(-x))

def SbbGB_ll_direct_logitnormal(param):
    """
    Log-likelihood function using direct logit-normal sampling
    
    Parameters:
    param: array-like
        [μ_p, μ_θ, σ²_p, σ²_θ] for the logit-normal distributions
    """
    # Direct sampling from logit-normal distributions
    p = sample_logitnormal(param[0], param[2], size=100_000)
    t = sample_logitnormal(param[1], param[3], size=100_000)
    
    # Pre-compute log terms for efficiency
    log_p = np.log(p)
    log_1mp = np.log1p(-p)
    log_t = np.log(t)
    log_1mt = np.log1p(-t)
    
    ll = np.zeros(len(p1x))
    
    for i in range(len(p1x)):
        # Base term (j = n - t_x[i])
        base_term = (p1x[i] * log_p + 
                    (n - p1x[i]) * log_1mp + 
                    n * log_1mt)
        base_lik = np.exp(base_term)
        
        # Compute all j terms at once
        j_range = np.arange(n - t_x[i])
        
        # Broadcast shapes for vectorized computation
        j_terms = (p1x[i] * log_p[:, None] +
                  (t_x[i] - p1x[i] + j_range) * log_1mp[:, None] +
                  log_t[:, None] +
                  (t_x[i] + j_range) * log_1mt[:, None])
        
        total_lik = base_lik + np.sum(np.exp(j_terms), axis=1)
        ll[i] = np.log(np.mean(total_lik))
    
    return -np.sum(ll * num_donors)

# Correlated S_BB-G/B
# Method 1

def SbbGB_ll_corr(param):
    """
    evaluate the log-likelihood function for the correlated S_BB-G/B model
    
    Parameters:
    param: array-like
        [μ_p, μ_θ, σ²_p, σ²_θ, σ_pθ] for the logit-normal distributions
    """    
    # Part A 
    Mu = param[:2]
    R = np.array([param[2:4], [0, param[4]]])
    Y = Z @ R
    
    p = 1 / (1 + np.exp(-(Y[:, 0] + Mu[0])))   
    t = 1 / (1 + np.exp(-(Y[:, 1] + Mu[1])))
    
    # Part B
    ll = np.empty(len(p1x))
    for i in range(len(p1x)):
        tmp_lik = p**p1x[i] * (1 - p)**(n - p1x[i]) * (1 - t)**n
        for j in range(n - t_x[i]):
            tmp_lik += p**p1x[i] * (1 - p)**(t_x[i] - p1x[i] + j) * t * (1 - t)**(t_x[i] + j)
        ll[i] = np.log(np.mean(tmp_lik))
    
    return -np.sum(ll * num_donors)

# Method 2

def SbbGB_ll_corr(param):
    # Ensure param is a numpy array
    param = np.asarray(param)
    
    # Part A
    Mu = np.array([param[0], param[1]])
    R = np.array([param[2:4], [0, param[4]]])

    Y = Z @ R
    logitp = Y[:, 0] + Mu[0]
    p = np.exp(logitp) / (1 + np.exp(logitp))
    logitt = Y[:, 1] + Mu[1]
    t = np.exp(logitt) / (1 + np.exp(logitt))
    
    # Part B
    ll = np.empty(len(p1x))  # Initialize with known size
    
    for i in range(len(p1x)): 
        tmp_lik = p**p1x[i] * (1-p)**(n-p1x[i]) * (1-t)**n
        
        for j in range(n - t_x[i]):
            addition = p**p1x[i] * (1-p)**(t_x[i]-p1x[i]+j) * t * (1-t)**(t_x[i]+j)
            tmp_lik = tmp_lik + addition
            
        ll[i] = np.log(np.mean(tmp_lik))
    
    return -np.sum(ll * num_donors)

# Method 3

def SbbGB_ll_corr(param):
    # Part A 
    Mu = param[:2]
    R = np.array([param[2:4], [0, param[4]]])
    Y = Z @ R
    
    # Compute p and t directly
    p = 1 / (1 + np.exp(-(Y[:, 0] + Mu[0])))
    t = 1 / (1 + np.exp(-(Y[:, 1] + Mu[1])))
    
    # Pre-allocate array for efficiency
    ll = np.empty(len(p1x))
    
    # Part B with minimal operations
    for i in range(len(p1x)):
        tmp_lik = p**p1x[i] * (1 - p)**(n - p1x[i]) * (1 - t)**n
        
        for j in range(n - t_x[i]):
            tmp_lik += p**p1x[i] * (1 - p)**(t_x[i] - p1x[i] + j) * t * (1 - t)**(t_x[i] + j)
            
        ll[i] = np.log(np.mean(tmp_lik))
    
    return -np.sum(ll * num_donors)