
data {
    int<lower=0> N;               // Number of customers
    array[N] int<lower=0> X;      // Number of transactions per customer
    vector<lower=0>[N] T;         // Total observation time per customer
    vector<lower=0>[N] t_x;       // Time of last transaction (0 if X=0)
}

parameters {
    real<lower=0> r;                   // Gamma shape (r)
    real<lower=0> alpha;               // Gamma scale (alpha)
    real<lower=0, upper=5> a;          // Beta shape 1 (a)
    real<lower=0, upper=5> b;          // Beta shape 2 (b)
}

model {
    // Weakly informative priors
    r ~ weibull(2, 1);
    alpha ~ weibull(2, 10);
    a ~ uniform(0, 5);
    b ~ uniform(0, 5);

    for (n in 1:N) {
        int x = X[n];
        real tx = t_x[n];
        real t = T[n];

        // Term 1: B(a, b + x)/B(a, b) * Γ(r + x)/Γ(r) * (alpha/(alpha + t))^(r + x)
        real log_term1 = (
            lbeta(a, b + x) - lbeta(a, b) + 
            lgamma(r + x) - lgamma(r) + 
            r * log(alpha) - (r + x) * log(alpha + t)
        );

        // Term 2: B(a + 1, b + x - 1)/B(a, b) * Γ(r + x)/Γ(r) * (alpha/(alpha + tx))^(r + x)
        real log_term2 = negative_infinity();
        if (x > 0) {
            log_term2 = (
                lbeta(a + 1, b + x - 1) - lbeta(a, b) + 
                lgamma(r + x) - lgamma(r) + 
                r * log(alpha) - (r + x) * log(alpha + tx)
            );
        }

        target += log_sum_exp(log_term1, log_term2);
    }
}
