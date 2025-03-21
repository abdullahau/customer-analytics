
data {
    int<lower=0> N;               // Number of customers
    array[N] int<lower=0> X;      // Number of transactions per customer
    vector<lower=0>[N] T;         // Total observation time per customer
    vector<lower=0>[N] t_x;        // Time of last transaction (0 if X=0)
}

parameters {
    real<lower=0> r;                         // Shape parameter for the Gamma prior on purchase rate
    real<lower=0> alpha;                     // Scale parameter for purchase rate
    real<lower=0, upper=1> phi_dropout;      // Mixture weight for dropout process (Uniform prior)
    real<lower=1> kappa_dropout;             // Scale parameter for dropout (Pareto prior)
}

transformed parameters {
    real a = phi_dropout * kappa_dropout;       // Dropout shape parameter (controls early dropout likelihood)
    real b = (1 - phi_dropout) * kappa_dropout; // Dropout scale parameter (controls later dropout likelihood)
}

model {
    // Priors:
    r ~ weibull(2, 1);                // Prior on r (purchase rate shape parameter)
    alpha ~ weibull(2, 10);           // Prior on alpha (purchase rate scale parameter)
    phi_dropout ~ uniform(0,1);       // Mixture component for dropout process
    kappa_dropout ~ pareto(1,1);      // Scale of dropout process

    for (n in 1:N) {
        int x = X[n];                 // Number of transactions for customer n
        real tx = t_x[n];              // Time of last transaction
        real t = T[n];                // Total observation time

        if (x == 0) {
            // Likelihood for customers with zero transactions:
            // Probability of no purchases during (0, T): (alpha/(alpha + t))^r
            // Likelihood for X=0: (alpha/(alpha + t))^r
            target += r * (log(alpha) - log(alpha + t));
        } else {
            // Term 1: Probability of surviving until T and making x purchases
            // Term 1: B(a, b + x)/B(a, b) * Γ(r + x)/Γ(r) * (alpha/(alpha + t))^(r + x)
            real beta_term1 = lbeta(a, b + x) - lbeta(a, b);  // Beta function term
            real gamma_term = lgamma(r + x) - lgamma(r);       // Gamma function term
            real term1 = gamma_term + beta_term1 + r * log(alpha) - (r + x) * log(alpha + t);
            
            // Term 2: Probability of surviving until t_x, then dropping out
            // Term 2: B(a + 1, b + x - 1)/B(a, b) * Γ(r + x)/Γ(r) * (alpha/(alpha + tx))^(r + x)
            real beta_term2 = lbeta(a + 1, b + x - 1) - lbeta(a, b);
            real term2 = gamma_term + beta_term2 + r * log(alpha) - (r + x) * log(alpha + tx);
            
            // Log-sum-exp for numerical stability
            target += log_sum_exp(term1, term2);
        }
    }
}
