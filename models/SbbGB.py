import numpy as np
from scipy.special import comb

def compute_L(p, t, x, t_x, n):
    """
    Compute L(p, θ | x, tx, n) 
    """
    lik = p**x * (1-p)**(n-x) * (1-t)**n
    for i in range(n - t_x):
        lik += p**x * (1-p)**(t_x-x+i) * t * (1-t)**(t_x+i)
    return np.mean(lik)

def compute_P_alive(p, t, x, t_x, n):
    """
    Compute P(alive at n | p, θ, x, tx, n)
    """
    numerator = p**x * (1-p)**(n-x) * (1-t)**n
    denominator = compute_L(p, t, x, t_x, n)
    return np.mean(numerator) / denominator


def compute_P_X_given_alive(p, t, n_star, x_star):
    """
    Compute P(X(n,n+n*)=x* | p, θ, alive at n)
    """
    first_term = comb(n_star, x_star) * p**x_star * (1-p)**(n_star-x_star) * (1-t)**n_star
    second_term = 0
    for i in range(x_star, n_star):
        second_term += comb(i, x_star) * p**x_star * (1-p)**(i-x_star) * t * (1-t)**i
    
    return np.mean(first_term + second_term)