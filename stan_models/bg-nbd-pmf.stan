
functions {
    real bg_nbd_pmf(int x, real t, real r, real alpha, real a, real b) {
        real term1;
        real term2 = 0;
        real log_B_ab = lbeta(a, b);  // log(B(a, b))
        
        // Term 1: Survived entire period
        term1 = exp(
        lbeta(a, b + x) - log_B_ab
        + lgamma(r + x) - lgamma(r) - lgamma(x + 1)
        + r * log(alpha / (alpha + t)) 
        + x * log(t / (alpha + t))
        );
        
        // Term 2: Dropped out after x purchases (x > 0)
        if (x > 0) {
        real sum_part = 0;
        real log_alpha_t = log(alpha) - log(alpha + t);
        
        // Summation: ∑_{j=0}^{x-1} [Γ(r+j)/Γ(r)j! * (t/(α+t))^j]
        for (j in 0:(x-1)) {
            sum_part += exp(
            lgamma(r + j) - lgamma(r) - lgamma(j + 1)
            + j * (log(t) - log(alpha + t))
            );
        }
        
        // Compute term2 using log-space for stability
        term2 = exp(
            lbeta(a + 1, b + x - 1) - log_B_ab
            + log(1 - exp(r * log_alpha_t) * sum_part)
        );
        }
        
        return term1 + term2;
    }
}

data {
    int<lower=0> N;
    array[N] int<lower=0> X;
    vector<lower=0>[N] T;
    vector<lower=0>[N] t_x;
}

parameters {
    real<lower=0> r;                         // Gamma shape for lambda
    real<lower=0> alpha;                     // Gamma rate for lambda
    real<lower=0, upper=1> phi_dropout;      // Mixture weight for dropout process (Uniform prior)
    real<lower=1> kappa_dropout;             // Scale parameter for dropout (Pareto prior)
}

transformed parameters {
    real a = phi_dropout * kappa_dropout;       // Dropout shape parameter (controls early dropout likelihood)
    real b = (1 - phi_dropout) * kappa_dropout; // Dropout scale parameter (controls later dropout likelihood)
}

model {
    // Priors 
    r ~ weibull(2, 1);              // Regularized prior for purchase rate shape
    alpha ~ weibull(2, 10);         // Regularized prior for purchase rate scale
    phi_dropout ~ uniform(0,1);     // Mixture component for dropout process (Mean p)
    kappa_dropout ~ pareto(1,1);    // Scale of dropout process (Dropout Concentration)   

    for (n in 1:N) {
        int x = X[n];                 // Number of transactions for customer n
        real tx = t_x[n];              // Time of last transaction
        real t = T[n];                // Total observation time

        if (x == 0) {
            target += r * (log(alpha) - log(alpha + t));
        } else {
            real beta_term1 = lbeta(a, b + x) - lbeta(a, b);  // Beta function term
            real gamma_term = lgamma(r + x) - lgamma(r);       // Gamma function term
            real term1 = gamma_term + beta_term1 + r * log(alpha) - (r + x) * log(alpha + t);
            
            real beta_term2 = lbeta(a + 1, b + x - 1) - lbeta(a, b);
            real term2 = gamma_term + beta_term2 + r * log(alpha) - (r + x) * log(alpha + tx);
            
            target += log_sum_exp(term1, term2);
        }
    }
}

generated quantities {
    // Posterior predictive checks
    array[N] int<lower=0> X_rep;
    vector[N] t_x_rep;
    
    // Analytical PMF calculations: For validation, compute P(X(t)=x) for all observations
    vector[N] pmf_values;
    
    for (n in 1:N) {
        int x = X[n];
        real t = T[n];
        
        // Analytical PMF calculation using Equation (8)
        pmf_values[n] = bg_nbd_pmf(x, t, r, alpha, a, b);
        
        // Posterior predictive simulation
        real lambda = gamma_rng(r, alpha);
        real p = beta_rng(a, b);
        real current_time = 0;
        int x_rep = 0;
        real tx_rep = 0;
        int active = 1;
        
        while (active && current_time < t) {
            real wait = exponential_rng(lambda);
            if (current_time + wait > t) {
                break;
            } else {
                current_time += wait;
                x_rep += 1;
                tx_rep = current_time;
                if (bernoulli_rng(p)) {
                    active = 0;
                }
            }
        }
        X_rep[n] = x_rep;
        t_x_rep[n] = tx_rep;
    }
}
