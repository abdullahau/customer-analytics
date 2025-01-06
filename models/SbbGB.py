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


def compute_p_x_star_given_alive(n_star, x_star, p, theta):
    """
    Compute P(X(n, n+n*) = x* | p, θ, alive at n).

    Parameters:
    - n_star: Future time period.
    - x_star: Number of transactions in the future.
    - p: Purchase probability.
    - theta: Dropout probability.

    Returns:
    - Probability of x_star transactions in the future interval.
    """
    # First term: Binomial distribution for the case of staying alive throughout the interval
    first_term = comb(n_star, x_star) * (p**x_star) * ((1-p)**(n_star - x_star)) * ((1-theta)**n_star)
    
    # Second term: Summation for dropout during the interval
    second_term = 0
    for i in range(x_star, n_star):
        second_term += comb(i, x_star) * (p**x_star) * ((1-p)**(i - x_star)) * theta * ((1-theta)**i)
    
    return first_term + second_term

def compute_probability_x_star(n, n_star, x_star, p, theta, t_x, p1x):
    """
    Compute P(X(n, n+n*) = x* | p, θ, x, t_x, n).

    Parameters:
    - n: Current time period.
    - n_star: Future time period.
    - x_star: Number of transactions in the future.
    - p: Purchase probability.
    - theta: Dropout probability.
    - x: Historical transactions.
    - t_x: Time of last transaction.
    - p1x: Historical transaction counts.

    Returns:
    - Probability of x_star transactions in the future interval.
    """
    # Compute P(Alive at n | p, θ, x, t_x, n)
    P_alive = compute_p_alive(n, p, theta, t_x, p1x)
    
    # Compute P(X(n, n+n*) = x* | p, θ, alive at n)
    P_x_star_alive = compute_p_x_star_given_alive(n_star, x_star, p, theta)
    
    # Combine terms
    result = np.empty(len(p1x))
    for i in range(len(p1x)):
        delta = 1 if x_star == 0 else 0
        result[i] = delta * (1 - P_alive[i]) + np.mean(P_x_star_alive) * P_alive[i]
    return result

def compute_p_alive(n, p, theta, t_x, p1x):
    """
    Compute P(Alive at n | p, θ, x, t_x, n).

    Parameters:
    - n: Current time period.
    - p: Purchase probability.
    - theta: Dropout probability.
    - x: Historical transactions.
    - t_x: Time of last transaction.
    - p1x: Historical transaction counts.

    Returns:
    - Probability of being alive at n for each customer.
    """
    P_alive = np.empty(len(p1x))
    for i in range(len(p1x)):
        A1 = p**p1x[i] * (1-p)**(n-p1x[i]) * (1-theta)**n
        num = np.mean(A1)
        for j in range(n - t_x[i]):
            A1 += p**p1x[i] * (1-p)**(t_x[i]-p1x[i]+j) * theta * (1-theta)**(t_x[i]+j)
        P_alive[i] = num / np.mean(A1)
    return P_alive

compute_probability_x_star(n, 5, 1, p, t, t_x, p1x)