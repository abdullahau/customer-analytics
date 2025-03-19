
data {
    int<lower=0> N;               // Number of customers
    array[N] int<lower=0> X;      // Number of transactions per customer
    vector<lower=0>[N] T;         // Total observation time per customer
    vector<lower=0>[N] Tx;        // Time of last transaction (0 if X=0)
}

parameters {
    real<lower=0> r;                   // gamma shape (r)
    real<lower=0> alpha;               // gamma scale (alpha)
    real<lower=0, upper=5> a;          // beta shape 1 (a)
    real<lower=0, upper=5> b;          // beta shape 2 (b)
}

model {
    // Weakly informative priors on log parameters
    r ~ weibull(2, 1);
    alpha ~ weibull(2, 10);
    a ~ uniform(0, 5);
    b ~ uniform(0, 5);

    for (n in 1:N) {
        int x = X[n];
        real tx = Tx[n];
        real t = T[n];
    
        if (x == 0) {
              // Likelihood for X=0: (alpha/(alpha + t))^r
              target += r * (log(alpha) - log(alpha + t));
        } else {
              // Term 1: B(a, b + x)/B(a, b) * Γ(r + x)/Γ(r) * (alpha/(alpha + t))^(r + x)
              real beta_term1 = lbeta(a, b + x) - lbeta(a, b);
              real gamma_term = lgamma(r + x) - lgamma(r);
              real term1 = gamma_term + beta_term1 + r * log(alpha) - (r + x) * log(alpha + t);
            
              // Term 2: B(a + 1, b + x - 1)/B(a, b) * Γ(r + x)/Γ(r) * (alpha/(alpha + tx))^(r + x)
              real beta_term2 = lbeta(a + 1, b + x - 1) - lbeta(a, b);
              real term2 = gamma_term + beta_term2 + r * log(alpha) - (r + x) * log(alpha + tx);
            
              // Log-sum-exp for numerical stability
              target += log_sum_exp(term1, term2);
        }
    }
}
